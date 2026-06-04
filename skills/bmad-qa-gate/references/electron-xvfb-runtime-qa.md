# Electron/Xvfb Runtime QA — Headless Linux Verification

## Problem

Electron apps need a real X display to render their GUI. Headless SSH servers (CI runners, remote VMs) have no display, so `electron` launches but blocks on GUI startup. Static checks (typecheck/test/build) pass but runtime UI behavior is unverified.

## Fix

Install Xvfb on Ubuntu:
```bash
sudo apt-get install -y xvfb
```

## Technique: Separate Runner Script

Electron's `app.whenReady()` does NOT work inline with Node `require`/`eval`. Write a standalone `.mjs` runner:

```js
// /tmp/helix-qa-runner.mjs
import { app, BrowserWindow } from 'electron';
import { writeFileSync } from 'fs';

app.whenReady().then(async () => {
  const win = new BrowserWindow({ width: 1280, height: 800, show: false });
  win.loadFile('/path/to/renderer/index.html');
  await new Promise((resolve) => win.webContents.on('did-finish-load', resolve));
  await new Promise(r => setTimeout(r, 800)); // let nav-init.js / CSS finish

  // Screenshot
  const img = await win.capturePage();
  writeFileSync('/tmp/qa-screenshot.png', img.toPNG());

  // DOM check
  const dom = await win.webContents.executeJavaScript(`
    (() => {
      const navItems = document.querySelectorAll('.nav-item');
      return {
        count: navItems.length,
        labels: Array.from(navItems).map(n => n.getAttribute('aria-label')),
        active: document.querySelector('.nav-item.active')?.getAttribute('data-dest-id')
      };
    })()
  `);
  console.log('DOM:', JSON.stringify(dom));

  // Computed styles (theme verification)
  const styles = await win.webContents.executeJavaScript(`
    (() => {
      const body = document.body;
      return {
        bg: getComputedStyle(body).backgroundColor,
        color: getComputedStyle(body).color,
        navBg: getComputedStyle(document.getElementById('nav-rail')).backgroundColor
      };
    })()
  `);
  console.log('Styles:', JSON.stringify(styles));

  win.close();
  app.quit();
}).catch(e => { console.error('Launch error:', e.message); app.quit(); process.exit(1); });
```

## Run

```bash
xvfb-run electron /tmp/helix-qa-runner.mjs --no-sandbox --disable-gpu 2>&1
```

Key flags:
- `--no-sandbox` — required on Ubuntu 23.10+ with AppArmor restrictions
- `--disable-gpu` — avoids GPU driver issues on headless servers

## What to Verify

1. **Screenshot** — saved PNG, visually inspect layout, colors, nav items
2. **DOM content** — verify nav destinations, active states, placeholder text
3. **Computed styles** — verify dark theme, accent colors, background colors match design tokens
4. **CSP** — check `meta[http-equiv="Content-Security-Policy"]` content
5. **No console errors** — check output for JS errors

## State File Updates

After passing QA, update:
- Story artifact: `qa_status: runtime_verified` + `qa_verified_at` timestamp
- Story QA Findings section: append verification details
- `_bmad/state.json`: update `workflow_status` and `state_check.notes`
- `CONTINUE-HERE.md`: append update section, remove stale "unverified" references
- `sprint-status.yaml`: update `review_notes` entry for the story

## Pitfalls

- **`browser_vision` uses Chrome, not Electron** — on Ubuntu 23.10+, Chrome needs `--no-sandbox`. If browser_vision fails with "No usable sandbox", try `xvfb-run` or add the flag.
- **Full path to Electron binary** — `xvfb-run electron` may not find Electron on PATH; use the full path: `xvfb-run /path/to/node_modules/.pnpm/electron@*/node_modules/electron/dist/electron`.
- **`replace_all` on CONTINUE-HERE.md** — if the target section appears multiple times, `patch(mode='replace', replace_all=True)` creates cascading duplicates. Remove ALL old copies after adding the new one.
- **Renderer timing** — Electron's `did-finish-load` fires before JS/CSS hydration in the renderer. Always add a short delay (500-1000ms) or wait for a specific DOM element before capturing screenshots.

## When This Applies

- Any Electron/Tauri/WebView desktop app on headless Linux
- CI pipelines that need visual verification before shipping
- Remote VMs with no X11 forwarding available
- Dark theme / CSS variable verification without a physical monitor
