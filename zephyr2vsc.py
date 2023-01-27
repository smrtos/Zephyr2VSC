# coding=UTF-8

"""A tool to import Zephyr code into Visual Studio Code in the context of a Zephyr application.

Copyright (c) 2019-2023 Ming Shao
"""

import sys
import os
import re
import json
import subprocess
from typing import Set

SETTINGS_JSON_TEMPLATE = {
    "files.exclude": {
        "**/.git": True,
        "**/.svn": True,
        "**/.hg": True,
        "**/CVS": True,
        "**/.DS_Store": True,
        "**/test*":True
    },
    "C_Cpp.exclusionPolicy": "checkFilesAndFolders",
	"C_Cpp.intelliSenseEngine": "Default",
	"cmake.configureOnOpen": False
}

C_CPP_PROPERTIES_JSON_TEMPLATE = {
    "configurations": [
        {
            "name": "Zephyr",
            "compilerPath": "",
            "cStandard": "c99",
            "cppStandard": "c++11",
            "intelliSenseMode": "gcc-x64",
            "compileCommands": "",
            "browse": 
            {
                "limitSymbolsToIncludedHeaders": True,
                "databaseFilename": "${workspaceFolder}/.vscode/browse.zephyr.db",
                "path": []
            }
        }
    ],
    "version": 4
}

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
                    c_files.add(os.path.relpath(c_files, src_dir))

    print(f"Found [{len(c_files)}] relevant C source files.\n")
    return c_files

def generate_compilation_db(build_dir: str, ninja_rules: Set[str]) -> str:
    # compDB will be saved in the build dir
    db_full_path = os.path.abspath(os.path.join(build_dir, "zephyr_compile_db.json"))
    print(f"Zephyr compilation DB will be saved as:\n[{db_full_path}]\n")
    
    rules = " ".join(ninja_rules)
    ninja_build_command = rf"ninja -C {build_dir} -t compdb {rules}"
    out = subprocess.run(ninja_build_command, stdout=subprocess.PIPE, shell=True).stdout.decode()

    # workaround for https://github.com/Microsoft/vscode-cpptools/issues/2417
    replace = {
        re.escape("--imacros="): "-include",
        re.escape("-imacros"): "-include",
    }
    pattern = re.compile("|".join(replace.keys()))
    fixed = map(lambda l: pattern.sub(lambda m: replace[re.escape(m.group(0))], l), out)
    
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
    settings = SETTINGS_JSON_TEMPLATE
    settings["files.exclude"]["**/.github"] = True
    settings["files.exclude"]["**/.known-issues"] = True

    # I was expecting "**/.*" can be used as a shortcut to exclude all the . started files or folders.
    # Ref: https://code.visualstudio.com/docs/editor/codebasics#_advanced-search-options
    #
    # But it turns out it will totally ruin the VS Code symbol parsing
    # According to https://github.com/microsoft/vscode-cpptools/issues/4063,
    # It seems "**/[.]*" can work around this issue.
    #settingsDecoded["files.exclude"]["**/[.]*"] = True

    for unused_c_file in unused_c_files:
        settings["files.exclude"][unused_c_file.replace("\\","/")] = True
    
    c_properties = C_CPP_PROPERTIES_JSON_TEMPLATE

    c_properties["configurations"][0]["compileCommands"] = db_full_path.replace("\\", "/")
    c_properties["configurations"][0]["compilerPath"] = compiler_path.replace("\\", "/")
    
    # Below line is related to to https://github.com/microsoft/vscode-cpptools/issues/4095
    # VS Code c_cpp_extension has fixed it. Please use c_cpp_extension > 0.25.1
    c_properties["configurations"][0]["browse"]["path"].extend([f.replace("\\","/") for f in used_c_files])

    vscode_dir = os.path.join(src_dir, ".vscode")
    if(os.path.exists(vscode_dir)):
        print(f".vscode folder already exists source dir:\n[{src_dir}]\n")
    os.mkdir(vscode_dir)
    print(f".vscode folder generated for source dir:\n[{src_dir}]\n")

    settings_path = os.path.join(vscode_dir, "settings.json")
    c_properties_path = os.path.join(vscode_dir, "c_cpp_properties.json")

    with open(settings_path, "w") as f:
        json.dump(settings, f)

    with open(c_properties_path, "w") as f:
        json.dump(c_properties, f)

    print(f"VS Code configuration JSON files generated:\n[{settings_path}]\n[{c_properties_path}]\n")
    return


def usage():
    print(os.linesep)
    print("zephyr2vsc ver 0.11")
    print("By ming.shao@intel.com")
    print("[Description]:")
    print("  This tool imports Zephyr source code into Visual Studio Code in the context of a Zephyr build.")
    print("[Pre-condition]:")
    print("  A Zephyr build must be made before using this tool because some build-generated files are needed.")
    print("[usage]:")
    print("  zephyr2vsc <compilerPath> <srcDir> <bldDir>")
    print("  <compilerPath>: the fullpath of the compiler")
    print("  <srcDir>: the Zephyr source code folder to open in VS Code.")
    print("  <bldDir>: the Zephyr build folder where build.ninja file is located.")
    return


if __name__=="__main__":   
    if(len(sys.argv)!= 4):
        usage()
    else:
        print("zephyr2vsc ver 0.0.2")
        print("By ming.shao@intel.com")

        compiler_path = os.path.abspath(os.path.normpath(sys.argv[1])) # this is the fullpath of the compiler.
        src_dir = os.path.abspath(os.path.normpath(sys.argv[2])) # this is the folder to open in VS Code.
        build_dir = os.path.abspath(os.path.normpath(sys.argv[3])) # this is the folder where build.ninja file is located.

        print(f"Start generating VSCode workspace for:\n[{src_dir}]\n")

        print("step 1")

        ninja_rules = get_ninja_rules(build_dir)
        used_c_files = get_relevant_c_files_relative_path(src_dir, build_dir)
        all_c_files = get_all_c_files_relative_path(src_dir)

        unused_c_files = all_c_files - used_c_files
        print(f"Exclude [{len(unused_c_files)}] unused C source files.\n")

        used_c_files_folders = {os.path.dirname(file) for file in used_c_files}

        db_full_path = generate_compilation_db(build_dir, ninja_rules)

        generate_vscode_config_jsons(
            unused_c_files,
            used_c_files,
            compiler_path,
            db_full_path,
            src_dir
        )

        print(f"Finished generating VSCode workspace for:\n[{src_dir}]\n")
