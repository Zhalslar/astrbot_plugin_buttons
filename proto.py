class ProtobufEncoder:
    def encode(self, obj):
        buffer = bytearray()
        for tag in sorted(obj.keys()):
            self._encode(buffer, tag, obj[tag])
        return bytes(buffer)

    def _encode(self, buffer, tag, value):
        if isinstance(value, list):
            for item in value:
                self._encode_value(buffer, tag, item)
        else:
            self._encode_value(buffer, tag, value)

    def _encode_value(self, buffer, tag, value):
        if value is None:
            return
        if isinstance(value, int):
            self._encode_varint(buffer, tag, value)
        elif isinstance(value, bool):
            self._encode_bool(buffer, tag, value)
        elif isinstance(value, str):
            self._encode_string(buffer, tag, value)
        elif isinstance(value, (bytes, bytearray)):
            self._encode_bytes(buffer, tag, value)
        elif isinstance(value, dict):
            nested = self.encode(value)
            self._encode_bytes(buffer, tag, nested)
        else:
            raise TypeError(f"Unsupported type {type(value)}")

    def _encode_varint(self, buffer, tag, value):
        key = (tag << 3) | 0
        self._write_varint(buffer, key)
        self._write_varint(buffer, value)

    def _encode_bool(self, buffer, tag, value):
        self._encode_varint(buffer, tag, 1 if value else 0)

    def _encode_string(self, buffer, tag, value):
        key = (tag << 3) | 2
        encoded = value.encode("utf-8")
        self._write_varint(buffer, key)
        self._write_varint(buffer, len(encoded))
        buffer.extend(encoded)

    def _encode_bytes(self, buffer, tag, value):
        key = (tag << 3) | 2
        self._write_varint(buffer, key)
        self._write_varint(buffer, len(value))
        buffer.extend(value)

    def _write_varint(self, buffer, value):
        value &= 0xFFFFFFFFFFFFFFFF
        while True:
            byte = value & 0x7F
            value >>= 7
            if value:
                buffer.append(byte | 0x80)
            else:
                buffer.append(byte)
                break
