# Changelog

Changes in this fork of lnocriesl's Dragonborn's Codex. The newest are at the top.

## Unreleased

### Added

- Console page: a **Bat Files** card lists every `.txt` under `<game folder>/bat/` (subfolders included) as a
  button, grouped by subfolder. A click runs the file's lines as console commands in order, on the selected
  target if any, like the game's own `bat` command. Blank lines and lines starting with `;` or `//` are
  skipped. Without a `bat` folder the card explains how to set one up; it rescans on every open, and has a
  Refresh button.
- Bat Files: a **Preview only** switch (off by default). With it on, a click shows the file's contents in a
  scrolling, line-numbered view instead of running it; lines a run would skip are greyed out.
- `gamepadToggle=` in `DragonbornsCodex.ini` sets the gamepad combo that opens and closes the menu: one to
  three buttons joined with `+`, such as `L3+R3`, `X`, or `X+LB+LT`. It is unset by default, so no gamepad
  combo opens the menu until one is set; empty, `none` or `off` also leave it unset. Names: A, B, X, Y, LB/L1,
  RB/R1, LT/L2, RT/R2, L3/LS, R3/RS, Start/Menu, Back/Select/View, DPadUp, DPadDown, DPadLeft, DPadRight; case
  doesn't matter. The ini lists them, an invalid value leaves the combo unset with a warning in the log, and
  the menu's button hints show the combo in use.
- [SKSE Menu Framework](https://github.com/QTR-Modding/SKSE-Menu-Framework-3) support, when it is
  installed: a **Dragonborn's Codex** section with a General page that shows the menu's keyboard key and
  gamepad combo, and an **Open Dragonborn's Codex** button that closes the framework's menu and opens this one.
  The framework is optional; without it nothing changes.
- The ini explains `toggleKey` (a DirectInput scan code in decimal; 210 is Insert).
- The menu header shows **Current target: \<name\>**, or **Current target: none**, in place of the
  "Game connected" label, which was always shown.

### Fixed

- The ini's font comment named the old `Data/SKSE/Plugins/CheatMenu` folder; fonts are looked up in
  `Data/SKSE/Plugins/DragonbornsCodex`. The School settings message named `CheatMenu.log` instead of
  `DragonbornsCodex.log`.

- Gamepad: **A** now activates the focused control (switches, buttons, rows, sidebar pages, sliders). Before,
  A did nothing, despite the button hints.
- Gamepad: the D-pad and left stick move between the sidebar and the page. Right from the sidebar goes to the
  page's first control. Left at the page's left edge, or B, goes back to the sidebar. B in the sidebar closes
  the menu.
- Gamepad: B cancels an edit, closes a dropdown or leaves a scrolling list before it goes back or closes the
  menu. While the right stick moves the pointer, A clicks like the mouse.

### Changed

- Settings now live in `Data/SKSE/Plugins/DragonbornsCodex.ini`, next to the DLL (with Mod Organizer 2, in
  Overwrite), instead of `Documents/My Games/Skyrim Special Edition/SKSE/`. The log and character profiles
  (now `SKSE/DragonbornsCodexProfiles`) stay in the SKSE folder.
- The gamepad combo that opens the menu (L3+R3 in the original) is no longer set by default; see
  `gamepadToggle=` above.
- While a gamepad drives the menu, the controls that capture a keyboard key are greyed out: Menu Hotkey's
  Change, the hotkey list's Assign, the custom commands' Key button and the key chips on rows.
- The menu starts in the dark theme; Service > Appearance > Theme switches it.
- Menu text: "Highlights (ESP)" is now "Highlights", "ESP Look" is "Highlight Style", and "Reset ESP look"
  is "Reset highlight style".

### Removed

- The Skyrim dragon emblem image (rendered from the game's `logo.nif`) is no longer built into the plugin.
  The sidebar shows the drawn dragon icon instead, and the faint emblem on the Home page's player card is gone.
- The unused support for SkyUI item icons in the item and enchanting lists. It only drew icons from an atlas
  file that never shipped.
- The lookup for loose `icons/*.dds` menu icons (the original's exported map markers, no longer shipped). The
  menu's icons are all drawn in code.

## 1.0.0 (fork base)

The original release's source, rebuilt. Differences from the original distribution:

- No Bethesda files are shipped:
  - The 35 map-marker icons (`icons/`) are gone; the menu uses the line icons it already drew without them.
  - The 91 key glyphs (`keys/`) are read at runtime from the player's own game files.
- Builds on Linux (MSVC under Proton's Wine) instead of the Windows CMake/vcpkg setup; same SKSE plugin name
  ("CheatMenu") and author.
- Source comments translated from Russian to English; the Russian section of the player readme removed.
