# *****************************************************************************
#
#                           Brawlhalla Modloader Core
#   Copyright (C) 2020 Farbigoz
#   
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#   Contacts:
#       GitHub: https://github.com/Farbigoz
#       Gmail: ferattori@gmail.com
#       VK: https://vk.com/fabriziog    (Preferably)
#
# *****************************************************************************

from sys import platform

import os, re, hashlib

from .localConfig import CoreConfig
from .swf import Swf
from .imports import ArrayList, Configuration, HighlightedTextWriter, ScriptExportMode

__all__ = ["BRAWLHALLA_PATH", "BRAWLHALLA_SWFS", "BRAWLHALLA_FILES", "BRAWLHALLA_VERSION"]


if platform in ["win32", "win64"]:
    import winreg

    def SearchBrawlhallaHome():
        brawlhallaFolders = []
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

        with open(os.path.join(os.path.join(steampath, "steamapps"), "libraryfolders.vdf")) as vdf:
            for line in [
                            *vdf.read().split("{")[1].split("}")[0].strip().split("\n"),
                            f'"0"\t\t"{steampath}"'
                        ]:

                find = re.findall(r'"\d*"\t\t"([^"]*)"', line.strip())

                if find: 
                    folder = os.path.join(find[0].replace("\\\\", "\\"), "steamapps")
                    if "common" in os.listdir(folder) and "Brawlhalla" in os.listdir(os.path.join(folder, "common")):
                        brawlhallaFolders.append(os.path.join(folder, "common", "Brawlhalla"))

        brawlhallaFolders = list(set([*brawlhallaFolders, *CoreConfig.BrawlhallaAllowedPaths]))

        found = []
        for folder in brawlhallaFolders:
            if os.path.exists(folder) and "Brawlhalla.exe" in os.listdir(folder) and "BrawlhallaAir.swf" in os.listdir(folder):
                if folder in CoreConfig.BrawlhallaIgnoredPaths:
                    continue

                found.append(folder)

        return None if found == [] else (found[0] if len(found) == 1 else found)

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

BRAWLHALLA_SWFS = SearchBrawlhallaSwfs(BRAWLHALLA_PATH) if isinstance(BRAWLHALLA_PATH, str) else None


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

BRAWLHALLA_FILES = SearchBrawlhallaFiles(BRAWLHALLA_PATH) if isinstance(BRAWLHALLA_PATH, str) else None


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

BRAWLHALLA_VERSION = SearchBrawlhallaVersion(BRAWLHALLA_SWFS["BrawlhallaAir.swf"]) if isinstance(BRAWLHALLA_PATH, str) else None
