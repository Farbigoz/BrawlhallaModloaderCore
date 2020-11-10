# Brawlhalla Modloader Core ![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)

**Brawlhalla Modloader Core** - A tool for building, installing and uninstalling various modifications for Brawlhalla.

## Required libraries

    $ pip install JPype1

## Wiki

* [How create mod for Modloader]()

## Examples

Mods\ModFolderName

### Build mod

```python
import core

mod = core.ModBuilder("ModFolderName")
mod.setConfiguration(gameVersion='4.08', modName="MapBackgrounds", modAuthor="Farbigoz")
mod.build()
```


### Install mod

```python
import core

mod = core.Mod("ModFolderName")

processor = core.Processor()
processor.addModsToInstall(mod)
processor.process()
```

### Uninstall mod

```python
import core

mod = core.Mod("ModFolderName")

processor = core.Processor()
processor.addModsToUninstall(mod)
processor.process()
```

### Find mods

```python
import core

finder = core.ModsFinder()
print(finder.mods)
finder() #Find again
print(finder.mods)
```

## Licenses

Brawlhalla Modloader Core is licensed with GNU GPL v3, see the [license.txt](license.txt).
It uses modified code of these libraries:

* [FFDec Library](https://github.com/jindrapetrik/jpexs-decompiler) - LGPLv3
