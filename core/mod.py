import os, json, hashlib, time, zipfile
from typing import List, Dict
from . import MODS_PATH
from . import Sql
from .utils.localConfig import ModsConfig
from .utils.exceptions import ModResourcesNotFound, ModFolderDoesNotExist, ModNotBuilded, ModifierDoesNotExist
from .utils.imports import *
from .utils.elementTypes import ElementStrToObject, ElementObjectToStr, ElementAnyToStr
from .utils.gameconstants import BRAWLHALLA_PATH, BRAWLHALLA_SWFS, BRAWLHALLA_FILES
from .utils.swf import Swf
from .modifier import MODIFIER_FORMAT, Modifier, ModifierTemplate, ModifierCreator
from .file import FILES_PACK, FilesPack



PLATFORMS = {
    0: None,
    1: "GameBanana",
    2: "BHMods"
}

RESOURCE_ELEMENT_FORMAT = ".bmlswf"

MOD_DATABASE_FILE = "index.db"
MOD_TABLE_CONFIGURATION = "Configuration"
MOD_TABLE_CONFIGURATION_STRUCTURE = {
    "key": str,
    "value": str
}

MOD_TABLE_MODIFIER  = "Modifiers"
MOD_TABLE_MODIFIER_NAME     = "name"
MOD_TABLE_MODIFIER_ELEMENTS = "elements"
MOD_TABLE_MODIFIER_STRUCTURE = {
    MOD_TABLE_MODIFIER_NAME:     str,
    MOD_TABLE_MODIFIER_ELEMENTS: str
}

MOD_TABLE_FILES = "Files"
MOD_TABLE_FILES_NAME = "name"
MOD_TABLE_FILES_PATH = "path"
MOD_TABLE_FILES_HASH = "hash"
MOD_TABLE_FILES_STRUCTURE = {
    MOD_TABLE_FILES_NAME: str,
    MOD_TABLE_FILES_PATH: str,
    MOD_TABLE_FILES_HASH: str
}

class ModifierFlag:
    pass
class FileFlag:
    pass


