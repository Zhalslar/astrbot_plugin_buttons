def is_hex_string(s: str) -> bool:
    """判断是否为合法的十六进制字符串"""
    if len(s) % 2 != 0:
        return False
    return all(c in "0123456789abcdefABCDEF" for c in s)


def process_json(data, path=None):
    """递归处理 JSON 中的 hex->xx 字符串"""
    if path is None:
        path = []

    if isinstance(data, dict):
        return {int(k): process_json(v, path + [str(k)]) for k, v in data.items()}

    elif isinstance(data, list):
        return [process_json(item, path + [str(i + 1)]) for i, item in enumerate(data)]

    elif isinstance(data, str):
        if len(path) >= 2 and path[-2:] == ["5", "2"] and is_hex_string(data):
            return bytes.fromhex(data)
        if data.startswith("hex->"):
            hex_part = data[5:]
            return bytes.fromhex(hex_part) if is_hex_string(hex_part) else data
        return data

    else:
        return data
