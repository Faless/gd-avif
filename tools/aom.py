def aom_cmake_config(env):
    bindir = env.Dir("bin/thirdparty/aom/{}/{}/install".format(env["platform"], env["arch"]))
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
        "CMAKE_INSTALL_PREFIX": bindir.abspath,
    }
    config["CMAKE_CROSSCOMPILING"] = "1"  # Force "cross compiling" so cmake does not override CMAKE_SYSTEM_PROCESSOR
    config["AOM_TARGET_CPU"] = {"x86_64": "x86_64", "x86_32": "x86", "arm64": "aarch64", "arm32": "arm"}[env["arch"]]
    return config


def build_library(env):
    lib_ext = ".lib" if env.msvc else ".a"
    aom = env.CMakeBuild(
        env.Dir("#bin/thirdparty/aom"),
        env.Dir("thirdparty/aom"),
        cmake_options=aom_cmake_config(env),
        cmake_outputs=["libaom" + lib_ext],
        install=True,
    )
    env.Append(CPPPATH=[env["AOM_INCLUDE"]])
    env.Prepend(LIBS=list(filter(lambda f: str(f).endswith(lib_ext), aom)))
    if env["platform"] == "linux" and env.get("threads", True):
        env.PrependUnique(LIBS=["pthread"])

    return aom


def exists(env):
    return "CMake" in env


def generate(env):
    env["AOM_INCLUDE"] = env.Dir("thirdparty/aom").abspath
    env["AOM_LIBS"] = ["libaom.a"]
    env.AddMethod(build_library, "BuildAOM")
