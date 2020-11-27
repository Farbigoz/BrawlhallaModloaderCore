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

from .utils.imports import *
from .utils.elementTypes import ElementAnyToObject
from .utils.localConfig import ModsConfig

from .file import File
from .modifier import ModifierTemplate, Modifier
from .mod import Mod, ModsFinder
from .gameswf import GameSwf, GAME_SWF_IMAGES_START, GAME_SWF_IMAGES_END

from typing import Dict, List, Union, Tuple


class OpenGameSwfFlag:
    pass
class InstalledModifierFlag:
    pass
class InstalledFileFlag:
    pass
class UninstalledModifierFlag:
    pass
class UninstalledFileFlag:
    pass
class DoneFlag:
    pass


class Processor:
    modifiersToInstall: Dict[str, List[ModifierTemplate]]
    filesPacksToInstall: list
    modifiersToUninstall: dict
    filesPacksToUninstall: list

    conflictMods: list

    def __init__(self):
        self.modifiersToInstall = {}
        self.filesPacksToInstall = []
        self.modifiersToUninstall = {}
        self.filesPacksToUninstall = []

        self.conflictMods = {} #{InstalledMod: NewMod} 


    def addModsToInstall(self, *mods):
        mods: List[Mod]

        for mod in mods:
            if mod.GHOST_MOD: continue

            for modifier in mod.modifierList:
                if modifier.swfName not in self.modifiersToInstall:
                    self.modifiersToInstall[modifier.swfName] = []

                for otherModifier in self.modifiersToInstall.get(modifier.swfName, []):
                    if modifier.findElementMatches(otherModifier):
                        otherMod = ModsFinder.findByHash(otherModifier.modHash)
                        if otherMod not in self.conflictMods.get(mod, []):
                            self.conflictMods[mod] = [*self.conflictMods.get(mod, []), otherMod]

                for otherMod in ModsFinder:
                    if not otherMod.installed: continue 

                    for otherModifier in otherMod.modifierList:
                        if modifier.findElementMatches(otherModifier):
                            if otherMod not in self.conflictMods.get(mod, []):
                                self.conflictMods[mod] = [*self.conflictMods.get(mod, []), otherMod]

                self.modifiersToInstall[modifier.swfName].append(modifier)
                if modifier in self.modifiersToUninstall.get(modifier.swfName, {}):
                    self.modifiersToUninstall[modifier.swfName].remove(modifier)


            for otherFilesPack in self.filesPacksToInstall:
                if mod.filesPack.findFilesMatches(otherFilesPack):
                    otherMod =  ModsFinder.findByHash(otherFilesPack.modHash)
                    if otherMod not in self.conflictMods.get(mod, []):
                        self.conflictMods[mod] = [*self.conflictMods.get(mod, []), otherMod]

            for otherMod in ModsFinder:
                if not otherMod.installed: continue 
                
                if mod.filesPack.findFilesMatches(otherMod.filesPack):
                    if otherMod not in self.conflictMods.get(mod, []):
                        self.conflictMods[mod] = [*self.conflictMods.get(mod, []), otherMod]

            self.filesPacksToInstall.append(mod.filesPack)
            


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


    def getStepNum(self):
        n = 0
        n += len([modifier for modifier in self.modifiersToInstall.values()])
        n += len([modifier for modifier in self.modifiersToUninstall.values()])
        n += len([file for filePack in self.filesPacksToInstall for file in filePack])
        n += len([file for filePack in self.filesPacksToUninstall for file in filePack])
        return n


    def _process(self) -> Tuple[Union[InstalledModifierFlag, InstalledFileFlag, UninstalledModifierFlag, UninstalledFileFlag], Union[ModifierTemplate, File]]:
        for swfName in self.modifiersToInstall:
            yield OpenGameSwfFlag, swfName

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
                yield UninstalledModifierFlag, modifier

                self.uninstallModifier(gameSwf, modifier)

                yield DoneFlag, 


            #Installer
            for modifier in [
                                modifier
                                for modifier in self.modifiersToInstall[swfName]
                                if modifier.modHash not in gameSwf.installedMods
                            ]:
                yield InstalledModifierFlag, modifier

                self.installModifier(gameSwf, modifier)

                yield DoneFlag, 

            gameSwf.save()
            gameSwf.close()



        for swfName in self.modifiersToUninstall:
            yield OpenGameSwfFlag, swfName
            
            gameSwf = GameSwf(swfName)
            gameSwf.load()

            #Uninstaller
            for modifier in [
                                modifier
                                for modifier in self.modifiersToUninstall[swfName]
                                if modifier.modHash in gameSwf.installedMods
                            ]:
                yield UninstalledModifierFlag, modifier

                self.uninstallModifier(gameSwf, modifier)

                yield DoneFlag, 


            gameSwf.save()
            gameSwf.close()



        for filePack in self.filesPacksToInstall:
            for file in filePack:
                yield InstalledFileFlag, file

                file.place()

                yield DoneFlag, 

        for filePack in self.filesPacksToUninstall:
            for file in filePack:
                yield UninstalledFileFlag, file
                
                file.repair()

                yield DoneFlag, 

        uninstalledModsHashes = set([modifier.modHash for modifiers in self.modifiersToUninstall.values() for modifier in modifiers])
        installedModsHashes = set([modifier.modHash for modifiers in self.modifiersToInstall.values() for modifier in modifiers])
        ModsConfig.InstalledMods = list(( set(ModsConfig.InstalledMods) - uninstalledModsHashes ) | installedModsHashes)

        self.modifiersToInstall = {}
        self.filesPacksToInstall = []
        self.modifiersToUninstall = {}
        self.filesPacksToUninstall = []
        self.conflictMods = {} #{InstalledMod: NewMod} 


    def process(self, generator=False):
        if generator:
            return self._process()
        else:
            return [n for n in self._process()]

