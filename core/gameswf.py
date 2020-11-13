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
from .utils.elementTypes import ElementAnyToObject, ElementAnyToStr
from .utils.exceptions import FileDoesNotExist
from .utils.gameconstants import BRAWLHALLA_SWFS
from .utils.swf import Swf, SwfUtils


SYMBOL_CLASS_TAG_IS_MODIFIED            = 0xffff
SYMBOL_CLASS_TAG_BACKUP_ELEMENTS        = 0xfffe
SYMBOL_CLASS_TAG_BACKUP_ACTION_SCRIPTS  = 0xfffd
SYMBOL_CLASS_TAG_INSTALLED_MODS         = 0xfffc



GAME_SWF_ELEMENTS_START   = 0x0000
GAME_SWF_ELEMENTS_END     = 0x4fff
GAME_SWF_IMAGES_START     = 0x5000
GAME_SWF_IMAGES_END       = 0x6fff
GAME_SWF_FONTS_START      = 0x7000
GAME_SWF_FONTS_END        = 0x7fff
GAME_SWF_BACKUP_START     = 0x8000
GAME_SWF_BACKUP_END       = 0xffff


class GameSwf(Swf, SwfUtils):
    backupElements: dict        #{elType: {oldId: newId, ...}, ...}
    backupActionsScripts: dict  #{scriptName: content, ...}
    installedMods: list         #[modHash, ...]                               #{modHash: {swfName: {elType: {elId: element, ...}, ...}, ...}, ...}

    origElementsList: list  #[element, ...]
    imagesMap: dict         #{elId: element, ...}
    backupElementsList: list#[element, ...]

    def __init__(self, swfName):
        swfName = swfName.replace(".swf", "") + ".swf"
        if swfName not in BRAWLHALLA_SWFS:
            raise FileDoesNotExist(f"Game file '{swfName}' doesn't exists")

        super().__init__(BRAWLHALLA_SWFS[swfName])

    def init(self, *args):
        super().init(*args)

        self.backupElements = {}
        self.backupActionsScripts = {}
        self.installedMods = []

        self.origElementsList = []
        self.imagesMap = {}
        self.backupElementsList = []

    def load(self):
        super().load()

        if self.symbolClass.getTag(SYMBOL_CLASS_TAG_IS_MODIFIED):
            self.backupElements = self.symbolClass.getTag(SYMBOL_CLASS_TAG_BACKUP_ELEMENTS)
            self.backupActionsScripts = self.symbolClass.getTag(SYMBOL_CLASS_TAG_BACKUP_ACTION_SCRIPTS)
            self.installedMods = self.symbolClass.getTag(SYMBOL_CLASS_TAG_INSTALLED_MODS)
        else:
            self.symbolClass.addTag(SYMBOL_CLASS_TAG_IS_MODIFIED, True)
            self.symbolClass.addTag(SYMBOL_CLASS_TAG_BACKUP_ELEMENTS, {})
            self.symbolClass.addTag(SYMBOL_CLASS_TAG_BACKUP_ACTION_SCRIPTS, {})
            self.symbolClass.addTag(SYMBOL_CLASS_TAG_INSTALLED_MODS, [])
            self.symbolClass.save()

        for elType, elIdsMap in self.backupElements.items():
            self.backupElements[elType] = {int(old):int(new) for old, new in elIdsMap.items()}

        for element, elId in self.elementsMap.items():
            elType = type(element)

            if elId >= GAME_SWF_ELEMENTS_START and elId <= GAME_SWF_ELEMENTS_END:
                self.origElementsList.append(element)

            elif elType in DefineBitsLosslessTags and elId >= GAME_SWF_IMAGES_START and elId <= GAME_SWF_IMAGES_END:
                self.imagesMap[elId] = element

            elif elId >= GAME_SWF_BACKUP_START and elId <= GAME_SWF_BACKUP_END:
                self.backupElementsList.append(element)

        return self

    def save(self):
        self.symbolClass.setTag(SYMBOL_CLASS_TAG_BACKUP_ELEMENTS, self.backupElements)
        self.symbolClass.setTag(SYMBOL_CLASS_TAG_BACKUP_ACTION_SCRIPTS, self.backupActionsScripts)
        self.symbolClass.setTag(SYMBOL_CLASS_TAG_INSTALLED_MODS, self.installedMods)
        self.symbolClass.save()

        super().save()

    def __backupElement(self, element, elId, newElId):
        if element is None: return 
        
        cloneElement = element.cloneTag()
        self.setElementId(cloneElement, newElId)

        strElType = ElementAnyToStr(element)

        if strElType not in self.backupElements:
            self.backupElements[strElType] = {}
        self.backupElements[strElType][elId] = newElId

        self.addElement(cloneElement)

        self.backupElementsList.append(cloneElement)
    
    def backupElement(self, element: object=None, elType: object=None, elId: int=None):
        if element is not None:
            elType = ElementAnyToObject(element)
        else:
            elType = ElementAnyToObject(elType)

        strElType = ElementAnyToStr(elType)

        if elType in [*DefineBitsLosslessTags, CSMTextSettingsTag, DefineFontNameTag, DefineFontAlignZonesTag]:
            pass

        elif elType == ActionScriptTag:
            if elId not in self.backupActionsScripts:
                for pack in self.AS3Packs:
                    if str(pack) != elId: continue
                    self.backupActionsScripts[elId] = str(self.swf.getCached(pack).text)
                    break

        else:
            if elId is None:
                elId = self.getElementId(element)

            if self.backupElements.get(strElType, {}).get(elId, None) is None:
                element = self.getElementById(elId, elType)
                newElId = max([_elId for _elIds in self.backupElements.values() for _elId in _elIds.values()] or [GAME_SWF_BACKUP_START-1]) + 1

                self.__backupElement(element, elId, newElId)

                if elType == DefineEditTextTag:
                    csmtext = self.getElementById(elId, CSMTextSettingsTag)
                    self.__backupElement(csmtext, elId, newElId)

                elif elType in DefineFontTags:
                    fontname = self.getElementById(elId, DefineFontNameTag)
                    self.__backupElement(fontname, elId, newElId)

                    fontalign = self.getElementById(elId, DefineFontAlignZonesTag)
                    if fontalign is not None: self.__backupElement(fontalign, elId, newElId)

    def repairElement(self, element: object=None, elType: object=None, elId: int=None):
        if element is not None:
            elType = ElementAnyToObject(element)
        else:
            elType = ElementAnyToObject(elType)

        strElType = ElementAnyToStr(elType)

        if elType in [*DefineBitsLosslessTags]:#, CSMTextSettingsTag, DefineFontNameTag, DefineFontAlignZonesTag]:
            pass

        elif elType == ActionScriptTag:
            if elId in self.backupActionsScripts:
                for pack in self.AS3Packs:
                    if str(pack) != elId: continue
                    scriptRplacer = As3ScriptReplacerFactory.createByConfig()
                    pack.abc.replaceScriptPack(scriptRplacer, pack, self.backupActionsScripts[elId])
                    break
            pass

        else:
            if elId is None:
                elId = self.getElementId(element)

            if self.backupElements.get(strElType, {}).get(elId, None) is not None:
                element = self.getElementById(elId, elType)
                origElement = self.getElementById(self.backupElements[strElType][elId], elType).cloneTag()

                self.setElementId(origElement, elId)

                if element is None:
                    pass
                else:
                    if elType in DefineShapeTags:
                        element.getShapes()
                        if element.shapes.fillStyles.fillStyles and element.shapes.fillStyles.fillStyles[0].fillStyleType == 64:
                            imageId = int(element.shapes.fillStyles.fillStyles[0].bitmapId)
                            image = self.imagesMap.pop(imageId, None)
                            if image:
                                self.removeElement(image)

                    self.replaceElement(element, origElement)