class Mod:
    modPath: str
    modifierList: List[ModifierTemplate]
    filesPack: FilesPack

    GHOST_MOD: bool

    #Mod config
    gameVersion: str
    modName: str
    modAuthor: str
    modVersion: str
    modDescription: str
    modTags: list
    modPreview: str
    modId: str
    modHash: str
    authorId: str
    platform: str

    def __init__(self, modFolder: str=None, modJson: dict=None):
        self.GHOST_MOD = bool(modJson)

        if self.GHOST_MOD:
            self.modPath = None
            self.modFolder = None

            self.modifierList = []
            self.filesPack = FilesPack(None)

            self.loadConfig(modJson[MOD_TABLE_CONFIGURATION])

            for modifier in modJson[MOD_TABLE_MODIFIER]:
                self.modifierList.append(ModifierTemplate(mod=self, swfName=modifier[MOD_TABLE_MODIFIER_NAME], elements=modifier[MOD_TABLE_MODIFIER_ELEMENTS]))
                self.filesPack = FilesPack(None)

            for file in modJson[MOD_TABLE_FILES]:
                    self.filesPack.addFile(file[MOD_TABLE_FILES_NAME], file[MOD_TABLE_FILES_PATH], file[MOD_TABLE_FILES_HASH])

        else:
            self.modPath = os.path.join(MODS_PATH, modFolder)
            self.modFolder = modFolder

            if not os.path.exists(self.modPath):
                raise ModFolderDoesNotExist(f"Mod folder '{modFolder}' doesn't exist")

            if not os.path.exists(os.path.join(self.modPath, MOD_DATABASE_FILE)):
                raise ModNotBuilded(f"Mod '{modFolder}' not builded")

            self.modifierList = []
            self.filesPack = FilesPack(self.modPath)

            #Open index.db
            with Sql(os.path.join(self.modPath, MOD_DATABASE_FILE)) as index:
                self.loadConfig({cfg["key"]:cfg["value"] for cfg in index.read(MOD_TABLE_CONFIGURATION)})

                #Load modifiers
                for modifier in index.read(MOD_TABLE_MODIFIER):
                    if not os.path.exists(os.path.join(self.modPath, f"{modifier[MOD_TABLE_MODIFIER_NAME]}.{MODIFIER_FORMAT}")):
                        raise ModifierDoesNotExist(f"Modifier '{modifier[MOD_TABLE_MODIFIER_NAME]}.{MODIFIER_FORMAT}' doesn't exist")

                    self.modifierList.append(Modifier(self, modifier[MOD_TABLE_MODIFIER_NAME], json.loads(modifier[MOD_TABLE_MODIFIER_ELEMENTS])))

                #Load files
                for file in index.read(MOD_TABLE_FILES):
                    self.filesPack.addFile(file[MOD_TABLE_FILES_NAME], file[MOD_TABLE_FILES_PATH], file[MOD_TABLE_FILES_HASH])

    def loadConfig(self, config):
        for key, value in config.items():
            if key == "modTags" and not self.GHOST_MOD:
                setattr(self, key, json.loads(config["modTags"]))
            else:
                setattr(self, key, value)

    def __repr__(self):
        if self.GHOST_MOD:
            return f"<Ghost Mod: {self.modName}>"
        else:
            return f"<Mod: {self.modFolder}>"

    def __str__(self):
        return self.__repr__()

    def exportToJson(self):
        export = {
            MOD_TABLE_CONFIGURATION: {
                "gameVersion": self.gameVersion,
                "modName": self.modName,
                "modAuthor": self.modAuthor,
                "modVersion": self.modVersion,
                "modDescription": self.modDescription,
                "modTags": self.modTags,
                "modPreview": None,
                "modId": self.modId,
                "modHash": self.modHash,
                "authorId": self.authorId,
                "platform": self.platform
            },
            MOD_TABLE_MODIFIER: [
                {
                    MOD_TABLE_MODIFIER_NAME: modifier.swfName,
                    MOD_TABLE_MODIFIER_ELEMENTS: modifier.jsonElements
                }
                
                for modifier in self.modifierList
            ],
            MOD_TABLE_FILES: [
                {
                    MOD_TABLE_FILES_NAME: file.fileName,
                    MOD_TABLE_FILES_PATH: file.filePath,
                    MOD_TABLE_FILES_HASH: file.fileHash
                }
                for file in self.filesPack
            ]

        }

        return export



