#!/usr/bin/env python3
"""Build DragonbornsCodex.dll with MSVC under Wine and assemble build/mod.

    python3 tools/build.py          build the plugin and assemble build/mod (DLL, PDB, menu data, docs, licenses)
    python3 tools/build.py source   zip the committed source of HEAD into build/, for uploading with a release
    python3 tools/build.py clean    remove build outputs (keeps the Wine prefix and caches)

Run tools/fetch_toolchain.py once first. Nothing is copied into the game.
"""
import concurrent.futures
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fetch_toolchain as pins  # noqa: E402
import wine_env  # noqa: E402

ROOT = wine_env.ROOT
BUILD = ROOT / 'build'
OBJ = BUILD / 'obj'
SRC = ROOT / 'src'
DEPS = ROOT / 'deps'
MSVC = ROOT / 'toolchain/msvc/VC/Tools/MSVC' / pins.MSVC_VERSION
KITS = ROOT / 'toolchain/msvc/Windows Kits/10'
COMMONLIB = DEPS / 'commonlib-prebuilt'
THIRD_PARTY = DEPS / 'src'
IMGUI = THIRD_PARTY / 'imgui'
ASSETS = ROOT / 'assets/DragonbornsCodex'
DIST = ROOT / 'dist'
NAME = 'DragonbornsCodex'
DOCS = ['README.txt', 'THIRD-PARTY-NOTICES.md']
JOBS = int(os.environ.get('JOBS', 4))

DEFINES = [
    'WINVER=0x0601', '_WIN32_WINNT=0x0601', 'NOMINMAX', 'WIN32_LEAN_AND_MEAN',
    # The prebuilt CommonLib is compiled for all runtimes; this layout must match it.
    'ENABLE_SKYRIM_SE=1', 'ENABLE_SKYRIM_AE=1', 'ENABLE_SKYRIM_VR=1', 'HAS_SKYRIM_MULTI_TARGETING=1',
    'SPDLOG_COMPILED_LIB', 'SPDLOG_FMT_EXTERNAL',
]
# Same suppressions CommonLib's prebuilt target exports to consumers.
DISABLED_WARNINGS = [4005, 4061, 4068, 4200, 4201, 4265, 4266, 4371, 4514, 4582, 4583, 4623, 4625,
                     4626, 4702, 4710, 4711, 4820, 4996, 5026, 5027, 5045, 5053, 5204, 5220]
SYSTEM_LIBS = ['advapi32.lib', 'bcrypt.lib', 'd3d11.lib', 'd3dcompiler.lib', 'dbghelp.lib', 'dxgi.lib',
               'ole32.lib', 'version.lib', 'user32.lib', 'shell32.lib']
IMGUI_SOURCES = ['imgui.cpp', 'imgui_demo.cpp', 'imgui_draw.cpp', 'imgui_tables.cpp', 'imgui_widgets.cpp',
                 'backends/imgui_impl_dx11.cpp', 'misc/cpp/imgui_stdlib.cpp']


def sdk_version():
    versions = sorted(p.name for p in (KITS / 'Include').glob(pins.SDK_VERSION + '.*'))
    if not versions:
        raise SystemExit('Windows SDK missing; run tools/fetch_toolchain.py')
    return versions[-1]


def tool_env():
    sdk = sdk_version()
    include = [MSVC / 'include', *(KITS / 'Include' / sdk / n for n in ('ucrt', 'shared', 'um', 'winrt'))]
    lib = [MSVC / 'lib/x64', *(KITS / 'Lib' / sdk / n / 'x64' for n in ('ucrt', 'um'))]
    return {'INCLUDE': ';'.join(map(wine_env.win, include)), 'LIB': ';'.join(map(wine_env.win, lib))}


def msvc(tool, args):
    result = wine_env.run(MSVC / 'bin/Hostx64/x64' / (tool + '.exe'), args, extra_env=tool_env())
    if result.returncode != 0:
        raise SystemExit(f'{tool} failed ({result.returncode})')


def version():
    text = (ROOT / 'VERSION').read_text().strip()
    major, minor, patch = (int(part) for part in text.split('.'))
    return text, major, minor, patch


def base_flags(warnings='/W3'):
    text, major, minor, patch = version()
    flags = ['/nologo', '/std:c++latest', '/EHsc', '/permissive-', '/Zc:preprocessor', '/utf-8', '/MD',
             '/O2', '/Z7', '/bigobj', warnings, '/external:anglebrackets', '/external:W0', '/DNDEBUG']
    flags += ['/D' + d for d in DEFINES]
    flags += [f'/DCODEX_VERSION_MAJOR={major}', f'/DCODEX_VERSION_MINOR={minor}',
              f'/DCODEX_VERSION_PATCH={patch}', f'/DCODEX_VERSION_STRING="{text}"']
    flags += [f'/wd{w}' for w in DISABLED_WARNINGS]
    includes = [SRC, COMMONLIB / 'include', COMMONLIB / 'extern/openvr/headers',
                THIRD_PARTY / 'spdlog/include', THIRD_PARTY / 'fmt/include',
                THIRD_PARTY / 'DirectXTK/Inc', THIRD_PARTY / 'DirectXMath/Inc',
                THIRD_PARTY / 'SKSEMenuFramework/resources',
                IMGUI, IMGUI / 'backends', IMGUI / 'misc/cpp']
    return flags + ['/I' + wine_env.win(p) for p in includes]


