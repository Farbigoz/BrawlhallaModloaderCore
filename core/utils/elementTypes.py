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
