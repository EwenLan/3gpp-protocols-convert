leadingDigitInsertion = "E"


def TransformIdentifier(enumValue: str) -> str:
    ans: str = enumValue.replace("_", " ").title().replace(
        " ", "").replace("-", "_")
    if ans[0].isdigit():
        ans = leadingDigitInsertion + ans
    return ans


def ConvertFilename(filename: str) -> str:
    return ".".join(filename.split(".")[:-1]) + ".ts"
