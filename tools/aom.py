import os


def aom_cmake_config(env):
    config = {
        "CMAKE_BUILD_TYPE": "%s" % ("RelWithDebInfo" if env["debug_symbols"] else "Release"),
        "BUILD_SHARED_LIBS:": "0",
        "ENABLE_DOCS": "0",
        "ENABLE_EXAMPLES": "0",
        "ENABLE_TESTDATA": "0",
        "ENABLE_TESTS": "0",
        "ENABLE_TOOLS": "0",
        "CMAKE_POSITION_INDEPENDENT_CODE": "1",
        "CMAKE_INSTALL_LIBDIR": "lib",
        "CMAKE_INSTALL_PREFIX": env.Dir(env["AOM_INSTALL"]).abspath,
    }
    config["AOM_TARGET_CPU"] = {"x86_64": "x86_64", "x86_32": "x86", "arm64": "aarch64", "arm32": "arm"}[env["arch"]]
    return config


def build_library(env):
    lib_ext = ".lib" if env.msvc else ".a"

    # Since AOM does not support macOS universal binaries, we first need to build the two libraries
    # separately, then we join them together using lipo.
    if env["platform"] == "macos" and env["arch"] == "universal":
        build_envs = {
            "x86_64": env.Clone(),
            "arm64": env.Clone(),
        }
        arch_aom = []
        for arch in build_envs:
            benv = build_envs[arch]
            benv["arch"] = arch
            generate(benv)
            aom = benv.CMakeBuild(
                env.Dir(benv["AOM_BUILD"]),
                env.Dir(benv["AOM_SOURCE"]),
                cmake_options=aom_cmake_config(benv),
                cmake_outputs=benv["AOM_LIBS"],
            )
            arch_aom.extend(aom)

        # Join libraries using lipo.
        os.makedirs(env["AOM_INSTALL"] + "/lib", exist_ok=True)
        lipo_action = "lipo $SOURCES -create -output $TARGET"
        aom = env.Command(
            env.File("${AOM_INSTALL}/lib/libaom.a"),
            list(filter(lambda f: str(f).endswith(lib_ext), arch_aom)),
            lipo_action,
        )
        env.Depends(aom, arch_aom)

    else:
        aom = env.CMakeBuild(
            env.Dir(env["AOM_BUILD"]),
            env.Dir(env["AOM_SOURCE"]),
            cmake_options=aom_cmake_config(env),
            cmake_outputs=env["AOM_LIBS"],
            install=True,
        )

    env.Append(CPPPATH=[env["AOM_INCLUDE"]])
    env.Prepend(LIBS=list(filter(lambda f: str(f).endswith(lib_ext), aom)))
    if env["platform"] == "linux":
        env.PrependUnique(LIBS=["pthread"])

    return aom


def exists(env):
    return "CMake" in env


def generate(env):
    env["AOM_INSTALL"] = env.Dir("#bin/thirdparty/aom/${platform}/${arch}/install").abspath
    env["AOM_BUILD"] = env.Dir("#bin/thirdparty/aom/${platform}/${arch}").abspath
    env["AOM_SOURCE"] = env.Dir("thirdparty/aom").abspath
    env["AOM_INCLUDE"] = env["AOM_SOURCE"]
    env["AOM_LIBS"] = ["libaom.a"]
    env.AddMethod(build_library, "BuildAOM")