def stale(output, inputs):
    if not output.exists():
        return True
    built = output.stat().st_mtime
    return any(p.stat().st_mtime > built for p in inputs)


def compile_all(jobs, warnings='/W3'):
    """jobs: (source, object, extra flags, dependencies)."""
    todo = [j for j in jobs if stale(j[1], [j[0], *j[3]])]

    def one(job):
        source, obj, extra, _ = job
        obj.parent.mkdir(parents=True, exist_ok=True)
        msvc('cl', base_flags(warnings) + extra + ['/c', '/Fo' + wine_env.win(obj), wine_env.win(source)])

    with concurrent.futures.ThreadPoolExecutor(JOBS) as pool:
        list(pool.map(one, todo))


def build_dependencies():
    """spdlog (compiled, external fmt) and fmt, as CommonLib's vcpkg baseline builds them, plus Dear ImGui."""
    library = OBJ / 'deps/codex_deps.lib'
    sources = [THIRD_PARTY / 'fmt/src/format.cc',
               *(THIRD_PARTY / 'spdlog/src' / f for f in
                 ('spdlog.cpp', 'stdout_sinks.cpp', 'color_sinks.cpp', 'file_sinks.cpp', 'async.cpp', 'cfg.cpp'))]
    objects = [OBJ / 'deps' / (s.parent.parent.name + '_' + s.stem + '.obj') for s in sources]
    imgui = [IMGUI / s for s in IMGUI_SOURCES]
    sources += imgui
    objects += [OBJ / 'deps' / ('imgui_' + s.stem + '.obj') for s in imgui]
    compile_all([(s, o, [], []) for s, o in zip(sources, objects)], warnings='/W0')
    if stale(library, objects):
        msvc('lib', ['/nologo', '/OUT:' + wine_env.win(library), *map(wine_env.win, objects)])
    return library


def build_plugin(dependencies):
    headers = list(SRC.rglob('*.h'))
    pch_header, pch_source = SRC / 'PCH.h', SRC / 'PCH.cpp'
    pch, pch_obj = OBJ / 'plugin/PCH.pch', OBJ / 'plugin/PCH.obj'
    # VERSION goes in as compiler flags, so a new version rebuilds the PCH and with it everything.
    if stale(pch, [pch_header, pch_source, ROOT / 'VERSION']):
        pch_obj.parent.mkdir(parents=True, exist_ok=True)
        msvc('cl', base_flags() + ['/c', '/YcPCH.h', '/Fp' + wine_env.win(pch),
                                   '/Fo' + wine_env.win(pch_obj), wine_env.win(pch_source)])
    sources = sorted(p for p in SRC.rglob('*.cpp') if p != pch_source)
    objects = [OBJ / 'plugin' / (s.relative_to(SRC).with_suffix('.obj').as_posix().replace('/', '_')) for s in sources]
    use_pch = ['/YuPCH.h', '/FIPCH.h', '/Fp' + wine_env.win(pch)]
    compile_all([(s, o, use_pch, [*headers, pch]) for s, o in zip(sources, objects)])

    dll, pdb = BUILD / (NAME + '.dll'), BUILD / (NAME + '.pdb')
    inputs = [pch_obj, *objects, dependencies, COMMONLIB / 'lib/CommonLibSSE.lib']
    if stale(dll, inputs):
        msvc('link', ['/NOLOGO', '/DLL', '/MACHINE:X64', '/DEBUG:FULL', '/OPT:REF', '/OPT:ICF',
                      '/PDBALTPATH:' + NAME + '.pdb', '/OUT:' + wine_env.win(dll), '/PDB:' + wine_env.win(pdb),
                      *map(wine_env.win, inputs), wine_env.win(COMMONLIB / 'lib/openvr_api.lib'), *SYSTEM_LIBS])
    return dll, pdb


def pe_tables(dll):
    """(export names, imported DLL names) of a PE32+ image."""
    data = dll.read_bytes()
    pe = struct.unpack_from('<I', data, 0x3C)[0]
    sections = struct.unpack_from('<H', data, pe + 6)[0]
    optional_size = struct.unpack_from('<H', data, pe + 20)[0]
    optional = pe + 24
    export_rva, import_rva = (struct.unpack_from('<I', data, optional + 112 + 8 * i)[0] for i in range(2))
    table = [struct.unpack_from('<8sIIII', data, optional + optional_size + 40 * i) for i in range(sections)]

    def offset(rva):
        for _, size, address, raw_size, raw in table:
            if address <= rva < address + max(size, raw_size):
                return raw + rva - address
        raise ValueError(f'RVA {rva:#x} outside sections')

    def string(rva):
        start = offset(rva)
        return data[start:data.index(b'\0', start)].decode()

    exported = set()
    if export_rva:
        base = offset(export_rva)
        count, names = struct.unpack_from('<II', data, base + 24)[0], struct.unpack_from('<I', data, base + 32)[0]
        exported = {string(struct.unpack_from('<I', data, offset(names) + 4 * i)[0]) for i in range(count)}
    imported = []
    descriptor = offset(import_rva) if import_rva else None
    while descriptor is not None:
        name_rva = struct.unpack_from('<I', data, descriptor + 12)[0]
        if name_rva == 0:
            break
        imported.append(string(name_rva))
        descriptor += 20
    return exported, imported


