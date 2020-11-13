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

import os, zipfile, shutil, hashlib
from typing import List
from .utils.gameconstants import BRAWLHALLA_PATH, BRAWLHALLA_FILES
from .utils.localConfig import LOCAL_DATA_PATH, ModsConfig



FILES_PACK = "pack.zip"
FILES_DUMP_FOLDER = os.path.join(LOCAL_DATA_PATH, "files")

if not os.path.exists(FILES_DUMP_FOLDER):
    os.mkdir(FILES_DUMP_FOLDER)


class File:
    packZip: zipfile.ZipFile
    file: str

    GHOST_MOD: bool
    
    def __init__(self, packZip, fileName, filePath, fileHash):
        self.GHOST_MOD = not bool(packZip)

        self.packZip = packZip
        self.fileName = fileName
        self.filePath = filePath
        self.fileHash = fileHash

    def place(self):
        if self.GHOST_MOD: return

        with open(BRAWLHALLA_FILES[self.fileName], "rb") as file:
            fileHash = hashlib.sha256(file.read()).hexdigest()[:16]

        #Если файл ниразу небыл сдамплен
        if self.fileName not in ModsConfig.OriginalFiles:
            self.dump(fileHash)

        #Если файл был обновлён
        if self.fileName in ModsConfig.ModifiedFiles and ModsConfig.ModifiedFiles[self.fileName] != fileHash:
            self.dump(fileHash)

        ModsConfig.ModifiedFiles = {**ModsConfig.ModifiedFiles, self.fileName:self.fileHash}
        self.packZip.extract(self.filePath.replace("\\", "/"), BRAWLHALLA_PATH)

    def dump(self, fileHash=None):
        if fileHash is None:
            with open(BRAWLHALLA_FILES[self.fileName], "rb") as file:
                fileHash = hashlib.sha256(file.read()).hexdigest()[:16]

        shutil.copyfile(BRAWLHALLA_FILES[self.fileName], os.path.join(FILES_DUMP_FOLDER, self.fileName))
        ModsConfig.OriginalFiles = {**ModsConfig.OriginalFiles, self.fileName: fileHash}

    def repair(self):
        shutil.copyfile(os.path.join(FILES_DUMP_FOLDER, self.fileName), BRAWLHALLA_FILES[self.fileName])
        ModsConfig.ModifiedFiles = {**ModsConfig.ModifiedFiles, self.fileName:ModsConfig.OriginalFiles[self.fileName]}

    def __repr__(self):
        return f"<File: {self.fileName}>"


class FilesPack:
    modPath: str
    files: List[File]

    GHOST_MOD: bool

    def __init__(self, modPath=None):
        self.GHOST_MOD = not bool(modPath)
        
        self.modPath = modPath
        self.files = []
        if os.path.exists(os.path.join(self.modPath, FILES_PACK)):
            self.packZip = zipfile.ZipFile(os.path.join(self.modPath, FILES_PACK), "r") if not self.GHOST_MOD else None
        else:
            self.packZip = None

    def addFile(self, fileName, filePath, fileHash):
        self.files.append(File(self.packZip, fileName, filePath, fileHash))

    def __iter__(self) -> File:
        for file in self.files:
            yield file