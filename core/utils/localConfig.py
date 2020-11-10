from .. import LOCAL_DATA_FOLDER
from .. import ConfigFile, ConfigElement
import os
from sys import platform

if platform in ["win32", "win64"]:
    LOCAL_DATA_PATH = os.path.join(os.getenv("APPDATA"), LOCAL_DATA_FOLDER)

    if LOCAL_DATA_FOLDER not in os.listdir(os.getenv("APPDATA")):
        os.mkdir(LOCAL_DATA_PATH)




CoreConfigFile = "core.cfg"

class CoreConfigMap(ConfigFile):
    BrawlhallaAirHash = ConfigElement()
    BrawlhallaVersion = ConfigElement()


CoreConfig = CoreConfigMap(os.path.join(LOCAL_DATA_PATH, CoreConfigFile))



ModsConfigFile = "mods.cfg"

class ModsConfigMap(ConfigFile):
    ModifiedFiles = ConfigElement(default={})
    OriginalFiles = ConfigElement(default={})

    JsonMods = ConfigElement(default={})
    InstalledMods = ConfigElement(default=[])

ModsConfig = ModsConfigMap(os.path.join(LOCAL_DATA_PATH, ModsConfigFile))