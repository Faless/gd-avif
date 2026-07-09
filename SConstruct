#!/usr/bin/env python
# ruff: noqa: F821

import os

# Minimum target platform versions.
if "ios_min_version" not in ARGUMENTS:
    ARGUMENTS["ios_min_version"] = "11.0"
if "macos_deployment_target" not in ARGUMENTS:
    ARGUMENTS["macos_deployment_target"] = "10.9"
if "android_api_level" not in ARGUMENTS:
    ARGUMENTS["android_api_level"] = "21"
if "api_version" not in ARGUMENTS:
    ARGUMENTS["api_version"] = "4.3"
if "use_static_cpp" not in ARGUMENTS:
    ARGUMENTS["use_static_cpp"] = "yes"

env = SConscript("godot-cpp/SConstruct").Clone()
env.__class__.msvc = env.get("is_msvc", False)


opts = Variables([], ARGUMENTS)

# Dependencies
for tool in ["cmake", "aom", "yuv", "avif"]:
    env.Tool(tool, toolpath=["tools"])

opts.Update(env)

result_path = os.path.join("bin", "gdavif")

# Our includes and sources
env.Append(CPPDEFINES=["GDEXTENSION"])  # Tells our sources we are building a GDExtension, not a module.
sources = [
    "register_types.cpp",
    "image_loader_avif.cpp",
    "resource_saver_avif.cpp",
]

deps = []
# For universal binaries, we first need to build the libraries separately,
# then join them together using lipo.
if env["platform"] == "macos" and env["arch"] == "universal":
    build_envs = {
        "x86_64": env.Clone(),
        "arm64": env.Clone(),
    }
    arch_aom = []
    arch_avif = []
    arch_yuv = []
    for arch in build_envs:
        benv = build_envs[arch]
        benv["arch"] = arch
        arch_aom.extend(benv.BuildAOM())
        arch_yuv.extend(benv.BuildLibYUV())
        arch_avif.extend(benv.BuildLibAvif(arch_aom, arch_yuv))

    # Join libraries using lipo.
    for targets in [arch_aom, arch_avif, arch_yuv]:
        libs = list(filter(lambda f: str(f).endswith(".a"), targets))
        path = "#bin/thirdparty/lipo"
        os.makedirs(env.Dir(path).abspath, exist_ok=True)
        lipo_action = "lipo $SOURCES -create -output $TARGET"
        lib = env.Command(
            env.File("{}/{}".format(path, os.path.basename(libs[0].abspath))),
            libs,
            lipo_action,
        )
        env.Depends(lib, libs)
        env.Append(LIBS=lib)
        deps.extend(lib)
    env.Append(CPPPATH=[env["AOM_INCLUDE"]])
    env.Append(CPPPATH=[env["YUV_INCLUDE"]])
    env.Append(CPPPATH=[env["AVIF_INCLUDE"]])
else:
    # Make our dependencies
    aom = env.BuildAOM()
    yuv = env.BuildLibYUV()
    avif = env.BuildLibAvif(aom, yuv)
    deps = aom + avif + yuv

env.Depends(sources, deps)

# We want to statically link against libstdc++ on Linux to maximize compatibility, but we must restrict the exported
# symbols using a GCC version script, or we might end up overriding symbols from other libraries.
# Using "-fvisibility=hidden" will not work, since libstdc++ explicitly exports its symbols.
symbols_file = None
if not env.get("use_llvm", False) and (
    env["platform"] == "linux" or (env["platform"] == "windows" and env.get("use_mingw", False))
):
    symbols_file = env.File("misc/gcc/symbols.map")
    env.Append(LINKFLAGS=["-Wl,--no-undefined,--version-script=" + symbols_file.abspath])
    env.Depends(sources, symbols_file)

# Make the shared library
result_name = "gdavif{}{}".format(env["suffix"], env["SHLIBSUFFIX"])
library = env.SharedLibrary(target=os.path.join(result_path, "lib", result_name), source=sources)

Default(library)

# GDNativeLibrary
extfile = env.InstallAs(os.path.join(result_path, "gdavif.gdextension"), "misc/gdavif.gdextension")
Default(extfile)
