def cmake_config(env):
    config = {
        "CMAKE_POSITION_INDEPENDENT_CODE": "1",
        "CMAKE_DISABLE_FIND_PACKAGE_JPEG": "1",
        "CMAKE_BUILD_TYPE": "%s" % ("RelWithDebInfo" if env["debug_symbols"] else "Release"),
    }
    config["CMAKE_CROSSCOMPILING"] = "1"  # Force "cross compiling" so cmake does not override CMAKE_SYSTEM_PROCESSOR
    if env["platform"] == "linux" and env["arch"] == "x86_32":
        config["CMAKE_C_FLAGS"] = "-mmmx -msse4.2"
    return config


def build_library(env):
    lib_ext = ".lib" if env.msvc else ".a"
    yuv = env.CMakeBuild(
        env.Dir("#bin/thirdparty/libyuv"),
        env.Dir("thirdparty/libyuv"),
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
    env["YUV_INCLUDE"] = env.Dir("thirdparty/libyuv/include").abspath
    env.AddMethod(build_library, "BuildLibYUV")