class ModBuilder:
    modPath: str
    modifierResources: dict
    files: dict

    def __init__(self, modFolder):
        self.modPath = os.path.join(MODS_PATH, modFolder)

        if not os.path.exists(self.modPath):
            raise ModFolderDoesNotExist(f"Mod folder '{modFolder}' doesn't exist")

        self.modifierResources = []
        self.files = {}

        for n, (path, folders, files) in enumerate(os.walk(self.modPath)):
            if n == 0:
                self.modifierResources = {
                    folder.replace(".swf", ""):os.path.join(self.modPath, folder)
                    for folder in folders
                    if folder.replace(".swf", "")+".swf" in BRAWLHALLA_SWFS and folder.replace(".swf", "") != "BrawlhallaAir"
                }
            
            else:
                for file in files:
                    if file in BRAWLHALLA_FILES:
                        self.files[os.path.join(path.replace(self.modPath+"\\", ""), file)] = file

        if not self.modifierResources and not self.files:
            raise ModResourcesNotFound()

    def setConfiguration(
                            self, 
                            gameVersion: str, 
                            modName: str, 
                            modAuthor: str, 
                            modVersion: str="0.1", 
                            modDescription: str=None, 
                            modTags: List[str]=[],
                            modPreview: str=None,
                            modId: str=None,
                            authorId: str=None,
                            platform: int=0
                        ):

        config = {
            "gameVersion": gameVersion,
            "modName": modName,
            "modAuthor": modAuthor,
            "modVersion": modVersion,
            "modDescription": modDescription,
            "modTags": json.dumps(modTags),
            "modPreview": modPreview,
            "modId": modId,
            "authorId": authorId,
            "platform": PLATFORMS[platform]
        }

        #Create index.db (mod data)
        with Sql(os.path.join(self.modPath, MOD_DATABASE_FILE)) as index:
            indexTables = index.tables()

            #Create config table
            if MOD_TABLE_CONFIGURATION not in indexTables:
                index.create(MOD_TABLE_CONFIGURATION, MOD_TABLE_CONFIGURATION_STRUCTURE)
                config["modHash"] = hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]

            #Create mod modifiers table
            if MOD_TABLE_MODIFIER not in indexTables:
                index.create(MOD_TABLE_MODIFIER, MOD_TABLE_MODIFIER_STRUCTURE)

            #Create mod files table
            if MOD_TABLE_FILES not in indexTables:
                index.create(MOD_TABLE_FILES, MOD_TABLE_FILES_STRUCTURE)

            #Write/Update config table
            for key, value in config.items():
                if index.search(MOD_TABLE_CONFIGURATION, {"key": key}):
                    index.update(MOD_TABLE_CONFIGURATION, {"key": key}, {"key": key, "value": value}, False)
                else:
                    index.add(MOD_TABLE_CONFIGURATION, {"key": key, "value": value}, False)

            index.save()

    def _build(self):
        indexModifiersElements = {}
        output = []

        for swfName, modifierResourcesPath in self.modifierResources.items():
            indexModifiersElements[swfName] = {}
            modifierElements = indexModifiersElements[swfName]

            mdcr = ModifierCreator(self.modPath, swfName)

            #Find Modifier elements
            elementFiles = []
            scriptFiles = []
            for element_folder in os.listdir(modifierResourcesPath):
                if element_folder in ["shapes", "morphshapes", "sprites", "fonts", "texts", "sounds", "images"]:
                    elementFiles += [
                                    os.path.join(modifierResourcesPath, element_folder, element) 
                                    for element in os.listdir(os.path.join(modifierResourcesPath, element_folder))
                                    if element.endswith(RESOURCE_ELEMENT_FORMAT)
                                ]
                elif element_folder in ["scripts"]:
                    scriptFiles += [
                                    os.path.join(modifierResourcesPath, element_folder, element) 
                                    for element in os.listdir(os.path.join(modifierResourcesPath, element_folder))
                                    if element.endswith(".as")
                                ]

            #Open .bmlswf's and write its elements to .bmlmodifier
            for elementPath in elementFiles:
                elementSwf = Swf(elementPath)
                elementSwf.load()

                #New element id by file name
                newElId = int(elementPath.rsplit("\\", 1)[1].replace(RESOURCE_ELEMENT_FORMAT, ""))
                for element in elementSwf.elementsList:
                    strElType = ElementObjectToStr(element)
                    elId = elementSwf.getElementId(element)

                    if elId != newElId:
                        elementSwf.setElementId(element, newElId)

                    mdcr.addElement(element)

                    if strElType not in modifierElements:
                        modifierElements[strElType] = []
                    modifierElements[strElType].append(elId)

                elementSwf.close()

            #Write scripts to .bmlmodifier
            for scriptFile in scriptFiles:
                with open(scriptFile, "r") as script:
                    strElType = ElementObjectToStr(ActionScriptTag)
                    scriptName = scriptFile.rsplit("\\", 1)[1].replace(".as", "")

                    mdcr.addAS(scriptName, script.read())

                    if strElType not in modifierElements:
                        modifierElements[strElType] = []
                    modifierElements[strElType].append(scriptName)

            mdcr.save()

            yield ModifierFlag, mdcr.swfName

        indexFiles = {}
        indexFilesHashes = {}
        if self.files:
            #Create files.zip
            with zipfile.ZipFile(os.path.join(self.modPath, FILES_PACK), "w") as filesZip:
                for filePath, fileName in self.files.items():
                    #Add mod files to files.zip
                    with open(os.path.join(self.modPath, filePath), "rb") as file:
                        path = BRAWLHALLA_FILES[fileName].replace(BRAWLHALLA_PATH+"\\", "")
                        indexFiles[fileName] = path
                        fileData = file.read()
                        filesZip.writestr(path, fileData)
                        indexFilesHashes[fileName] = hashlib.sha256(fileData).hexdigest()[:16]

                    yield FileFlag, os.path.join(self.modPath, filePath)

        #Write mod elements to index.db
        with Sql(os.path.join(self.modPath, MOD_DATABASE_FILE)) as index:
            for name, elements in indexModifiersElements.items():
                if index.search(MOD_TABLE_MODIFIER, {MOD_TABLE_MODIFIER_NAME: name}):
                    index.update(MOD_TABLE_MODIFIER, {MOD_TABLE_MODIFIER_NAME: name}, {MOD_TABLE_MODIFIER_ELEMENTS: json.dumps(elements)}, False)
                else:
                    index.add(MOD_TABLE_MODIFIER, {MOD_TABLE_MODIFIER_NAME: name, MOD_TABLE_MODIFIER_ELEMENTS: json.dumps(elements)}, False)

            for modifier in index.read(MOD_TABLE_MODIFIER):
                if modifier[MOD_TABLE_MODIFIER_NAME] not in indexModifiersElements:
                    index.delete(MOD_TABLE_MODIFIER, modifier, False)

            #Add new files
            for fileName, path in indexFiles.items():
                if index.search(MOD_TABLE_FILES, {MOD_TABLE_FILES_NAME: fileName}):
                    index.update(MOD_TABLE_FILES, {MOD_TABLE_FILES_NAME: fileName}, {MOD_TABLE_FILES_PATH: path, MOD_TABLE_FILES_HASH: indexFilesHashes[fileName], MOD_TABLE_FILES_HASH: indexFilesHashes[fileName]}, False)
                else:
                    index.add(MOD_TABLE_FILES, {MOD_TABLE_FILES_NAME: fileName, MOD_TABLE_FILES_PATH: path, MOD_TABLE_FILES_HASH: indexFilesHashes[fileName]}, False)

            #Remove not-exist files
            for file in index.read(MOD_TABLE_FILES):
                if file[MOD_TABLE_FILES_NAME] not in indexFiles:
                    index.delete(MOD_TABLE_FILES, file, False)

            index.save()

    def build(self, generator=False):
        if generator:
            return self._build()
        else:
            return [n for n in self._build()]