def git(*args):
    result = subprocess.run(['git', '-C', str(ROOT), *args], capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None


def package_docs(folder):
    """Menu data, docs, our license and the third-party license texts, into SKSE/Plugins/DragonbornsCodex."""
    text = version()[0]
    shutil.copytree(ASSETS, folder)
    for doc in DOCS:
        (folder / doc).write_text((DIST / doc).read_text().replace('@VERSION@', text))
    shutil.copy2(ROOT / 'LICENSE', folder / 'LICENSE.txt')
    shutil.copy2(ROOT / 'CHANGELOG.md', folder / 'CHANGELOG.md')
    shutil.copytree(DIST / 'licenses', folder / 'licenses')

    named = set(re.findall(r'licenses/([\w.-]+)', (DIST / 'THIRD-PARTY-NOTICES.md').read_text()))
    present = {p.name for p in (DIST / 'licenses').iterdir()}
    if named != present:
        raise SystemExit(f'THIRD-PARTY-NOTICES.md and dist/licenses disagree: missing {sorted(named - present)}, '
                         f'not mentioned {sorted(present - named)}')

    commit = git('rev-parse', 'HEAD')
    if commit is None:
        print('warning: not a git checkout (or no commits yet); no commit.txt in the package')
        return
    lines = [f'Built from commit {commit}']
    if git('status', '--porcelain'):
        lines.append('Built with uncommitted changes, so this build does not exactly match that commit.')
        print('warning: uncommitted changes; commit.txt says the build does not match its commit')
    (folder / 'commit.txt').write_text('\n'.join(lines) + '\n')


def package_source():
    """git archive of HEAD: the Corresponding Source for a build made from a clean tree at that commit."""
    if git('rev-parse', 'HEAD') is None:
        raise SystemExit('Not a git checkout with commits yet')
    if git('status', '--porcelain'):
        raise SystemExit('Uncommitted changes: commit first, so the source zip matches the build')
    text = version()[0]
    archive = BUILD / f'{NAME}-{text}-source.zip'
    BUILD.mkdir(exist_ok=True)
    git('archive', '--format=zip', f'--prefix={NAME}-{text}-source/', '-o', str(archive), 'HEAD')
    print(f'Wrote {archive.relative_to(ROOT)} ({git("rev-parse", "--short", "HEAD")})')


def package(dll, pdb):
    exported, imported = pe_tables(dll)
    missing = {'SKSEPlugin_Load', 'SKSEPlugin_Version'} - exported
    if missing:
        raise SystemExit(f'{dll.name} is missing SKSE exports: {sorted(missing)}')
    # Only Skyrim VR ships these; a hard import would stop the plugin loading on SE/AE.
    runtime_only = {'openvr_api.dll', 'steam_api64.dll'} & {name.lower() for name in imported}
    if runtime_only:
        raise SystemExit(f'{dll.name} hard-imports {sorted(runtime_only)}')
    plugins = BUILD / 'mod/SKSE/Plugins'
    shutil.rmtree(BUILD / 'mod', ignore_errors=True)
    plugins.mkdir(parents=True)
    shutil.copy2(dll, plugins)
    shutil.copy2(pdb, plugins)
    package_docs(plugins / NAME)
    print(f'{dll.name}: exports {", ".join(sorted(exported))}')
    print(f'{dll.name}: imports {", ".join(imported)}')
    print(f'Packaged {plugins.relative_to(ROOT)}')


def main():
    if sys.argv[1:] == ['source']:
        package_source()
        return
    if sys.argv[1:] == ['clean']:
        for path in (OBJ, BUILD / 'mod', BUILD / (NAME + '.dll'), BUILD / (NAME + '.pdb')):
            shutil.rmtree(path, ignore_errors=True) if path.is_dir() else path.unlink(missing_ok=True)
        return
    if sys.argv[1:]:
        raise SystemExit(__doc__)
    if not (MSVC / 'bin/Hostx64/x64/cl.exe').exists() or not (COMMONLIB / 'lib/CommonLibSSE.lib').exists():
        raise SystemExit('Toolchain missing; run tools/fetch_toolchain.py')
    if not (IMGUI / 'imgui.cpp').exists():
        raise SystemExit('Dear ImGui missing; run tools/fetch_toolchain.py')
    wine_env.ensure_prefix()
    package(*build_plugin(build_dependencies()))


if __name__ == '__main__':
    main()
