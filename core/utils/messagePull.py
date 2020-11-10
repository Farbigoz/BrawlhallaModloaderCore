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

class MessagePull:
    messageList = []
    
    #def __init__(self):
    #    self.messageList = []

    def __init__(self, element):
        self.messageList.append(element)

    def __call__(self, element):
        self.messageList.append(element)

    def __repr__(self):
        return f"<OutputPull: {str(self.messageList)}>"

    def __str__(self):
        return self.__repr__()

    def get(self):
        if self.messageList:
            return self.messageList.pop(0)

class MessagePollClassParent:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __eq__(self, other):
        return self.__class__ == other

    def __repr__(self):
        return f"{self.__class__.__name__}{str(self.args)}"

    def __str__(self):
        return "\n".join(self.args)


class ModConfigurationSet(MessagePollClassParent):
    pass


class DoneCreateIndexDatabase(MessagePollClassParent):
    pass

class StartCreateModifier(MessagePollClassParent):
    pass

class AddElementToModifier(MessagePollClassParent):
    pass

class DoneCreateModifier(MessagePollClassParent):
    pass

class DoneWriteModifiersToIndexDatabase(MessagePollClassParent):
    pass


class ModConflict(MessagePollClassParent):
    pass