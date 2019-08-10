This tool imports Zephyr source code into Visual Studio Code in the context of a build.
A build must be made before using this tool because certain dependent files are only generated after a build.

This tool will exclude files which are NOT relevant to the selected build context.
But the file exclusion is only done for .c files. Not for other files.
So if you open arbitrary files such as a .h file, that file may NOT be relevant to the current build.
So the symbols in that file may NOT be fully resolved.
In future I may expand the scope of irrelevant file exclusion.
But for .c file browsing, it suffices, I think.

Due to https://github.com/microsoft/vscode-cpptools/issues/4059,
pressing F12 on a function call can only goes to function prototype declaration for now.



