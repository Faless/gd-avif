def cmake_config(env):
    config = {
        "CMAKE_POSITION_INDEPENDENT_CODE": "1",
        "CMAKE_BUILD_TYPE": "%s" % ("RelWithDebInfo" if env["debug_symbols"] else "Release"),
    }
    config["CMAKE_CROSSCOMPILING"] = "1"  # Force "cross compiling" so cmake does not override CMAKE_SYSTEM_PROCESSOR
    return config


def build_library(env):
    lib_ext = ".lib" if env.msvc else ".a"
    avif = env.CMakeBuild(
        env["YUV_BUILD"],
        env["YUV_SOURCE"],
        cmake_options=cmake_config(env),
        cmake_outputs=["libyuv" + lib_ext],
        dependencies=[],
    )
    env.Append(CPPPATH=[env["YUV_INCLUDE"]])
    env.Prepend(LIBS=list(filter(lambda f: str(f).endswith(lib_ext), avif)))
    return avif


def exists(env):
    return "CMakeConfigure" in env and "CMakeBuild" in env


def generate(env):
    env["YUV_INSTALL"] = env.Dir("#bin/thirdparty/libyuv/{}/{}".format(env["platform"], env["arch"])).abspath
    env["YUV_BUILD"] = env.Dir("#bin/thirdparty/libyuv").abspath
    env["YUV_SOURCE"] = env.Dir("thirdparty/libyuv").abspath
    env["YUV_INCLUDE"] = env.Dir("${YUV_SOURCE}/include").abspath
    env.AddMethod(build_library, "BuildLibYUV")
