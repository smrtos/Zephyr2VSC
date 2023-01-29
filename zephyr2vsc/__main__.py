"""The CLI entrypoint of zephyr2vsc."""

import os
import sys

from zephyr2vsc.helpers import (
    generate_compilation_db,
    generate_vscode_config_jsons,
    get_all_c_files_relative_path,
    get_ninja_rules,
    get_relevant_c_files_relative_path,
)

USAGE = f"""
{os.linesep}
zephyr2vsc ver 0.11
By ming.shao@intel.com
[Description]:
  This tool imports Zephyr source code into Visual Studio Code in the context of a Zephyr build.
[Pre-condition]:
  A Zephyr build must be made before using this tool because some build-generated files are needed.
[usage]:
  zephyr2vsc <compilerPath> <srcDir> <bldDir>
  <compilerPath>: the fullpath of the compiler
  <srcDir>: the Zephyr source code folder to open in VS Code.
  <bldDir>: the Zephyr build folder where build.ninja file is located.
"""

if len(sys.argv) != 4:
    print(USAGE)
else:
    print("zephyr2vsc ver 0.0.2")
    print("By ming.shao@intel.com")

    compiler_path = os.path.abspath(
        os.path.normpath(sys.argv[1])
    )  # this is the fullpath of the compiler.
    src_dir = os.path.abspath(
        os.path.normpath(sys.argv[2])
    )  # this is the folder to open in VS Code.
    build_dir = os.path.abspath(
        os.path.normpath(sys.argv[3])
    )  # this is the folder where build.ninja file is located.

    print(f"Start generating VSCode workspace for:\n[{src_dir}]\n")

    print("step 1")

    ninja_rules = get_ninja_rules(build_dir)
    used_c_files = get_relevant_c_files_relative_path(src_dir, build_dir)
    all_c_files = get_all_c_files_relative_path(src_dir)

    unused_c_files = all_c_files - used_c_files
    print(f"Exclude [{len(unused_c_files)}] unused C source files.\n")

    db_full_path = generate_compilation_db(build_dir, ninja_rules)

    generate_vscode_config_jsons(unused_c_files, used_c_files, compiler_path, db_full_path, src_dir)

    print(f"Finished generating VSCode workspace for:\n[{src_dir}]\n")
