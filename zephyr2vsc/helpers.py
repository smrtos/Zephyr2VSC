"""Define the helper functions for zephyr2vsc."""

import json
import os
import re
import subprocess
from typing import Set

from zephyr2vsc import const


def get_ninja_rules(build_dir: str) -> Set[str]:
    ninja_rules_file = os.path.join(build_dir, "CMakeFiles", "rules.ninja")

    with open(ninja_rules_file, "r") as f:
        print(f"Ninja rules file found:\n[{ninja_rules_file}]\n")

        rules = set()
        for line in f.readlines():
            if m := re.match(r"^rule\s([^\n]*)$", line):
                rules.add(m.group(1))

    print(f"Found [{len(rules)}] ninja build rules in:\n[{ninja_rules_file}]\n")
    return rules


def get_all_c_files_relative_path(src_dir: str) -> Set[str]:
    all_c_files = set()
    for dir, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".c"):
                # get the relative path to the src_dir
                c_file = os.path.join(dir, file)
                all_c_files.add(os.path.relpath(c_file, src_dir))

    print(f"Found [{len(all_c_files)}] C source files in source dir:\n[{src_dir}]\n")
    return all_c_files


def get_relevant_c_files_relative_path(src_dir: str, build_dir: str) -> Set[str]:
    ninja_build_file = os.path.join(build_dir, "build.ninja")

    with open(ninja_build_file, "r") as f:
        print(f"Ninja build file found:\n[{ninja_build_file}]\n")

        c_files = set()
        for line in f.readlines():
            if m := re.match(r"^build\s.*\s([^\s|]+\.c)\s", line):
                c_file = os.path.normpath(m.group(1).replace("$", ""))
                if not os.path.isabs(c_file):
                    # this must be a build generated file
                    c_files.add(os.path.normpath(os.path.join(build_dir, c_file)))
                else:
                    # get the relative path to the src_dir
                    c_files.add(os.path.relpath(c_file, src_dir))

    print(f"Found [{len(c_files)}] relevant C source files.\n")
    return c_files


def generate_compilation_db(build_dir: str, ninja_rules: Set[str]) -> str:
    # compDB will be saved in the build dir
    db_full_path = os.path.abspath(os.path.join(build_dir, "zephyr_compile_db.json"))
    print(f"Zephyr compilation DB will be saved as:\n[{db_full_path}]\n")

    rules = " ".join(ninja_rules)
    ninja_build_command = rf"ninja -C {build_dir} -t compdb {rules}"
    out = (
        subprocess.run(ninja_build_command, stdout=subprocess.PIPE, shell=True)
        .stdout.decode(encoding="utf-8")
        .splitlines()
    )

    # workaround for https://github.com/Microsoft/vscode-cpptools/issues/2417
    replace = {
        re.escape("--imacros="): "-include",
        re.escape("-imacros"): "-include",
    }
    pattern = re.compile("|".join(replace.keys()))
    fixed = map(lambda line: pattern.sub(lambda m: replace[re.escape(m.group(0))], line), out)

    with open(db_full_path, "w") as f:
        f.writelines(fixed)

    print(f"Zephyr compilation DB is saved as:\n[{db_full_path}]\n")
    return db_full_path


def generate_vscode_config_jsons(
    unused_c_files: Set[str],
    used_c_files: Set[str],
    compiler_path: str,
    db_full_path: str,
    src_dir: str,
):
    settings = const.SETTINGS_JSON_TEMPLATE
    settings["files.exclude"]["**/.github"] = True  # type: ignore
    settings["files.exclude"]["**/.known-issues"] = True  # type: ignore

    # I was expecting "**/.*" can be used as a shortcut to exclude all the . started files or
    # folders.
    # Ref: https://code.visualstudio.com/docs/editor/codebasics#_advanced-search-options
    #
    # But it turns out it will totally ruin the VS Code symbol parsing
    # According to https://github.com/microsoft/vscode-cpptools/issues/4063,
    # It seems "**/[.]*" can work around this issue.
    # settingsDecoded["files.exclude"]["**/[.]*"] = True

    for unused_c_file in unused_c_files:
        settings["files.exclude"][unused_c_file.replace("\\", "/")] = True  # type: ignore

    c_properties = const.C_CPP_PROPERTIES_JSON_TEMPLATE

    c_properties["configurations"][0]["compileCommands"] = db_full_path.replace(  # type: ignore
        "\\", "/"
    )
    c_properties["configurations"][0]["compilerPath"] = compiler_path.replace(  # type: ignore
        "\\", "/"
    )

    # Below line is related to to https://github.com/microsoft/vscode-cpptools/issues/4095
    # VS Code c_cpp_extension has fixed it. Please use c_cpp_extension > 0.25.1
    used_c_folders = {os.path.dirname(f) for f in used_c_files}
    c_properties["configurations"][0]["browse"]["path"].extend(  # type: ignore
        [f.replace("\\", "/") for f in used_c_folders]
    )

    vscode_dir = os.path.join(src_dir, ".vscode")
    if os.path.exists(vscode_dir):
        print(f".vscode folder already exists source dir:\n[{src_dir}]\n")
    else:  # pragma: no cover
        os.mkdir(vscode_dir)
        print(f".vscode folder generated for source dir:\n[{src_dir}]\n")

    settings_path = os.path.join(vscode_dir, "settings.json")
    c_properties_path = os.path.join(vscode_dir, "c_cpp_properties.json")

    with open(settings_path, "w") as f:
        json.dump(settings, f)

    with open(c_properties_path, "w") as f:
        json.dump(c_properties, f)

    print(
        f"VS Code configuration JSON files generated:\n[{settings_path}]\n[{c_properties_path}]\n"
    )
    return
