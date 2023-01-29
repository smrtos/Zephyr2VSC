"""Define the constants for zephyr2vsc."""

SETTINGS_JSON_TEMPLATE = {
    "files.exclude": {
        "**/.git": True,
        "**/.svn": True,
        "**/.hg": True,
        "**/CVS": True,
        "**/.DS_Store": True,
        "**/test*": True,
    },
    "C_Cpp.exclusionPolicy": "checkFilesAndFolders",
    "C_Cpp.intelliSenseEngine": "Default",
    "cmake.configureOnOpen": False,
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
            "browse": {
                "limitSymbolsToIncludedHeaders": True,
                "databaseFilename": "${workspaceFolder}/.vscode/browse.zephyr.db",
                "path": [],
            },
        }
    ],
    "version": 4,
}
