.PHONY: ci run clean upload monitor tags

CIOPTS=--board=esp32dev --lib="src"

ci:
	cp -n examples/pubSubTest/config.h-dist examples/pubSubTest/config.h
	platformio ci $(CIOPTS) --lib=examples/pubSubTest examples/pubSubTest/pubSubTest.ino 

run:
	pio run

clean:
	-pio run --target clean
	rm -f src/*.o

upload:
	pio run --target upload 

monitor:
	pio device monitor 

tags:
	ctags -R