class ModsFinder:
    mods: List[Mod]
    modsMap: Dict[str, Mod]

    def __init__(self):
        self.mods = []
        self.modsMap = {}
        self()

    def __call__(self):
        for folder in os.listdir(MODS_PATH):
            try:
                mod = Mod(folder)
                self.mods.append(mod)
                self.modsMap[mod.modHash] = mod

                if mod.modHash not in ModsConfig.JsonMods:
                    ModsConfig.JsonMods = {**ModsConfig.JsonMods, mod.modHash:mod.exportToJson()}

            except ModNotBuilded:
                pass

        for modHash, modJson in ModsConfig.JsonMods.items():
            if modHash in self.modsMap: continue

            mod = Mod(modJson=modJson)
            self.mods.append(mod)
            self.modsMap[mod.modHash] = mod

        for modHash in self.modsMap:
            if modHash in ModsConfig.JsonMods: continue
            mod = self.modsMap.pop(self.modsMap)
            self.mods.remove(mod)




#md = Mod("ModFolderBlaBla")
#print(md)
#print(md.filesPack.files[0].repairOrig())


#mb = ModBuilder("ModFolderBlaBla")
#mb.setConfiguration("4.08", "Popa", "Fabriziog")

#for l in mb.generator_build():
#    print(l)

#print(mb.build())

