class TypeInfo(object):
    typeName: str

    def __init__(self, typeName: str) -> None:
        super().__init__()
        self.typeName = typeName

    def GetTypeName(self) -> str:
        return self.typeName

    def GetImportFrom(self) -> str:
        return ""


class SchemaBase(object):
    typeName: str

    def __init__(self, typeName: str) -> None:
        super().__init__()
        self.typeName = typeName

    def GetTypeName(self) -> str:
        return self.typeName
