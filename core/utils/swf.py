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

from .exceptions import FileDoesNotExist
from .imports import *
from .elementTypes import ElementAnyToObject, ElementAnyToStr
from .symbolclass import SymbolClass


SYMBOL_CLASS_TAG_IS_MODIFIED            = 0xffff
SYMBOL_CLASS_TAG_BACKUP_ELEMENTS        = 0xfffe
SYMBOL_CLASS_TAG_BACKUP_ACTION_SCRIPTS  = 0xfffd
SYMBOL_CLASS_TAG_INSTALLED_MODS         = 0xfffc


class SwfUtils:
    def setElementId(self, element: object, elId: int):
        elType = type(element)

        if elType in DefineShapeTags:
            element.shapeId = elId

        elif elType == DefineSpriteTag:
            element.spriteId = elId

        elif elType == DefineSoundTag:
            element.soundId = elId

        elif elType == DefineEditTextTag:
            element.characterID = elId

        elif elType == CSMTextSettingsTag:
            element.textID = elId

        elif elType == DefineFontTag:
            element.fontId = elId
            element.characterID = elId

        elif elType in DefineFontTags:
            element.fontID = elId

        elif elType == DefineFontNameTag:
            element.fontId = elId

        elif elType == DefineFontAlignZonesTag:
            element.fontID = elId

        elif elType in DefineBitsLosslessTags:
            element.characterID = elId

        element.setModified(True)

        return element

    def getElementId(self, element: object):
        elType = type(element)
        elId = -1

        if elType in DefineShapeTags:
            elId = element.shapeId

        elif elType == DefineSpriteTag:
            elId = element.spriteId

        elif elType == DefineSoundTag:
            elId = element.soundId

        elif elType == DefineEditTextTag:
            elId = element.characterID

        elif elType == CSMTextSettingsTag:
            elId = element.textID

        elif elType == DefineFontTag:
            elId = element.fontId

        elif elType in DefineFontTags:
            elId = element.fontID

        elif elType == DefineFontNameTag:
            elId = element.fontId

        elif elType == DefineFontAlignZonesTag:
            elId = element.fontID

        elif elType in DefineBitsLosslessTags:
            elId = element.characterID

        elId = int(elId)

        if elId > 0:
            return elId


class Swf(SwfUtils):
    swfPath: str
    swf: SWF

    elementsList: list          #[element, ...]
    elementsMap: dict           #{element: elId, ...}
    elementsMapByType: dict     #{elType: {elId: element, ...}, ...}
    symbolClass: SymbolClass

    def __init__(self, swfPath: str):
        if not os.path.exists(swfPath):
            raise FileDoesNotExist(f"File '{swfPath}' doesn't exist")

        self.init(swfPath)

    def init(self, swfPath: str):
        self.swfPath = swfPath
        self.swf = None

        self.elementsList = []
        self.elementsMap = {}
        self.elementsMapByType = {}
        self.symbolClass = None

    def load(self) -> SWF:
        fileStream = FileInputStream(self.swfPath)
        self.swf = SWF(BufferedInputStream(fileStream), True)
        fileStream.close()

        for element in self.swf.getTags():
            elType = type(element)
            elId = None

            if elType == SymbolClassTag:
                self.symbolClass = SymbolClass(element)
            else:
                elId = self.getElementId(element)
            
            if elId is not None:
                self.elementsList.append(element)

                self.elementsMap[element] = elId

                if elType not in self.elementsMapByType:
                    self.elementsMapByType[elType] = {}
                self.elementsMapByType[elType][elId] = element

        return self

    def close(self):
        if self.swf:
            self.swf.clearTagSwfs()
            self.swf.clearAllCache()

        self.init(self.swfPath)

    def save(self):
        if self.swf is not None:
            fileStream = FileOutputStream(self.swfPath)
            self.swf.saveTo(fileStream)
            fileStream.close()

    def getElementById(self, elId: int, elType=None, elTypes=[]):
        if elType:
            return self.elementsMapByType.get(ElementAnyToObject(elType), {}).get(elId, None)
        elif elTypes:
            for elType in elTypes:
                elements = self.elementsMapByType.get(ElementAnyToObject(elType), {})
                if elId in elements:
                    return elements[elId]
        else:
            for elType, elements in self.elementsMapByType.items():
                if elId in elements:
                    return elements[elId]

    def getElementTypeById(self, elId: int, elTypes=[]):
        if elTypes:
            for elType in elTypes:
                elType = ElementAnyToObject(elType)
                elements = self.elementsMapByType.get(elType, {})
                if elId in elements:
                    return elType
        else:
            for elType, elements in self.elementsMapByType.items():
                if elId in elements:
                    return elType 

    @property
    def AS3Packs(self):
        return self.swf.getAS3Packs()

    def addElement(self, element):
        self.swf.addTag(element)

        elId = self.getElementId(element)
        elType = ElementAnyToObject(element)

        self.elementsList.append(element)
        self.elementsMap[element] = elId
        if elType not in self.elementsMapByType:
            self.elementsMapByType[elType] = {}
        self.elementsMapByType[elType][elId] = element

    def replaceElement(self, oldElement, newElement):
        self.swf.replaceTag(oldElement, newElement)

    def removeElement(self, element):
        elId = self.getElementId(element)
        elType = ElementAnyToObject(element)

        self.swf.removeTag(element)

        self.elementsList.remove(element)
        self.elementsMap.pop(element)
        self.elementsMapByType[elType].pop(elId)
        


class SwfCreator(SwfUtils):
    swfPath: str

    def __init__(self, swfPath: str):
        self.init(swfPath)

    def init(self, swfPath: str):
        self.swfPath = swfPath

    def create(self):
        #Create swf file
        self.fileStream = FileOutputStream(self.swfPath)
        self.bufferedStream = BufferedOutputStream(self.fileStream)

        self.byteArrayStream = ByteArrayOutputStream()

        self.swfOutputStream = SWFOutputStream(self.byteArrayStream, 15)

        #Write head
        self.swfOutputStream.writeRECT(RECT(0, 0, 0, 0))
        self.swfOutputStream.writeFIXED8(24.0)
        self.swfOutputStream.writeUI16(1)

    def addElement(self, element):
        if type(element) == bytearray:
            self.swfOutputStream.write(element)
        else:
            element.writeTag(self.swfOutputStream)

    def save(self):
        #Write EndTag
        self.swfOutputStream.writeUI16(0x0000)

        #Save modifier
        byteArray = self.byteArrayStream.toByteArray()

        outputContentSwfStream = SWFOutputStream(self.bufferedStream, 15)
        outputContentSwfStream.write("FWS".encode())                                                #type
        outputContentSwfStream.write(15)                                                            #version
        outputContentSwfStream.writeUI32(outputContentSwfStream.getPos() + byteArray.length + 4)    #size
        outputContentSwfStream.write(byteArray)                                                     #data
        self.bufferedStream.flush()

        self.fileStream.close()

        self.fileStream = None
        self.bufferedStream = None
        self.byteArrayStream = None
        self.swfOutputStream = None


