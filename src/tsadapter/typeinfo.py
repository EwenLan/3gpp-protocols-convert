from abc import abstractclassmethod
import typing


class TsType:
    importFrom: str
    typeName: str

    def __init__(self, importFrom: str, typeName: str) -> None:
        self.importFrom = importFrom
        self.typeName = typeName

    def GetImportFrom(self) -> str:
        return self.importFrom

    def GetTypeName(self) -> str:
        return self.typeName


class TsTypeInfo(object):
    @abstractclassmethod
    def ToString(self) -> str:
        return ""

    @abstractclassmethod
    def GetTypeList(self) -> typing.List[TsType]:
        return []


class TsSingleTypeInfo(TsTypeInfo):
    elementaryType: TsType

    def __init__(self, elementaryType: TsType) -> None:
        self.elementaryType = elementaryType

    def GetTypeList(self) -> typing.List[TsType]:
        return [self.elementaryType]


class TsSimpleTypeInfo(TsSingleTypeInfo):
    def ToString(self) -> str:
        return self.originType.GetTypeName()


class TsArrayTypeInfo(TsSingleTypeInfo):
    def ToString(self) -> str:
        return "{}[]".format(self.elementType.GetTypeName())


class TsMapTypeInfo(TsTypeInfo):
    mapFromType: TsType
    mapToType: TsType

    def __init__(self, mapFromType: TsType, mapToType: TsType) -> None:
        self.mapFromType = mapFromType
        self.mapToType = mapToType

    def ToString(self) -> str:
        return "{{ [key: {}]: {} }}".format(self.mapFromType.GetTypeName(), self.mapToType.GetTypeName())

    def GetTypeList(self) -> typing.List[TsType]:
        return [self.mapFromType, self.mapToType]
