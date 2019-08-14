## Introduction

Visual Studio Code is a cross-platform IDE.

This tool imports Zephyr ([https://github.com/zephyrproject-rtos/zephyr](https://soco.intel.com/external-link.jspa?url=https%3A%2F%2Fgithub.com%2Fzephyrproject-rtos%2Fzephyr) ) source code into Visual Studio Code in the context of a build.

A build must be made before using this tool because certain dependent files are only generated after a build.

This tool can run on both Windows and Linux. 

## What you will get via this tool

- Exclusion of C files irrelevant to a specific Zephyr build
- Intellisense support
- Unambiguous symbol resolution
- Goto definition/declaration easily
- Rich VS Code extensions
- etc.

## Notes

This tool will exclude files which are NOT relevant to the selected build context.

But the file exclusion is only done for .c files. Not for other files.

So if you open arbitrary files such as a .h file, that file may NOT be relevant to the current build.

So the symbols in that file may NOT be fully resolved.

In future I may expand the scope of irrelevant file exclusion.

But for .c file browsing, it suffices, I think. 

## Pre-requisites

1. Install VS Code

   Windows: [https://code.visualstudio.com/docs/?dv=win](https://soco.intel.com/external-link.jspa?url=https%3A%2F%2Fcode.visualstudio.com%2Fdocs%2F%3Fdv%3Dwin)

   Linux:  [https://code.visualstudio.com/docs/?dv=linux64_deb](https://soco.intel.com/external-link.jspa?url=https%3A%2F%2Fcode.visualstudio.com%2Fdocs%2F%3Fdv%3Dlinux64_deb)  (Ubuntu like)

2. Install VSCode C/C++ Extension:

   [https://code.visualstudio.com/docs/languages/cpp](https://soco.intel.com/external-link.jspa?url=https%3A%2F%2Fcode.visualstudio.com%2Fdocs%2Flanguages%2Fcpp) 

## Usage

1. Download and extract the zip.

2. Goto the extracted folder.

3. Run "python zephyr2vsc.py" to see the usage info and run it. 

   ![zephyr2vs.usage](https://git-gar-1.devtools.intel.com/git/api/2/repos/mshao-zephyr2vscode/download/pics/zephyr2vs.usage.png?refspec=refs%2Fheads%2Fmaster&access_token=eyJraWQiOiIxIiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiJtc2hhbyIsImF1ZCI6WyJzb2FwNjAiLCJjdGYiLCJzdm4iLCJnZXJyaXQiXSwibmJmIjoxNTY1NjYwNDIyLCJhbXIiOlsidXJuOmN0ZjphbXI6anNlc3Npb24iXSwiaXNzIjoidXJuOmN0Zjppc3M6dGYtaWRwIiwiZXhwIjoxNTY1NjY0MDIyLCJpYXQiOjE1NjU2NjA0MjIsImp0aSI6IjgzMjQyMDEwLTgxZGUtNGQ2ZS1iZjllLTIxYzdiZDE0MDBkZCJ9.GtJ_SViTG0BqO_C9tPkR9_pBbc8xMqEkv9tT8Y_G7kmbMOrwxShvG94yM2K8Cb7suPpR4sTQGWIlnZPGWLJ6pNHT1JXAasoi6OpHHjLPAAM2HbqnRX9ciRIoxhIbltTx7cwRoWQ8Z8skUz6gGckt_I5clKwoBY2ZTG2ZpZL9zEA)

4. Open the zephyr source dir with VS Code. And wait for the database icon at the bottom right to disappear. 

   It takes less than 1 min on Windows. Linux is even faster. 

   This icon indicates that VS Code is parsing the files in the background.

   You can hover the mouse on it to see the progress. 

    ![file parsing icon](https://tf-amr-1.devtools.intel.com/ctf/code/projects.mshao/git/scm.zephyr2vscode/file/pics/file%20parsing%20icon.png)

## A sample run

![zephyr2vs.run](https://git-gar-1.devtools.intel.com/git/api/2/repos/mshao-zephyr2vscode/download/pics/zephyr2vs.run.png?refspec=refs%2Fheads%2Fmaster&access_token=eyJraWQiOiIxIiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiJtc2hhbyIsImF1ZCI6WyJzb2FwNjAiLCJjdGYiLCJzdm4iLCJnZXJyaXQiXSwibmJmIjoxNTY1NjYwNDIyLCJhbXIiOlsidXJuOmN0ZjphbXI6anNlc3Npb24iXSwiaXNzIjoidXJuOmN0Zjppc3M6dGYtaWRwIiwiZXhwIjoxNTY1NjY0MDIyLCJpYXQiOjE1NjU2NjA0MjIsImp0aSI6Ijk1ZDFjNDc4LWZiOWYtNDRlOS1iNjNlLTkwNjgwYmQ0YWQ0NyJ9.TRIizKI1CdwvV_dnwPmgB2nD4sydVcTpZksvBXjp8L1818uMhEHZCQsrH1598cgGQl1Xr5xyEURBWYQMSXvkH2xRN656dOg1O2mOGTBoyn3E8nvUD3BB3qLRByFjD1I2Jsm6MsNW5Cuyz_CZOTK70zllpvR9sBJYbzaUMdw5ILY)

## Known issues

1. Below VS Code bug is not fixed. Currently using a workaround.

   [https://github.com/microsoft/vscode-cpptools/issues/4063](https://github.com/microsoft/vscode-cpptools/issues/4063)

2. Do not change the driver letters with `subst` command on Windows after a Zephyr build is made.

   Because the .ninja files uses absolute path and the new driver letter will break the relative path handling.
