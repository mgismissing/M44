import random
import msvcrt

read = False

class KeyboardDriver:
    # Make request with content 0x01 to wait for user input
    port: int = 0x00
    def __pinit__():
        pass
    def __pboot__():
        pass
    def __ptick__():
        pass
    def read() -> int:
        value = KeyboardDriver.port
        KeyboardDriver.port = 0x00
        return value
    def write(value: int):
        KeyboardDriver.port = value & 0xFF

class ScreenDriver:
    # Make request to print the corresponding charcode to the screen
    port: int = 0x00
    def __pinit__():
        pass
    def __pboot__():
        pass
    def __ptick__():
        value = ScreenDriver.read()
        if value != 0x00:
            print(end=chr(value), flush=True)
    def read() -> int:
        value = ScreenDriver.port
        ScreenDriver.port = 0x00
        return value
    def write(value: int):
        ScreenDriver.port = value & 0xFF

ports = {
    0x00: KeyboardDriver,
    0x01: ScreenDriver
}