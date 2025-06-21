class Protobuf:
    @staticmethod
    def encode(obj) -> bytes:
        buffer = bytearray()
        for tag in sorted(obj.keys()):
            Protobuf._encode(buffer, tag, obj[tag])
        return bytes(buffer)

    @staticmethod
    def _encode(buffer, tag, value):
        if isinstance(value, list):
            for item in value:
                Protobuf._encode_value(buffer, tag, item)
        else:
            Protobuf._encode_value(buffer, tag, value)

    @staticmethod
    def _encode_value(buffer, tag, value):
        if value is None:
            return
        if isinstance(value, int):
            Protobuf._encode_varint(buffer, tag, value)
        elif isinstance(value, bool):
            Protobuf._encode_bool(buffer, tag, value)
        elif isinstance(value, str):
            Protobuf._encode_string(buffer, tag, value)
        elif isinstance(value, (bytes, bytearray)):
            Protobuf._encode_bytes(buffer, tag, value)
        elif isinstance(value, dict):
            nested = Protobuf.encode(value)
            Protobuf._encode_bytes(buffer, tag, nested)
        else:
            raise TypeError(f"Unsupported type {type(value)}")

    @staticmethod
    def _encode_varint(buffer, tag, value):
        key = (tag << 3) | 0
        Protobuf._write_varint(buffer, key)
        Protobuf._write_varint(buffer, value)

    @staticmethod
    def _encode_bool(buffer, tag, value):
        Protobuf._encode_varint(buffer, tag, 1 if value else 0)

    @staticmethod
    def _encode_string(buffer, tag, value):
        key = (tag << 3) | 2
        encoded = value.encode("utf-8")
        Protobuf._write_varint(buffer, key)
        Protobuf._write_varint(buffer, len(encoded))
        buffer.extend(encoded)

    @staticmethod
    def _encode_bytes(buffer, tag, value):
        key = (tag << 3) | 2
        Protobuf._write_varint(buffer, key)
        Protobuf._write_varint(buffer, len(value))
        buffer.extend(value)

    @staticmethod
    def _write_varint(buffer, value):
        value &= 0xFFFFFFFFFFFFFFFF
        while True:
            byte = value & 0x7F
            value >>= 7
            if value:
                buffer.append(byte | 0x80)
            else:
                buffer.append(byte)
                break
