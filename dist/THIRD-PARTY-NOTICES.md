# Third-party notices

Dragonborn's Codex is free software under the GNU General Public License, version 3 or (at your option) any
later version; the full text is `LICENSE.txt`. Copyright (C) 2026 lnocriesl, with later modifications by their
respective authors. The source code for this build is the source archive distributed with it; `commit.txt`
names the commit it was built from.

`DragonbornsCodex.dll` contains code from the projects below, under their own GPL-compatible licenses. Their
license texts are in `licenses/`.

## CommonLibSSE-NG v15.7.0

https://github.com/alandtse/CommonLibSSE-NG/tree/v15.7.0, statically linked from its official prebuilt bundle.

- GPL-3.0-or-later: `licenses/CommonLibSSE-NG-COPYING.txt`
- Its Modding Exception and GPL-3.0 Linking Exception: `licenses/CommonLibSSE-NG-EXCEPTIONS.md`
- The MIT license its original code was released under: `licenses/CommonLibSSE-NG-MIT.txt`

The prebuilt library is compiled with these, also under their own licenses:

| Library | License | Text |
|---|---|---|
| Hacker Disassembler Engine 64 (hde64) | BSD 2-Clause | `licenses/hde64.txt` |
| [rapidcsv](https://github.com/d99kris/rapidcsv) | BSD 3-Clause | `licenses/rapidcsv.txt` |
| [Xbyak](https://github.com/herumi/xbyak) | BSD 3-Clause | `licenses/xbyak.txt` |
| [nlohmann/json](https://github.com/nlohmann/json) | MIT | `licenses/nlohmann-json.txt` |
| [toml11](https://github.com/ToruNiina/toml11) | MIT | `licenses/toml11.txt` |
| [SimpleIni](https://github.com/brofield/simpleini) | MIT | `licenses/SimpleIni.txt` |
| [DirectXMath](https://github.com/microsoft/DirectXMath) | MIT | `licenses/DirectXMath.txt` |
| [DirectXTK](https://github.com/microsoft/DirectXTK) | MIT | `licenses/DirectXTK.txt` |
| [OpenVR](https://github.com/ValveSoftware/openvr) headers | BSD 3-Clause | `licenses/openvr.txt` |

Not every library is necessarily used by this plugin; their notices are included in case any of their code is.

## Compiled into the plugin

| Library | License | Text |
|---|---|---|
| [Dear ImGui](https://github.com/ocornut/imgui) 1.92.8 (core, DX11 backend, `imgui_stdlib`) | MIT | `licenses/imgui.txt` |
| [{fmt}](https://github.com/fmtlib/fmt) 12.2.0 | MIT | `licenses/fmt.txt` |
| [spdlog](https://github.com/gabime/spdlog) 1.17.0 | MIT | `licenses/spdlog.txt` |

## Data files

- Fonts in `fonts/`: Jost by indestructible type\* and Oswald by Vernon Adams and contributors, under the SIL
  Open Font License 1.1 (`fonts/OFL-Jost.txt`, `fonts/OFL-Oswald.txt`).
- No game files are included. The key glyphs in the menu's button hints are read at runtime from the player's own
  installed Skyrim interface files.

## Not included

SKSE and Address Library are separate installs. The Microsoft Visual C++ runtime is installed by the player.
