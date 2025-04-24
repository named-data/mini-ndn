class CircularByteBuffer:
    """Byte buffer handmade for terminal output"""
    size: int = 0
    start: int = 0
    buffer: bytearray

    def __init__(self, size: int):
        self.buffer = bytearray(size)

    def writeByte(self, byte: int):
        if self.size < len(self.buffer):
            self.buffer[self.size] = byte
            self.size += 1
            return

        self.buffer[self.start % self.size] = byte
        self.start = (self.start + 1) % self.size

    def write(self, data: bytes):
        for byte in data:
            self.writeByte(byte)

    def read(self):
        if self.size <= len(self.buffer):
            return self.buffer[self.start:self.start + self.size]
        else:
            return self.buffer[self.start:] + self.buffer[:self.start]