from sys import platform

import os, re, hashlib

from .localConfig import CoreConfig
from .swf import Swf
from .imports import ArrayList, Configuration, HighlightedTextWriter, ScriptExportMode

__all__ = ["BRAWLHALLA_PATH", "BRAWLHALLA_SWFS", "BRAWLHALLA_FILES", "BRAWLHALLA_VERSION"]


if platform in ["win32", "win64"]:
    import winreg

    def SearchBrawlhallaHome():
        steamFolders = []
        steampath = ""

        for reg in ["SOFTWARE\\WOW6432Node\\Valve\\Steam", "SOFTWARE\\Valve\\Steam"]:
            try:
                steampath = winreg.QueryValueEx(
                    winreg.OpenKey(
                        winreg.HKEY_LOCAL_MACHINE,
                        reg
                    ), 
                    "InstallPath"
                )[0]
                break

            except:
                pass

        if not steampath:
            return None

        steamFolders.append(os.path.join(steampath, "steamapps"))
        
        with open(os.path.join(steamFolders[0], "libraryfolders.vdf")) as vdf:
            for line in vdf.read().split("{")[1].split("}")[0].strip().split("\n"):
                find = re.findall(r'"(\d+)"\t\t"([^"]+)"', line.strip())
                if find: steamFolders.append(os.path.join(find[0][1].replace("\\\\", "\\"), "steamapps"))

        for folder in steamFolders:
            if (
                    "common" in os.listdir(folder) 
                    and 
                    "Brawlhalla" in os.listdir(os.path.join(folder, "common"))
                    and
                    "Brawlhalla.exe" in os.listdir(os.path.join(folder, "common", "Brawlhalla"))
                ):

                return os.path.join(folder, "common", "Brawlhalla")

        return None

elif platform == "darwin":
    def SearchBrawlhallaHome():
        return None

else:
    def SearchBrawlhallaHome():
        return None

BRAWLHALLA_PATH = SearchBrawlhallaHome()


def SearchBrawlhallaSwfs(brawlhallaPath: str):
    if brawlhallaPath is None:
        return None

    brawlhallaSwfs = {}

    for path, _, files in os.walk(brawlhallaPath):
        if len(path.replace(brawlhallaPath, "").split("\\")) > 2: continue
        
        for file in files:
            if not file.endswith(".swf"): continue

            brawlhallaSwfs[file] = os.path.join(path, file)

    return brawlhallaSwfs

BRAWLHALLA_SWFS = SearchBrawlhallaSwfs(BRAWLHALLA_PATH)


def SearchBrawlhallaFiles(brawlhallaPath: str):
    if brawlhallaPath is None:
        return None

    brawlhallaFiles = {}

    for path, _, files in os.walk(brawlhallaPath):
        for file in files:
            if file.endswith(".mp3") or file.endswith(".png") or file.endswith(".jpg"):
                brawlhallaFiles[file] = os.path.join(path, file)
                #brawlhallaFiles[brawlhallaFiles[file].replace(brawlhallaPath+"\\", "")] = brawlhallaFiles[file]

    return brawlhallaFiles

BRAWLHALLA_FILES = SearchBrawlhallaFiles(BRAWLHALLA_PATH)


def SearchBrawlhallaVersion(brawlhallaAirPath: str):
    with open(brawlhallaAirPath, "rb") as file:
        brawlhallaAirHash = hashlib.sha256(file.read()).hexdigest()

    if brawlhallaAirHash == CoreConfig.BrawlhallaAirHash:
        return CoreConfig.BrawlhallaVersion


    brawlhallaAir = Swf(brawlhallaAirPath)
    brawlhallaAir.load()

    for AS3Pack in brawlhallaAir.AS3Packs:
        methodInfos = ArrayList()
        AS3Pack.getMethodInfos(methodInfos)

        abc = AS3Pack.abc
        for methodInfo in methodInfos:
            bodyIndex = abc.findBodyIndex(methodInfo.getMethodIndex())

            if bodyIndex != -1:
                body = abc.bodies.get(bodyIndex)
                writer = HighlightedTextWriter(Configuration.getCodeFormatting(), True)
                abc.bodies.get(bodyIndex).getCode().toASMSource(abc.constants, abc.method_info.get(body.method_info), body, ScriptExportMode.PCODE, writer)

                search = re.findall(r'pushstring "(\d\.\d\d)"|pushstring "(\d\.\d\d\.\d)', str(writer.toString()))

                if search:
                    CoreConfig.BrawlhallaVersion = search[0][0] or search[0][1]
                    CoreConfig.BrawlhallaAirHash = brawlhallaAirHash
                    break

    brawlhallaAir.close()

    return CoreConfig.BrawlhallaVersion

BRAWLHALLA_VERSION = SearchBrawlhallaVersion(BRAWLHALLA_SWFS["BrawlhallaAir.swf"]) if BRAWLHALLA_SWFS else None