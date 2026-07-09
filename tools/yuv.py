import os


def cmake_config(env):
    config = {
        "CMAKE_POSITION_INDEPENDENT_CODE": "1",
        "CMAKE_BUILD_TYPE": "%s" % ("RelWithDebInfo" if env["debug_symbols"] else "Release"),
    }
    config["CMAKE_CROSSCOMPILING"] = "1"  # Force "cross compiling" so cmake does not override CMAKE_SYSTEM_PROCESSOR
    return config


def build_library(env):
    lib_ext = ".lib" if env.msvc else ".a"

    # Since YUV does not support macOS universal binaries, we first need to build the two libraries
    # separately, then we join them together using lipo.
    if env["platform"] == "macos" and env["arch"] == "universal":
        build_envs = {
            "x86_64": env.Clone(),
            "arm64": env.Clone(),
        }
        arch_yuv = []
        for arch in build_envs:
            benv = build_envs[arch]
            benv["arch"] = arch
            generate(benv)
            yuv = benv.CMakeBuild(
                benv["YUV_BUILD"],
                benv["YUV_SOURCE"],
                cmake_options=cmake_config(benv),
                cmake_outputs=["libyuv" + lib_ext],
                dependencies=[],
            )
            arch_yuv.extend(yuv)

        # Join libraries using lipo.
        os.makedirs(env.Dir("${YUV_BUILD}/${platform}/${arch}/").abspath, exist_ok=True)
        lipo_action = "lipo $SOURCES -create -output $TARGET"
        yuv = env.Command(
            env.File("${YUV_BUILD}/${platform}/${arch}/libyuv.a"),
            list(filter(lambda f: str(f).endswith(lib_ext), arch_yuv)),
            lipo_action,
        )
        env.Depends(yuv, arch_yuv)

    else:
        yuv = env.CMakeBuild(
            env["YUV_BUILD"],
            env["YUV_SOURCE"],
            cmake_options=cmake_config(env),
            cmake_outputs=["libyuv" + lib_ext],
            dependencies=[],
        )

    env.Append(CPPPATH=[env["YUV_INCLUDE"]])
    env.Prepend(LIBS=list(filter(lambda f: str(f).endswith(lib_ext), yuv)))
    return yuv


def exists(env):
    return "CMakeConfigure" in env and "CMakeBuild" in env


def generate(env):
    env["YUV_INSTALL"] = env.Dir("#bin/thirdparty/libyuv/{}/{}".format(env["platform"], env["arch"])).abspath
    env["YUV_BUILD"] = env.Dir("#bin/thirdparty/libyuv").abspath
    env["YUV_SOURCE"] = env.Dir("thirdparty/libyuv").abspath
    env["YUV_INCLUDE"] = env.Dir("${YUV_SOURCE}/include").abspath
    env.AddMethod(build_library, "BuildLibYUV")
