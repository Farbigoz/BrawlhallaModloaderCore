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

from .imports import *

__all__ = ["ElementStrToObject", "ElementObjectToStr"]

_types = {
    "DefineBitsLosslessTag": DefineBitsLosslessTag,
    "DefineBitsLossless2Tag": DefineBitsLossless2Tag,
    "DefineShapeTag": DefineShapeTag,
    "DefineShape2Tag": DefineShape2Tag,
    "DefineShape3Tag": DefineShape3Tag,
    "DefineShape4Tag": DefineShape4Tag,
    "DefineFontTag": DefineFontTag,
    "DefineFont2Tag": DefineFont2Tag,
    "DefineFont3Tag": DefineFont3Tag,
    "DefineFont4Tag": DefineFont4Tag,
    "DefineSpriteTag": DefineSpriteTag,
    "DefineSoundTag": DefineSoundTag,
    "DefineEditTextTag": DefineEditTextTag,
    "CSMTextSettingsTag": CSMTextSettingsTag,
    "DefineFontNameTag": DefineFontNameTag,
    "DefineFontAlignZonesTag": DefineFontAlignZonesTag,
    "SymbolClassTag": SymbolClassTag,
    "ActionScriptTag": ActionScriptTag
}
_types = {**_types, **{v:k for k,v in _types.items()}}


def ElementStrToObject(elType: str) -> object:
    """
    Convert Element name to Element class
    """
    return _types.get(elType, None)


def ElementObjectToStr(elType: object) -> str:
    """
    Convert Element class to Element name
    """
    return _types.get(elType, None) or _types.get(type(elType), None)


def ElementAnyToObject(elType: object) -> object:
    """
    Convert Element class or Element name to Element class
    """
    if type(elType) == str:
        return ElementStrToObject(elType)
    elif elType not in _types:
        return type(elType)
    else:
        return elType


def ElementAnyToStr(elType: object) -> str:
    """
    Convert Element class or Element name to Element name
    """
    if type(elType) == str:
        return elType
    else:
        return ElementObjectToStr(elType)
