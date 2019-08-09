import sys
import os.path
import re
import io
import string
import json
import subprocess

def GetNinjaRules(everything):
    rulesFile = everything["ninjaRulesFile"]
    rules = []

    with open(rulesFile, "r") as f:
        lines = f.readlines()
    
    for line in lines:
        m = re.match(r"^rule\s([^\n]*)$", line)
        if(not m is None):
            rules.append(m.group(1))

    everything["ninjaRules"] = list(set(rules))
    return

def GetAllCFilesRelativePath(everything):
    srcDir = everything["srcDir"]
    allCFiles = []
    for _dir, _subdirs, _files in os.walk(srcDir):
        if(len(_files)==0):
            continue
        for _file in _files:
            if(_file[-2:] == ".c"):
                cFile = os.path.join(_dir, _file)
                allCFiles.append(os.path.relpath(cFile,srcDir)) # get the relative path to the srcDir
    
    everything["allCFiles"] = list(set(allCFiles))
#    for cFile in allCFiles:
#        print(cFile)
    return

def GetRelevantCFilesRelativePath(everything):
    buildFile = everything["ninjaBldFile"]
    srcDir = everything["srcDir"]
    bldDir = everything["bldDir"] 
    cFiles = []

    with open(buildFile, "r") as f:
        lines = f.readlines()
    
    for line in lines:
        m = re.match(r"^build\s.*\s([^\s|]+\.c)\s", line)
        if(not m is None):
            cFile = os.path.normpath(m.group(1).replace("$", ""))
            if(not os.path.isabs(cFile)):
                #This must be a build generated file
                cFiles.append(os.path.normpath(os.path.join(bldDir, cFile)))
            else:
                cFiles.append(os.path.relpath(cFile, srcDir))# get the relative path to the srcDir
    everything["cFiles"] = list(set(cFiles))
#    for cFile in cFiles:
#        print(cFile)
    return

def GetExcludedCFilesRelativePath(everything):
    relevantCFilesSet = set(everything["cFiles"])
    allCFilesSet = set(everything["allCFiles"])
    excludeCFiles = allCFilesSet - relevantCFilesSet
    everything["excludeCFiles"] = list(set(excludeCFiles))
    return

def CreateDotVSCodeFolderInSrcDir(everything):
    vscodeDir = os.path.join(everything["srcDir"], ".vscode")
    everything["vscodeDir"] = vscodeDir
    if(os.path.exists(vscodeDir)):
        return
    os.mkdir(vscodeDir)
    return

def GenerateCompilationDB(everything):
    compDBFileFullpath = os.path.join(everything["bldDir"], "zephyr_compile_db.json") # compDB will be saved in the bldDir
    allRulesString = " ".join(everything["ninjaRules"])
    cmdString = r"ninja -C <BLD_DIR> -t compdb <RULES>"
    cmdString = cmdString.replace(r"<BLD_DIR>", everything["bldDir"])
    #cmdString = cmdString.replace(r"<COMPDB_OUTPUT>", compDBFileFullpath)
    cmdString = cmdString.replace(r"<RULES>", allRulesString)

    with open(compDBFileFullpath, "w") as f:
        subprocess.run(cmdString, stdout=f)

    f = open(compDBFileFullpath, "r")
    fixedLines = []
    for line in f.readlines():
        fixedLines.append(line.replace("--imacros=", "-include")) # workaround https://github.com/Microsoft/vscode-cpptools/issues/2417
    f.close()

    f = open(compDBFileFullpath, "w")
    f.writelines(fixedLines)
    f.close()   

    everything["compDBFileFullpath"] = compDBFileFullpath
    print("Zephyr compilation DB is saved as: " + compDBFileFullpath)
    return

def GenerateVSCConfigJSONs(everything):
    settings = everything["settings.json"]
    cprops = everything["c_cpp_properties.json"]
    settingsDecoded= None
    cpropsDecoded = None
    with open(settings, "r") as f:
        settingsDecoded = json.load(f)        
    with open(cprops, "r") as f:
        cpropsDecoded = json.load(f) 

    for excludedCFile in everything["excludeCFiles"]:
        settingsDecoded["files.exclude"][excludedCFile] = True
    
    settingsDecoded["files.exclude"]["**/.github"] = True
    settingsDecoded["files.exclude"]["**/.known-issues"] = True
    settingsDecoded["files.exclude"]["**/.vscode"] = True

    cpropsDecoded["configurations"][0]["compileCommands"]= everything["compDBFileFullpath"]
    cpropsDecoded["configurations"][0]["compilerPath"]= everything["compilerPath"]

    CreateDotVSCodeFolderInSrcDir(everything)
    vscodeDir = everything["vscodeDir"]
    targetSettingsJsonFullpath = os.path.join(vscodeDir, "settings.json")
    targetCPropsJsonFullpath = os.path.join(vscodeDir, "c_cpp_properties.json")

    with open(targetSettingsJsonFullpath, "w") as f:
        json.dump(settingsDecoded, f)

    with open(targetCPropsJsonFullpath, "w") as f:
        json.dump(cpropsDecoded, f)


    return

def GetNinjaRulesFile(everything):
    everything["ninjaRulesFile"]= os.path.join(everything["bldDir"], "rules.ninja")
    return

def GetNinjaBuildFile(everything):
    everything["ninjaBldFile"]= os.path.join(everything["bldDir"], "build.ninja")
    return

def LoadVSCJSONTemplates(everything):
    everything["settings.json"] = os.path.abspath(os.path.join(os.curdir, r"settings.json"))
    everything["c_cpp_properties.json"] = os.path.abspath(os.path.join(os.curdir, r"c_cpp_properties.json"))    
    return

def DeriveOtheConfigs(everything):
    GetNinjaRulesFile(everything)
    GetNinjaBuildFile(everything)
    LoadVSCJSONTemplates(everything)
    return


def DoWork(everything):
    print("Start generating VSCode workspace for Zephyr")
    DeriveOtheConfigs(everything)    
    GetNinjaRules(everything)
    GetRelevantCFilesRelativePath(everything)
    GetAllCFilesRelativePath(everything)
    GetExcludedCFilesRelativePath(everything)

    GenerateCompilationDB(everything)
    GenerateVSCConfigJSONs(everything)

    return    

def Usage():
    print("Usage:\n")
    print("zephyr2vsc <srcDir> <bldDir> <compilerPath>")
    print("\t <srcDir>: the source code folder to open in VS Code.")
    print("\t <bldDir>: the build folder where build.ninja file is located.")
    print("\t <compilerPath>: the fullpath of the compiler")
    return


def CleanseArgs(everything):
    return
    


if __name__=="__main__":
    everything = dict()    
    if(len(sys.argv)!= 4):
        Usage()
    else:
        everything["srcDir"] = os.path.normpath(sys.argv[1]) # this is the folder to open in VS Code.
        everything["bldDir"] = os.path.normpath(sys.argv[2]) # this is the folder where build.ninja file is located.
        everything["compilerPath"] = os.path.normpath(sys.argv[3]) # this is the folder where build.ninja file is located.
        CleanseArgs(everything)
        DoWork(everything)
        
    sys.exit(0)