
MACHINEKIT_DIR=/usr

check:
	nosetests test_hal_smartplug.py

install:
	cp hal_smartplug.py $(MACHINEKIT_DIR)/bin/hal_smartplug
