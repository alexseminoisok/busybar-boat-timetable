# BUSY Bar — Boat Timetable (North Greenwich Pier)

An on-device JavaScript app for the [BUSY Bar](https://busy.app) that shows live
**Uber Boat** (TfL river bus) departures from **North Greenwich Pier, London**,
styled like a UK countdown sign: coloured text on a dark grey background, two
boats at a time, paging through the upcoming ones. It runs **on the bar**
(JerryScript) and fetches TfL data **itself** over HTTPS — no companion app or
API key.

> **Made specifically for North Greenwich Pier.** It's the default; any other
> Uber Boat pier can be picked on the bar — see [Choosing a pier](#choosing-a-pier).

```
Battersea Power Station  9m
Barking Riverside       14m
```

- **Routes:** RB1 (west to Battersea Power Station, east to Barking Riverside)
  and RB6 (to Putney) — whatever TfL predicts for the pier, both directions.
  Boats terminating at North Greenwich are skipped.
- **Source:** TfL Unified API, `/StopPoint/930GMIL/Arrivals`, every 30 s. No
  API key needed.
- **Rows:** two columns — destination pier (" Pier" dropped; scrolls if it
  doesn't fit) and minutes (`due` under a minute), counting down live between
  refreshes. Route numbers (RB1, RB6) aren't shown.
- **Paging:** each pair stays up until both destinations have scrolled once
  (min 5 s), then a quick 0.4 s fade brings in the next pair (or a pixel
  dissolve — set `TRANSITION` in `main.js`).
- **Colours:** cyan by default; press **Start** for green, amber, pink, red.
  The bar remembers your pick.
- **Background:** a dim, slow "river surface" drifting behind the text, played
  natively by the bar (set `BG_ANIM = false` in `main.js` for plain grey).

Companion to [busybar-bus-timetable](https://github.com/alexseminoisok/busybar-bus-timetable)
(same display engine, North Greenwich bus station).

## Controls

| Input | Action |
|-------|--------|
| **Encoder** | Previous / next pair of boats |
| **Start** | Next text colour: cyan → green → amber → pink → red |
| **OK** | Refresh now |
| **Back** | Exit |

## Requirements

A BUSY Bar running firmware that includes the **on-device JS runner** — i.e. the
runtime that provides the global `listen("input", …)` and `fetch()` APIs and
lists JS apps in the **Apps** menu. (On official *release* firmware the JS SDK is
still "coming soon"; this app targets the dev/JS-runner firmware.) The bar needs
internet access (Wi-Fi) to reach TfL.

## Install

USB (default address `10.0.4.20`):

```bash
./install_boat_timetable.sh 10.0.4.20
```

Wi-Fi (set your HTTP-API password):

```bash
BAR_TOKEN=<http-access-password> ./install_boat_timetable.sh <bar-ip>
```

The script uploads the app to `/ext/user_assets/community.boat_timetable/` and
writes the `js_apps_enabled` flag. Then on the bar: **mode switch → Apps →
Boat Timetable → Start**. To update after changing files, run the installer
again and reopen the app.

## Choosing a pier

On the bar: **Apps → Boat Timetable → Setup → Pier**, then pick from all 24
Uber Boat piers (Putney → Barking Riverside, west to east). North Greenwich is
the default. Reopen the app to apply — settings are read at launch.

The list lives in `build_settings.py`, which generates both
`appmeta/settings.json` (the Setup picker, max 32 options) and the pier table
in `scripts/main.js`. Pier IDs are TfL `930G…` stop points
(`https://api.tfl.gov.uk/Line/rb1/StopPoints`).

## Layout

```
community.boat_timetable/
├── anims/     bg_water.anim (animated background)
├── appmeta/   manifest.json, settings.json (Setup → Pier), icons
└── scripts/   main.js
build_settings.py           # pier list -> settings.json + main.js table
build_bg_anim.py            # regenerates anims/bg_water.anim (AMP = strength)
build_icons.py              # regenerates the Apps-menu icons
install_boat_timetable.sh   # curl installer
```

## How it works

- **Data:** the Arrivals endpoint returns a JSON array of predictions (~1 KB
  each; a handful at a time for a pier). TfL caches the response for up to a
  minute, so countdowns use each boat's absolute `expectedArrival` against the
  bar's internet-synced clock (`/api/time`, re-read every 10 min) rather than
  the relative `timeToStation`. Boats are tracked by vehicle ID across
  refreshes. If the network drops, the last data keeps counting down; after
  3 minutes without an update the screen shows "No signal".
- **Font:** `small` (busy_regular_5) for everything; text widths are computed
  in JS from the font's advance table so columns line up.
- **Transitions:** an `xpmbitmap` overlay in the background colour sits on
  top; the fade ramps its `opacity` 0→100→0 while the next pair is swapped in
  underneath.
- **Background:** a looping `animation` element (`bg_water.anim`, 10 s at
  12 fps, "bicycle1" format via the firmware's `scripts/seq2anim.py`) under
  the text. The bar plays it itself, so it costs no draw requests — measured
  17 → 19 ms per draw with it running.
- **Draw:** `POST http://127.0.0.1/api/display/draw` (loopback skips auth),
  sending only changed elements; minutes tick every second.

## Attribution

Powered by TfL Open Data. Live river-bus arrival data is provided by
[Transport for London](https://tfl.gov.uk/info-for/open-data-users/) under the
[TfL transport data terms](https://tfl.gov.uk/corporate/terms-and-conditions/transport-data-service).
Uber Boat by Thames Clippers operates TfL's river-bus services. This project is
not affiliated with or endorsed by TfL, Thames Clippers or Uber.

## Credits

Built for the BUSY Bar.
