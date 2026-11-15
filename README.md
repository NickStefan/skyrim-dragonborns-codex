# Dragonborn's Codex

An in-game cheat and tool menu for Skyrim SE/AE, as an SKSE plugin built on CommonLibSSE-NG
(alandtse v15.7.0, official prebuilt MSVC bundle) and Dear ImGui 1.92.8.

This is a fork of lnocriesl's Dragonborn's Codex 1.0.0, rebuilt from the source that shipped with the
release. The original built with CMake and vcpkg on Windows; this one builds on Linux.

## Layout

- `src/` the plugin's C++ source. `PluginInfo.cpp` holds the SKSE plugin declaration, which the original's
  CMake generated.
- `assets/DragonbornsCodex/` the menu's runtime data (languages, fonts), copied into
  `Data/SKSE/Plugins/DragonbornsCodex/`. No Bethesda files are shipped: key glyphs are read at runtime from the
  game's `Interface/exported/*.png.dds`, and the menu icons are drawn in code. Loose `icons/<name>.dds` files are
  still picked up if present (see `IconTexture` in `src/Menu.cpp`).
- `dist/` the player readme, third-party notices and license texts packaged with the DLL.
- `tools/` the build scripts.
- `VERSION` the plugin version, compiled into the DLL and the packaged readme.

## Build (Linux / SteamOS)

Builds use MSVC 14.51 (`cl.exe` 19.51.36260, matching the CommonLib bundle) under Proton 10's Wine.
Everything is fetched into this directory (`deps/`, `toolchain/`, `build/`); nothing is installed system-wide.

```sh
python3 tools/fetch_toolchain.py   # once; downloads ~2.5 GB and accepts the VS Build Tools license
python3 tools/build.py             # builds build/mod: DragonbornsCodex.dll, .pdb and the menu data
python3 tools/build.py clean
```

If another workspace already fetched the same toolchain (for example SkiingInSkyrim), skip the download and
symlink its MSVC/SDK and CommonLib bundle instead; the smaller sources (fmt, spdlog, ImGui, ...) are still cloned:

```sh
python3 tools/fetch_toolchain.py --reuse ../SkiingInSkyrim
```

`CODEX_PROTON` or `CODEX_WINE` select another Wine; `JOBS` limits parallel compiles.
The build uses its own Wine prefix in `build/wine`, with `S:` mapped to this directory.

The in-game test bridge the original author used (`CODEX_TEST_BRIDGE`, `src/TestBridge.cpp`) was not part of the
released source, so this build always uses the empty stubs in `src/TestBridge.h`.

## Install

Copy the contents of `build/mod` into the game's `Data` folder (or a mod manager folder), replacing the original
mod's files. Requires SKSE and Address Library for SKSE Plugins.
The log is written to `DragonbornsCodex.log` in the SKSE log directory of the game's Proton prefix
(`Documents/My Games/Skyrim Special Edition/SKSE`).

## License

GPL-3.0-or-later; see [LICENSE](LICENSE). What's compiled into the DLL and under which license is in
[dist/THIRD-PARTY-NOTICES.md](dist/THIRD-PARTY-NOTICES.md), with the license texts in `dist/licenses/`.

To release: commit, build, then `python3 tools/build.py source` for the source zip to ship next to the mod
(the GPL requires the matching source to be available).
