def avif_cmake_config(env):
    config = {
        "BUILD_SHARED_LIBS": "0",
        "AVIF_CODEC_AOM": "SYSTEM",
        "AVIF_CODEC_AOM_DECODE": "ON",
        "AVIF_CODEC_AOM_ENCODE": "ON",
        "AVIF_LIBYUV": "SYSTEM",
        "AOM_LIBRARY": env["AOM_INSTALL"] + "/libaom.a",
        "AOM_INCLUDE_DIR": env["AOM_INCLUDE"],
        "LIBYUV_LIBRARY": env["YUV_INSTALL"] + "/libyuv.a",
        "LIBYUV_INCLUDE_DIR": env["YUV_INCLUDE"],
        "CMAKE_POSITION_INDEPENDENT_CODE": "1",
        "CMAKE_BUILD_TYPE": "%s" % ("RelWithDebInfo" if env["debug_symbols"] else "Release"),
    }
    return config


def build_library(env, aom, yuv):
    lib_ext = ".lib" if env.msvc else ".a"
    avif = env.CMakeBuild(
        env["AVIF_BUILD"],
        env["AVIF_SOURCE"],
        cmake_options=avif_cmake_config(env),
        cmake_outputs=env["AVIF_LIBS"],
        dependencies=aom + yuv,
    )
    env.Append(CPPPATH=[env["AVIF_INCLUDE"]])
    env.Prepend(LIBS=list(filter(lambda f: str(f).endswith(lib_ext), avif)))
    return avif


def exists(env):
    return "CMakeConfigure" in env and "CMakeBuild" in env


def generate(env):
    env["AVIF_BUILD"] = env.Dir("#bin/thirdparty/libavif").abspath
    env["AVIF_SOURCE"] = env.Dir("thirdparty/libavif").abspath
    env["AVIF_INCLUDE"] = env.Dir("${AVIF_SOURCE}/include").abspath
    env["AVIF_LIBS"] = ["libavif.a"]
    env.AddMethod(build_library, "BuildLibAvif")
