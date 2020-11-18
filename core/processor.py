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

import os

from .utils.imports import *
from .utils.elementTypes import ElementAnyToObject
from .utils.gameconstants import BRAWLHALLA_SWFS
from .utils.localConfig import ModsConfig

from .file import FilesPack, File
from .modifier import ModifierTemplate, Modifier
from .mod import Mod
from .gameswf import GameSwf, GAME_SWF_IMAGES_START, GAME_SWF_IMAGES_END

from typing import Dict, List, Union, Tuple



class InstalledModifierFlag:
    pass
class InstalledFileFlag:
    pass
class UninstalledModifierFlag:
    pass
class UninstalledFileFlag:
    pass


class Processor:
    files: List[str]
    modifiersElements: Dict[str, List[int]]

    modifiersToInstall: Dict[str, List[ModifierTemplate]]
    filesPacksToInstall: list
    modifiersToUninstall: dict
    filesPacksToUninstall: list

    conflictMods: list

    def __init__(self):
        self.modifiersElements = {}
        self.files = []

        self.modifiersToInstall = {}
        self.filesPacksToInstall = []
        self.modifiersToUninstall = {}
        self.filesPacksToUninstall = []

        self.conflictMods = []


    def addModsToInstall(self, *mods):
        mods: List[Mod]

        for mod in mods:
            if mod.GHOST_MOD: continue

            for modifier in mod.modifierList:
                if modifier.swfName not in self.modifiersToInstall:
                    self.modifiersToInstall[modifier.swfName] = []
                    self.modifiersElements[modifier.swfName] = []

                self.modifiersToInstall[modifier.swfName].append(modifier)
                if modifier in self.modifiersToUninstall.get(modifier.swfName, {}):
                    self.modifiersToUninstall[modifier.swfName].remove(modifier)

                modifierElements = [element for elements in modifier.elements.values() for element in elements]

                if set(modifierElements) & set(self.modifiersElements[modifier.swfName]):
                    self.conflictMods.append(mod)
                    
                self.modifiersElements[modifier.swfName] += modifierElements

            self.filesPacksToInstall.append(mod.filesPack)


            files = [file.fileName for file in mod.filesPack]

            if set(files) & set(self.files):
                self.conflictMods.append(mod)

            self.files += files


    def addModsToUninstall(self, *mods):
        mods: List[Mod]

        for mod in mods:
            for modifier in mod.modifierList:
                if modifier.swfName not in self.modifiersToUninstall:
                    self.modifiersToUninstall[modifier.swfName] = []

                self.modifiersToUninstall[modifier.swfName].append(modifier)
                if modifier in self.modifiersToInstall.get(modifier.swfName, {}):
                    self.modifiersToInstall[modifier.swfName].remove(modifier)

            self.filesPacksToUninstall.append(mod.filesPack)


    def installModifier(self, gameSwf: GameSwf, modifier: Modifier):
        if gameSwf.swf is None: gameSwf.load()
        if modifier.swf is None: modifier.load()

        #Backup elements
        for elType, elIds in modifier.elements.items():
            for elId in elIds:
                gameSwf.backupElement(elType=elType, elId=elId)

        #Modified elements
        for element, elId in modifier.elementsMap.items():
            elType = ElementAnyToObject(element)
            cloneElement = element.cloneTag()

            if elType in [*DefineShapeTags, DefineSpriteTag, DefineSoundTag, DefineEditTextTag, CSMTextSettingsTag, *DefineFontTags]:
                origElement = gameSwf.getElementById(elId, elType)
                gameSwf.replaceElement(origElement, cloneElement)

            if elType in DefineShapeTags:
                if elId in modifier.repeatingBeatmaps:
                    #Add link to image
                    imageId = modifier.repeatingBeatmaps[elId]
                    image = modifier.getElementById(imageId, elTypes=DefineBitsLosslessTags)

                    for n in range(GAME_SWF_IMAGES_START, GAME_SWF_IMAGES_END):
                        if n not in gameSwf.imagesMap:
                            newImageId = n
                            break

                    cloneImage = image.cloneTag()
                    modifier.setElementId(cloneImage, newImageId)
                    cloneImage.setModified(True)
                    gameSwf.addElement(cloneImage)
                    gameSwf.imagesMap[newImageId] = cloneImage

                    cloneElement.shapes.fillStyles.fillStyles[0].bitmapId = newImageId
                    cloneElement.setModified(True)

            elif elType in DefineFontTags:
                #Replcae FontNameElement
                origFontNameElement = gameSwf.getElementById(elId, DefineFontNameTag)
                cloneFontNameElement = modifier.getElementById(elId, DefineFontNameTag).cloneTag()
                gameSwf.replaceElement(origFontNameElement, cloneFontNameElement)

                #Replace\Remove\Add FontAlignZonesTag
                origFontAlignZones = gameSwf.getElementById(elId, DefineFontAlignZonesTag)
                cloneFontAlignZones = modifier.getElementById(elId, DefineFontAlignZonesTag)

                if origFontAlignZones is not None and cloneFontAlignZones is not None:
                    gameSwf.replaceElement(origFontAlignZones, cloneFontAlignZones.cloneTag())
                elif origFontAlignZones is not None and cloneFontAlignZones is None:
                    gameSwf.removeElement(origFontAlignZones)
                elif origFontAlignZones is None and cloneFontAlignZones is not None:
                    gameSwf.addElement(cloneFontAlignZones.cloneTag())

        gameSwf.installedMods.append(modifier.modHash)


    def uninstallModifier(self, gameSwf: GameSwf, modifier: Modifier):
        if gameSwf.swf is None: gameSwf.load()
        if modifier.swf is None: modifier.load()

        for elType, elIds in modifier.elements.items():
            for elId in elIds:
                gameSwf.repairElement(elType=elType, elId=elId)

        gameSwf.installedMods.remove(modifier.modHash)


    def _process(self) -> Tuple[Union[InstalledModifierFlag, InstalledFileFlag, UninstalledModifierFlag, UninstalledFileFlag], Union[ModifierTemplate, File]]:
        for swfName in self.modifiersToInstall:
            gameSwf = GameSwf(swfName)
            gameSwf.load()

            #Uninstaller
            for modifier in set([
                                *[  
                                    modifier
                                    for modifier in self.modifiersToUninstall.get(swfName, [])
                                    if modifier.modHash in gameSwf.installedMods
                                ],
                                *[
                                    modifier
                                    for modifier in self.modifiersToInstall[swfName]
                                    if modifier.modHash in gameSwf.installedMods
                                ]
                            ]):
                self.uninstallModifier(gameSwf, modifier)

                yield UninstalledModifierFlag, modifier


            #Installer
            for modifier in [
                                modifier
                                for modifier in self.modifiersToInstall[swfName]
                                if modifier.modHash not in gameSwf.installedMods
                            ]:
                self.installModifier(gameSwf, modifier)

                yield InstalledModifierFlag, modifier

            gameSwf.save()
            gameSwf.close()



        for swfName in self.modifiersToUninstall:
            gameSwf = GameSwf(swfName)
            gameSwf.load()

            #Uninstaller
            for modifier in [
                                modifier
                                for modifier in self.modifiersToUninstall[swfName]
                                if modifier.modHash in gameSwf.installedMods
                            ]:
                self.uninstallModifier(gameSwf, modifier)

                yield UninstalledModifierFlag, modifier


            gameSwf.save()
            gameSwf.close()



        for filePack in self.filesPacksToInstall:
            for file in filePack:
                file.place()

                yield InstalledFileFlag, file

        for filePack in self.filesPacksToUninstall:
            for file in filePack:
                file.repair()

                yield UninstalledFileFlag, file

        uninstalledModsHashes = set([modifier.modHash for modifiers in self.modifiersToUninstall.values() for modifier in modifiers])
        installedModsHashes = set([modifier.modHash for modifiers in self.modifiersToInstall.values() for modifier in modifiers])
        ModsConfig.InstalledMods = list(( set(ModsConfig.InstalledMods) - uninstalledModsHashes ) | installedModsHashes)

        self.modifiersToInstall = {}
        self.filesPacksToInstall = []
        self.modifiersToUninstall = {}
        self.filesPacksToUninstall = []


    def process(self, generator=False):
        if generator:
            return self._process()
        else:
            return [n for n in self._process()]

