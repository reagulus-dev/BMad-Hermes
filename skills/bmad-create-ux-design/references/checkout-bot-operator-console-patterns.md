# Checkout-Bot / Operator-Console UX Patterns

Use when a BMad UX design task involves retail restock monitors, checkout workers, automation operator consoles, or the user asks to take inspiration from tools such as Stellar AIO.

## Public-source research pattern
- Inspect public marketing/docs/help pages for IA and setup flow patterns.
- Capture reusable UX structure, not private implementation details or brand imitation.
- Save project-local research notes when findings materially change the artifact.
- Record both `patterns_to_borrow` and `patterns_not_borrowed` so downstream agents do not overgeneralize.

## Common IA patterns
- Dashboard: active tasks, checkouts, failures/declines, spend/orders, unhealthy profiles/routes, recent activity.
- Tasks / task groups: site/vendor-specific groups; create/edit/duplicate/start/stop/delete/view logs actions.
- Targets/products: URL, PID/SKU, tags, quantity, item priority, price/cart rules, monitor strategy.
- Profiles & sessions: separate persistent browser/session state from checkout identity/payment references.
- Routes/proxies: grouped, testable, health-scored; distinguish monitor route and checkout route.
- Verification queue: CAPTCHA/3DS/OTP/user-assistance requests with live session focus and explicit outcome actions.
- Alerts/settings: Discord webhook configuration, test button, event-level toggles, delivery history.
- Logs/history: timestamped state changes, ATC/cart events, guardrail decisions, verification requests, provider delivery status.

## Checkout-worker rules
- Prefer unique profile ownership per worker; the UI should block two workers sharing one persistent profile.
- Multi-item cart attempts belong inside one worker-owned vendor/profile/cart context.
- Duplicating a worker config must require selecting a new profile before activation.
- Show cart ownership, worker status, current step, last event, and lock state prominently.

## Guardrail placement
- Do not defer first price validation until after 3DS/SCA or payment authorization.
- Preferred sequence: target setup → product read when reliable → add-to-cart response → cart review before shipping/payment progression → final pre-submit re-check.
- Cart review should show observed line price, configured max price, quantity, subtotal/total where available, min-cart/max-cart result, and pass/skip/abort state.
- If a retailer only shows 3DS/SCA after a payment attempt, label it as post-submit payment verification and ensure all cart-level guardrails passed before reaching it.

## Patterns to avoid copying blindly
- CAPTCHA bypass/auto-solver UX unless explicitly in scope and legally/product-safe; otherwise keep human-assisted verification.
- Very high task-count guidance as a default; keep bounded worker/cadence defaults and warnings.
- Profile rotation/concurrency that undermines session integrity or profile exclusivity.
