from .imports import JInt, JString
from .exceptions import SymbolClassTagAlreadyExist, SymbolClassTagDoesNotExist
import json
from typing import Union

JSON_FLAG   = "!json"
TRUE_FLAG   = "!true"
FALSE_FLAG  = "!false"
NONE_FLAG   = "!null"

class ByteArray:
    def __init__(self):
        self.data = bytearray()

    def _normalize_data(self, data):
        if type(data) == self.__class__:
            return data.data
        else:
            return data

    def writeUI32(self, data):
        data = self._normalize_data(data)

        self.data.append(data & 0xff)
        self.data.append((data >> 8) & 0xff)
        self.data.append((data >> 16) & 0xff)
        self.data.append((data >> 24) & 0xff)

    def writeUI16(self, data):
        data = self._normalize_data(data)

        self.data.append(data & 0xff)
        self.data.append((data >> 8) & 0xff)

    def writeUI8(self, data):
        data = self._normalize_data(data)

        self.data.append(data & 0xff)

    def write(self, data):
        data = self._normalize_data(data)

        for _elem in data:
            self.data.append(_elem)

    def __len__(self):
        return len(self.data)

class SymbolClass():
    tags: dict
    headerTagId: int = 0x133f

    def __init__(self, symbolClassTag=None):
        self.symbolClass = symbolClassTag
        self.tags = {}

        if self.symbolClass is not None:
            for tag, name in dict(self.symbolClass.getTagToNameMap()).items():
                self.tags[int(tag)] = self._str_to_object(tag, name)

    def __contains__(self, item):
        return item in self.tags

    def __getitem__(self, key):
        return self.tags[key]

    def _str_to_object(self, tag: int, name: str) -> Union[dict, list, bool, None, str]:
        tag = str(tag)
        obj = str(name)

        if obj.startswith(tag):
            obj = obj.replace(tag, "")
            if obj.startswith(JSON_FLAG):
                obj = json.loads(obj.replace(JSON_FLAG, ""))
            elif obj.startswith(TRUE_FLAG):
                obj = True
            elif obj.startswith(FALSE_FLAG):
                obj = False
            elif obj.startswith(NONE_FLAG):
                obj = None
        
        return obj

    def _object_to_str(self, tag: int, obj: Union[dict, list, bool, None, str]) -> str:
        tag = str(tag)
        name = str(obj)

        if type(obj) in [dict, list]:
            name = tag+JSON_FLAG+json.dumps(obj)
        elif obj == True:
            name = tag+TRUE_FLAG
        elif obj == False:
            name = tag+FALSE_FLAG
        elif obj == None:
            name = tag+NONE_FLAG

        return name

    def getNextTagId(self) -> int:
        return len(self.tags)

    def addTag(self, tag: int, name: object) -> None:
        if tag in self.tags: raise SymbolClassTagAlreadyExist("This tag already exists")
        self.tags[int(tag)] = name

    def setTag(self, tag: int, name: object) -> None:
        if tag not in self.tags: raise SymbolClassTagDoesNotExist("This tag does not exist")
        self.tags[int(tag)] = name

    def getTag(self, tag: int) -> object:
        return self.tags.get(int(tag), None)

    def getByteArray(self, reverse=True) -> bytearray:
        if self.symbolClass is not None:
            self.save()
            content = bytearray(self.symbolClass.getData())

        else:
            content = ByteArray()
            content.writeUI16(len(self.tags))

            for tag in sorted(list(self.tags), reverse=reverse):
                content.writeUI16(tag)
                content.write(self._object_to_str(tag, self.tags[tag]).encode())
                content.writeUI8(0x00)

        symbolClass = ByteArray()
        symbolClass.writeUI16(self.headerTagId)
        symbolClass.writeUI32(len(content))
        symbolClass.write(content)
        
        return symbolClass.data

    def save(self, reverse=True):
        if self.symbolClass is not None:
            self.symbolClass.tags.clear()
            self.symbolClass.names.clear()

            for tag in sorted(list(self.tags), reverse=reverse):
                self.symbolClass.tags.add(JInt(tag))
                self.symbolClass.names.add(JString(self._object_to_str(tag, self.tags[tag])))

            self.symbolClass.setModified(True)
