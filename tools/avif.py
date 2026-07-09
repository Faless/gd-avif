def avif_cmake_config(env, aom, yuv):
    config = {
        "BUILD_SHARED_LIBS": "0",
        "AVIF_CODEC_AOM": "SYSTEM",
        "AVIF_CODEC_AOM_DECODE": "ON",
        "AVIF_CODEC_AOM_ENCODE": "ON",
        "AVIF_LIBYUV": "SYSTEM",
        "AOM_LIBRARY": aom[0].abspath,
        "AOM_INCLUDE_DIR": env["AOM_INCLUDE"],
        "LIBYUV_LIBRARY": yuv[0].abspath,
        "LIBYUV_INCLUDE_DIR": env["YUV_INCLUDE"],
        "CMAKE_POSITION_INDEPENDENT_CODE": "1",
        "CMAKE_BUILD_TYPE": "%s" % ("RelWithDebInfo" if env["debug_symbols"] else "Release"),
    }
    return config


def build_library(env, aom, yuv):
    lib_ext = ".lib" if env.msvc else ".a"
    avif = env.CMakeBuild(
        env.Dir("#bin/thirdparty/libavif"),
        env.Dir("thirdparty/libavif"),
        cmake_options=avif_cmake_config(env, aom, yuv),
        cmake_outputs=["libavif" + lib_ext],
        dependencies=aom + yuv,
    )
    env.Append(CPPPATH=[env["AVIF_INCLUDE"]])
    env.Prepend(LIBS=list(filter(lambda f: str(f).endswith(lib_ext), avif)))
    return avif


def exists(env):
    return "CMakeConfigure" in env and "CMakeBuild" in env


def generate(env):
    env["AVIF_INCLUDE"] = env.Dir("thirdparty/libavif/include").abspath
    env.AddMethod(build_library, "BuildLibAvif")
