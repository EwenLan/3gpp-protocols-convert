from common import ConvertFilename
import schemasreader
from log import Log
from tsadapter.tsadapter import TsAdapter
from yamlreader import YamlReader
import os

log = Log(__name__).getLogger()


if __name__ == "__main__":
    inputFilePath = "protocols\\29503-h50\\TS29503_Nudm_UECM.yaml"
    outputDirectory = "output"
    outputFilename = ConvertFilename(os.path.basename(inputFilePath))
    outputPath = os.path.join(outputDirectory, outputFilename)
    inputContent = YamlReader(inputFilePath)
    schemas = schemasreader.Schemas(
        schemasreader.GetSchemasPart(inputContent.GetDictContent()))
    tsFile = TsAdapter()
    for i in schemas.simpleTypeSchemas:
        tsFile.AddSimpleTypeDefine(i.typeName, i.originType)
    for i in schemas.enumTypeSchemas:
        tsFile.AddEnumTypeDefine(i.typeName, i.enumValue)
    for i in schemas.objectTypeSchemas:
        tsFile.AddObjectTypeDefine(i.typeName, i.properties)
    for i in schemas.arrayTypeSchemas:
        tsFile.AddArrayTypeDefine(i.typeName, i.elementType.GetTypeName())
    tsFile.Save(outputPath)
