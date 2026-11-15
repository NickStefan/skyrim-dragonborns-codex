Dragonborn's Codex @VERSION@
========================
An in-game cheat and tool menu for Skyrim Special Edition / Anniversary Edition (SKSE plugin).
Press Insert to open or close it (can be changed in Service -> Controls), or L3+R3 on a gamepad
(gamepadToggle= in DragonbornsCodex.ini: up to three buttons joined with +, e.g. X+LB+LT; the ini lists the
button names; leave it empty to turn the gamepad toggle off).

This is a modified version of lnocriesl's Dragonborn's Codex 1.0.0, rebuilt from its released source
on Linux against the CommonLibSSE-NG v15.7.0 prebuilt bundle. Third-party code compiled into the DLL
is listed in THIRD-PARTY-NOTICES.md.

Requirements
- SKSE64 for your game version
- Address Library for SKSE Plugins
- Tested on Skyrim 1.6.1170. Other versions are not tested.

Install
Install the archive with Mod Organizer 2 or Vortex, or copy the SKSE folder into Data.

Uninstall
Turn off the toggles you used (speed, damage, weightless items...) and save, then remove the mod.
Values the game keeps in the save (for example a changed run speed) stay as they were when you removed it.

Files it writes
Data\SKSE\Plugins\DragonbornsCodex.ini   your menu settings, hotkeys, favourites (next to the DLL; created by
                                         the menu; with Mod Organizer 2 it lands in Overwrite)
Documents\My Games\Skyrim Special Edition\SKSE\DragonbornsCodex.log        log
Documents\My Games\Skyrim Special Edition\SKSE\DragonbornsCodexProfiles\   character profiles
Per-save state goes into the SKSE co-save next to your save.

Languages
English and Russian (Data\SKSE\Plugins\DragonbornsCodex\lang). Translations are plain .ini files: copy en.ini,
translate the values and pick the language in Service -> Appearance.

License and source code
Dragonborn's Codex - Copyright (C) 2026 lnocriesl

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General
Public License as published by the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
for more details. The full license text is in LICENSE.txt next to this file, and at
https://www.gnu.org/licenses/gpl-3.0.html

The complete source code of this build is the DragonbornsCodex-@VERSION@-source.zip distributed with it
(commit.txt next to this file names the commit it was built from).
The fonts keep their own SIL Open Font License.

Credits
- SKSE team; CommonLibSSE-NG (GPL-3.0); Dear ImGui by Omar Cornut (MIT)
- Fonts: Jost by indestructible type*, Oswald by Vernon Adams and contributors, both under the SIL Open Font
  License 1.1 (fonts\OFL-*.txt)
- Key glyphs are read from your own game's interface files; no Bethesda files are included
- The autoloot rules were modelled on SmartHarvest SE
