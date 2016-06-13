
SHELL:=/bin/bash
ROOT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

.PHONY: all fresh dependencies install fulluninstall uninstall removedeps

all: dependencies

fresh: fulluninstall dependencies

fulluninstall: uninstall cleancode

install:
	# Create link in /usr/local/bin to screeps stats program.
	ln -s -f $(ROOT_DIR)/bin/screepsconsole.sh /usr/local/bin/screepsconsole

dependencies:
	if [ ! -d $(ROOT_DIR)/env ]; then virtualenv $(ROOT_DIR)/env; fi
	source $(ROOT_DIR)/env/bin/activate; yes w | pip install -r $(ROOT_DIR)/requirements.txt

uninstall:
	# Remove screepsstats link in /user/local/bin
	if [ -L /usr/local/bin/screepsconsole.sh ]; then \
		rm /usr/local/bin/screepsconsole; \
	fi;

cleancode:
	# Remove existing environment
	if [ -d $(ROOT_DIR)/env ]; then \
		rm -rf $(ROOT_DIR)/env; \
	fi;
	# Remove compiled python files
	if [ -d $(ROOT_DIR)/screep_etl ]; then \
		rm -f $(ROOT_DIR)/screep_etl/*.pyc; \
	fi;
