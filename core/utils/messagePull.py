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