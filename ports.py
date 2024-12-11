import random

read = False

class ExampleDriver:
    port: int = 0x00
    def __pinit__():
        pass
    def __pboot__():
        pass
    def __ptick__():
        pass
    def read() -> int:
        value = ExampleDriver.port
        ExampleDriver.port = 0x00
        return value
    def write(value: int):
        ExampleDriver.port = value & 0xFF

ports = {
    0x00: ExampleDriver
}