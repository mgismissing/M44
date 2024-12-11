# Ports

## What are "ports"?

Ports are M44's way to communicate with external I/O devices such as a keyboard or a screen. To make this happen, a `ports.py` file with the correct structure must be present in the same directory as the `cpu.py` file.

## Creating the `ports.py` file

To get started, create a `ports.py` file in the same directory as the `cpu.py` file. Then, copy and paste this code:

```py3
class ExampleDriver:
    port: int = 0x00
    def __pinit__():
        print("Example Driver Initialized!")
    def __pboot__():
        print("Example Driver Ready!")
    def __ptick__():
        print("Example Driver Tick!")
    def read():
        value = ExampleDriver.port
        if ExampleDriver.port == 0x00:
            print("No data to read!")
        else:
            print(f"Received: {ExampleDriver.port}")
        ExampleDriver.port = 0x00
        return value
    def write(value: int):
        ExampleDriver.port = value & 0xFF
        print(f"Written value {value}")

ports = {
    0x00: ExampleDriver
}
```

So, how does this code work and why should it be like this?

```py3
class ExampleDriver:
    port: int = 0x00
```

First, we define a class called `ExampleDriver` (this name can be changed to anything you want) and we create a variable called `port`. This variable is the actual port that will enable us to communicate with the CPU.

```py3
    def __pinit__():
        print("Example Driver Initialized!")
    def __pboot__():
        print("Example Driver Ready!")
```

Then we create a function called `__pinit__` and another one called `__pboot__`: the first one will be called when the `cpu.py` **program** is run and the last one will be called when the **CPU** is run.

```py3
    def __ptick__():
        print("Example Driver Tick!")
```

Right after them is the `__ptick__` function: this one will be run **once for every CPU cycle**. This means you really shouldn't put time consuming operations here (and of course no "waiting for x seconds") unless it's really necessary, because the CPU will keep running **only after this part of the code has finished running**.

```py3
    def read():
        value = ExampleDriver.port
        if ExampleDriver.port == 0x00:
            print("No data to read!")
        else:
            print(f"Received: {ExampleDriver.port}")
        ExampleDriver.port = 0x00
        return value
    def write(value: int):
        ExampleDriver.port = value & 0xFF
        print(f"Written value {value}")
```

Finally, these are example functions (they won't be automatically called by the CPU) that read and write information over the port we saw before.

```py3
ports = {
    0x00: ExampleDriver
}
```

Once we're finished defining the drivers we can define a `ports` dict that will store on **which** of the 256 ports the drivers should be. This will then be needed when programming the CPU as we will need to specify the port number before sending data to it. If no port is specified then that connection will be "dead" and anything written to it will be lost. Trying to read from one of those ports is also not recommended because it will return random values. You might be thinking that it can come in handy when creating RNGs but at this point you should rather create another driver for that and have it generate a random value for every CPU cycle.

## Low-level trickery

If you want to get advanced and the default read/write function from the above example is not enough for you, this is how the CPU reads and writes data to a port at a low level. By reading this part you will be able to use the CPU to your advantage and create a custom function that can fulfil your needs.

### Reading / writing a byte

The CPU talks with other devices by setting a variable and optionally waiting for the device to read it. The variable, `port`, can be normally found in the user defined `ports.py` file. The process to read a byte from a port is as follows:

1. The CPU reads the value in the `port` variable;
2. Its value is then reset to `0x00`.

This can be used to check if the CPU has read the byte or if it's executing some other code. Let's use an example: imagine that the processor should read a byte from port `0x9E`, store it in the RAM and add it to the `D` register. Since this operation will obviously use more that one instruction (and more that one cycle) to execute we can't just output all of the data on one single clock cycle. What we should do every cycle (in the `__ptick__` function) is:

1. Check if the `port` variable is set to `0x00` (this means that it has been succesfully read and stored by the CPU);
2. Do nothing if it's not `0x00`, or write the next byte if it is;
3. End the function code and give control back to the CPU.

Writing bytes, instead, is more straightforward. We just set the `port` variable to whatever value we want.

This should also work the other way around (the CPU will wait for us to read and set the `port` variable back to `0x00` before writing the next byte).

Lastly, you should know this, but if you don't already: **writing more times to the same port in the same CPU cycle will NOT yield faster speed in communication. It will just overwrite the older value with the one we're trying to write.**
