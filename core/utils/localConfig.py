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