build:
	customasm main.asm -o main.bin

build-run: build
	python cpu.py main.bin --clock-speed 10

build-run-debug: build
	python cpu.py main.bin --clock-speed 1 --debug