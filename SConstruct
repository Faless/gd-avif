#!python

import os, sys, platform, json, subprocess

import builders


def add_sources(sources, dirpath, extension):
    for f in os.listdir(dirpath):
        if f.endswith("." + extension):
            sources.append(dirpath + "/" + f)


def replace_flags(flags, replaces):
    for k, v in replaces.items():
        if k in flags:
            flags[flags.index(k)] = v


env = Environment()
opts = Variables(["customs.py"], ARGUMENTS)
opts.Update(env)

ARGUMENTS["ios_min_version"] = "11.0"
ARGUMENTS["macos_deployment_target"] = "10.9"
env = SConscript("godot-cpp/SConstruct").Clone()

# Patch mingw SHLIBSUFFIX.
if env["platform"] == "windows" and env["use_mingw"]:
    env["SHLIBSUFFIX"] = ".dll"

opts.Update(env)

# Dependencies
deps_source_dir = "libs"
env.Append(
    BUILDERS={
        "BuildAOM": env.Builder(action=builders.aom_action, emitter=builders.aom_emitter),
        "BuildLibAvif": env.Builder(action=builders.avif_action, emitter=builders.avif_emitter),
    }
)

# AOM
aom = env.BuildAOM(env.Dir(builders.get_aom_build_dir(env)), env.Dir(builders.get_aom_source_dir(env)))

env.Prepend(CPPPATH=[builders.get_aom_include_dir(env)])
env.Prepend(LIBPATH=[builders.get_aom_build_dir(env)])
env.Append(LIBS=[aom])

# avif
avif = env.BuildLibAvif(env.Dir(builders.get_avif_build_dir(env)), [env.Dir(builders.get_avif_source_dir(env))] + aom)

env.Append(LIBPATH=[builders.get_avif_build_dir(env)])
env.Append(CPPPATH=[builders.get_avif_include_dir(env)])
env.Prepend(LIBS=[avif])

# Our includes and sources
env.Append(CPPPATH=["src/"])
sources = []
add_sources(sources, "src/", "cpp")
env.Depends(sources, [aom, avif])

# Make the shared library
result_path = os.path.join("bin", "gdavif")
result_name = "gdavif.{}.{}.{}{}".format(env["platform"], env["target"], env["arch_suffix"], env["SHLIBSUFFIX"])
library = env.SharedLibrary(target=os.path.join(result_path, "lib", result_name), source=sources)
Default(library)

# GDNativeLibrary
gdnlib = "gdavif"
extfile = env.Substfile(
    os.path.join(result_path, gdnlib + ".gdextension"),
    "misc/gdavif.gdextension",
    SUBST_DICT={
        "{GDNATIVE_PATH}": gdnlib,
        "{TARGET}": env["target"],
    },
)
Default(extfile)
