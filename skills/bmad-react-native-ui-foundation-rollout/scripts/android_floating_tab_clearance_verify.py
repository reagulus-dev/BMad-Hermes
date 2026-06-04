#!/usr/bin/env python3
"""Capture and verify floating bottom-tab scroll clearance on Android.

Environment variables:
  ADB_BIN=/path/to/adb                         default: ~/Android/Sdk/platform-tools/adb
  ANDROID_UDID=<device serial>                 required if multiple devices are connected
  APP_PACKAGE=<android package>                required
  OUTPUT_DIR=<evidence output dir>             default: ./_bmad/artifacts/evidence/android-tab-clearance
  TAB_SPEC='today:105:Today,calendar:275:Calendar,...'
      screen_key:tap_x:expected_accessibility_label entries. Tap y defaults to 1335.
  TAB_TAP_Y=1335
  SWIPE_COUNT=20
  SCREEN_WIDTH_CENTER_X=360

Pass criterion:
  For each tab, selected tab label matches expectation and all non-tab text bottoms are above
  the top of the floating tab button bounds after repeated bottom-scroll swipes.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import time
from pathlib import Path

ADB = os.environ.get("ADB_BIN", str(Path.home() / "Android/Sdk/platform-tools/adb"))
UDID = os.environ.get("ANDROID_UDID", "")
PKG = os.environ["APP_PACKAGE"]
OUT = Path(os.environ.get("OUTPUT_DIR", "./_bmad/artifacts/evidence/android-tab-clearance")).resolve()
TAB_SPEC = os.environ.get("TAB_SPEC", "today:105:Today,calendar:275:Calendar,bookings:445:Bookings,more:615:More")
TAB_TAP_Y = int(os.environ.get("TAB_TAP_Y", "1335"))
SWIPE_COUNT = int(os.environ.get("SWIPE_COUNT", "20"))
SWIPE_X = int(os.environ.get("SCREEN_WIDTH_CENTER_X", "360"))

OUT.mkdir(parents=True, exist_ok=True)
DEVICE = f"-s {UDID}" if UDID else ""

def run(cmd: str, check: bool = True) -> str:
    result = subprocess.run(cmd, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if check and result.returncode != 0:
        raise RuntimeError(f"command failed {result.returncode}: {cmd}\n{result.stdout}")
    return result.stdout

def adb(cmd: str) -> str:
    return run(f"{ADB} {DEVICE} {cmd}")

def capture(name: str) -> None:
    run(f"{ADB} {DEVICE} exec-out screencap -p > {OUT / (name + '.png')}")
    adb("shell uiautomator dump /sdcard/floating-tab-window.xml >/dev/null")
    run(f"{ADB} {DEVICE} pull /sdcard/floating-tab-window.xml {OUT / (name + '.xml')} >/dev/null")

def parse_screen_spec():
    screens = []
    for entry in TAB_SPEC.split(","):
        key, x, label = entry.split(":", 2)
        screens.append((key, int(x), label))
    return screens

screens = parse_screen_spec()
adb(f"shell am force-stop {PKG}")
adb(f"shell monkey -p {PKG} -c android.intent.category.LAUNCHER 1 >/dev/null")
time.sleep(3)

for key, tap_x, _label in screens:
    adb(f"shell input tap {tap_x} {TAB_TAP_Y}")
    time.sleep(1)
    capture(f"{key}-top")
    for _ in range(SWIPE_COUNT):
        adb(f"shell input swipe {SWIPE_X} 1220 {SWIPE_X} 260 650")
        time.sleep(0.15)
    capture(f"{key}-bottom")

labels = [label for _key, _x, label in screens]
summary = {
    "device": adb("shell getprop ro.product.model").strip(),
    "android": adb("shell getprop ro.build.version.release").strip(),
    "package": PKG,
    "screens": {},
}
for key, _x, expected_label in screens:
    xml = (OUT / f"{key}-bottom.xml").read_text(encoding="utf-8")
    tab_bounds = {}
    for label in labels:
        match = re.search(r'content-desc="%s"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"' % re.escape(label), xml)
        if match:
            tab_bounds[label] = tuple(map(int, match.groups()))
    tab_top = min((b[1] for b in tab_bounds.values()), default=None)
    selected_match = re.search(r'content-desc="([^"]+)"[^>]*selected="true"', xml)
    selected = selected_match.group(1) if selected_match else None
    max_content_y2 = 0
    content_at_or_under = []
    for match in re.finditer(r'text="([^"]+)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml):
        text = match.group(1)
        x1, y1, x2, y2 = map(int, match.groups()[1:])
        if not text or text in labels:
            continue
        max_content_y2 = max(max_content_y2, y2)
        if tab_top is not None and y2 >= tab_top:
            content_at_or_under.append({"text": text[:90], "bounds": [x1, y1, x2, y2]})
    summary["screens"][key] = {
        "expected_tab": expected_label,
        "selected_tab": selected,
        "tab_bounds": tab_bounds,
        "tab_top": tab_top,
        "max_content_text_bottom": max_content_y2,
        "clearance_px": None if tab_top is None else tab_top - max_content_y2,
        "content_at_or_under_tab_top": content_at_or_under[:20],
        "pass": selected == expected_label and tab_top is not None and tab_top - max_content_y2 > 0 and not content_at_or_under,
    }
summary["content_clearance_pass"] = all(s["pass"] for s in summary["screens"].values())
(OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary, indent=2))
if not summary["content_clearance_pass"]:
    raise SystemExit(1)
