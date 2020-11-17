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

__author__ = "Farbigoz"
__version__ = "0.1"




LOCAL_DATA_FOLDER = "BrawlhallaModloader"
MODS_PATH = "Mods"

import os
def _CreateModFolder():
    global MODS_PATH
    if not os.path.exists(MODS_PATH):
        os.makedirs(MODS_PATH)

def SetModsPath(path: str):
    global MODS_PATH
    MODS_PATH = path
    _CreateModFolder()

_CreateModFolder()

from .libs.sqlite import Sql
from .libs.config_file import ConfigFile, ConfigElement
from .utils import *
from .file import *
from .modifier import *
from .mod import *
from .processor import Processor
