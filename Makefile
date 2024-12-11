build:
	customasm main.asm -o main.bin

build-run: build
	python cpu.py main.bin --clock-speed 100

build-run-quick: build
	python cpu.py main.bin --clock-speed 1000

build-run-debug: build
	python cpu.py main.bin --clock-speed 1 --debug