Visual Studio Code is a cross-platform IDE.
This tool imports Zephyr (https://github.com/zephyrproject-rtos/zephyr ) source code into Visual Studio Code in the context of a build.
A build must be made before using this tool because certain dependent files are only generated after a build.
This tool can run on both Windows and Linux.

With this tool, you will get:
-Exclusion of C files irrelevant to a specific Zephyr build
-Intellisense support
-Unambiguous symbol resolution
-Goto definition/declaration easily
-Rich VS Code extensions
-etc.

Note:
This tool will exclude files which are NOT relevant to the selected build context.
But the file exclusion is only done for .c files. Not for other files.
So if you open arbitrary files such as a .h file, that file may NOT be relevant to the current build.
So the symbols in that file may NOT be fully resolved.
In future I may expand the scope of irrelevant file exclusion.
But for .c file browsing, it suffices, I think.

Known issues:
1. Below VS Code bug is not fixed. Currently using a workaround.
   https://github.com/microsoft/vscode-cpptools/issues/4063
2. Do not change the driver letters with subst command on Windows after a Zephyr build is made.
   Because the .ninja files uses absolute path and the new driver letter will break the relative path handling.