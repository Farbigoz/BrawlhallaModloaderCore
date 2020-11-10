import jpype, os
from jpype import JClass, JString, JInt

FFDEC_LIB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "libs/ffdec_lib.jar"))

# Run JVM
jpype.startJVM(classpath=[FFDEC_LIB_PATH])

# Java
ArrayList = JClass('java.util.ArrayList')
FileInputStream = JClass('java.io.FileInputStream')
FileOutputStream = JClass('java.io.FileOutputStream')
BufferedInputStream = JClass('java.io.BufferedInputStream')
BufferedOutputStream = JClass('java.io.BufferedOutputStream')
ByteArrayOutputStream = JClass('java.io.ByteArrayOutputStream')

# FFDEc_lib
#  Swf
SWF = JClass('com.jpexs.decompiler.flash.SWF')
SWFHeader = JClass('com.jpexs.decompiler.flash.SWFHeader')
SWFOutputStream = JClass('com.jpexs.decompiler.flash.SWFOutputStream')

Configuration = JClass('com.jpexs.decompiler.flash.configuration.Configuration')
HighlightedTextWriter = JClass('com.jpexs.decompiler.flash.helpers.HighlightedTextWriter')
ScriptExportMode = JClass('com.jpexs.decompiler.flash.exporters.modes.ScriptExportMode')

As3ScriptReplacerFactory = JClass('com.jpexs.decompiler.flash.importers.As3ScriptReplacerFactory')

#  Types
RECT = JClass('com.jpexs.decompiler.flash.types.RECT')
FILLSTYLE = JClass('com.jpexs.decompiler.flash.types.FILLSTYLE')

#  Tags
DefineBitsLosslessTag = JClass('com.jpexs.decompiler.flash.tags.DefineBitsLosslessTag')
DefineBitsLossless2Tag = JClass('com.jpexs.decompiler.flash.tags.DefineBitsLossless2Tag')
DefineBitsLosslessTags = [
    DefineBitsLosslessTag, 
    DefineBitsLossless2Tag
]
DefineShapeTag = JClass('com.jpexs.decompiler.flash.tags.DefineShapeTag')
DefineShape2Tag = JClass('com.jpexs.decompiler.flash.tags.DefineShape2Tag')
DefineShape3Tag = JClass('com.jpexs.decompiler.flash.tags.DefineShape3Tag')
DefineShape4Tag = JClass('com.jpexs.decompiler.flash.tags.DefineShape4Tag')
DefineShapeTags = [
    DefineShapeTag,
    DefineShape2Tag,
    DefineShape3Tag,
    DefineShape4Tag
]
DefineFontTag = JClass('com.jpexs.decompiler.flash.tags.DefineFontTag')
DefineFont2Tag = JClass('com.jpexs.decompiler.flash.tags.DefineFont2Tag')
DefineFont3Tag = JClass('com.jpexs.decompiler.flash.tags.DefineFont3Tag')
DefineFont4Tag = JClass('com.jpexs.decompiler.flash.tags.DefineFont4Tag')
DefineFontTags = [
    DefineFontTag,
    DefineFont2Tag,
    DefineFont3Tag,
    DefineFont4Tag
]
DefineSpriteTag = JClass('com.jpexs.decompiler.flash.tags.DefineSpriteTag')
DefineSoundTag = JClass('com.jpexs.decompiler.flash.tags.DefineSoundTag')
DefineEditTextTag = JClass('com.jpexs.decompiler.flash.tags.DefineEditTextTag')
CSMTextSettingsTag = JClass('com.jpexs.decompiler.flash.tags.CSMTextSettingsTag')
DefineFontNameTag = JClass('com.jpexs.decompiler.flash.tags.DefineFontNameTag')
DefineFontAlignZonesTag = JClass('com.jpexs.decompiler.flash.tags.DefineFontAlignZonesTag')
SymbolClassTag = JClass('com.jpexs.decompiler.flash.tags.SymbolClassTag')
class ActionScriptTag:
    pass