import os, json
from typing import Dict, List
from .utils.imports import FILLSTYLE, DefineShapeTags
from .utils.swf import Swf, SwfCreator
from .utils.symbolclass import SymbolClass
from .utils.elementTypes import ElementAnyToObject, ElementObjectToStr

MODIFIER_FORMAT = "bmlmodifier"

SYMBOL_CLASS_TAG_IS_MODIFIER        = 0xffff
SYMBOL_CLASS_TAG_ACTION_SCRIPTS     = 0xfffe
SYMBOL_CLASS_TAG_REPEATING_BEATMAPS = 0xfffd

__all__ = ["MODIFIER_FORMAT", "ModifierTemplate", "Modifier", "ModifierCreator"]

class ModifierTemplate:
    swfName: str
    elements: Dict[str, List[int]]  #{elType: [elId, ...], ...}
    modHash: str
    modPath: str
    modifierPath: str
    mod: object

    actionScripts: Dict[str, str]
    repeatingBeatmaps: Dict[int, int]

    def __init__(self, swfName: str, elements: Dict[str, List[int]]=None, modHash: str=None, modPath: str=None, mod: object=None):
        self.swfName = swfName.replace(".swf", "")
        self.elements = {ElementAnyToObject(elType):ids for elType, ids in elements.items()} if elements is not None else None
        self.modHash = modHash
        self.modPath = modPath
        self.modifierPath = os.path.join(self.modPath, f"{self.swfName}.{MODIFIER_FORMAT}") if self.modPath else None
        self.mod = mod

        self.actionScripts = {}         #{scriptName: content, ...}
        self.repeatingBeatmaps = {}     #{shapeId: imageId, ...}

    def clearCache(self):
        self.actionScripts = {}         #{scriptName: content, ...}
        self.repeatingBeatmaps = {}     #{shapeId: imageId, ...}

    def __repr__(self):
        return f"<Modifier: {self.swfName}>"

    def __str__(self):
        return self.__repr__()

    @property
    def jsonElements(self):
        return {ElementObjectToStr(elType):elements for elType, elements in self.elements.items()}


class Modifier(ModifierTemplate, Swf):
    def __init__(self, mod: object, swfName: str, elements: Dict[str, List[int]]=None):
        super().__init__(mod=mod, modPath=mod.modPath, swfName=swfName, elements=elements, modHash=mod.modHash)
        super().init(swfPath=self.modifierPath)

    def load(self):
        super().load()

        if bool(self.symbolClass.getTag(SYMBOL_CLASS_TAG_IS_MODIFIER)):
            self.actionScripts = self.symbolClass.getTag(SYMBOL_CLASS_TAG_ACTION_SCRIPTS)
            self.repeatingBeatmaps = self.symbolClass.getTag(SYMBOL_CLASS_TAG_REPEATING_BEATMAPS)

            #fix var's
            self.repeatingBeatmaps = {int(old):int(new) for old, new in self.repeatingBeatmaps.items()}
        
        return self

    def close(self):
        super().close()
        self.clearCache()


class ModifierCreator(ModifierTemplate, SwfCreator):
    def __init__(self, modPath: str, swfName: str):
        swfName = swfName.replace(".swf", "").replace(MODIFIER_FORMAT, "")
        super().__init__(swfName=swfName, modPath=modPath)
        self.init(swfPath=self.modifierPath)

        self.create()

    def addElement(self, element):
        super().addElement(element)

        if type(element) in DefineShapeTags:
            for fillStyle in element.getShapes().fillStyles.fillStyles:
                if fillStyle.fillStyleType == FILLSTYLE.REPEATING_BITMAP:
                    self.repeatingBeatmaps[self.getElementId(element)] = fillStyle.bitmapId

    def addAS(self, name, content):
        self.actionScripts[name] = content

    def save(self):
        #Create SymbolClass
        symbolCls = SymbolClass()

        symbolCls.addTag(SYMBOL_CLASS_TAG_IS_MODIFIER, True)
        symbolCls.addTag(SYMBOL_CLASS_TAG_ACTION_SCRIPTS, self.actionScripts)
        symbolCls.addTag(SYMBOL_CLASS_TAG_REPEATING_BEATMAPS, self.repeatingBeatmaps)
        
        super().addElement(symbolCls.getByteArray())

        super().save()

        self.clearCache()
