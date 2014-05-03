# Makefile for the creation of the Debian deployment package.

# Dependencies:
# - rsync
# - dpkg-deb

SHELL=/bin/bash

APP_NAME=pjc-compmgr

VERSION?=$(shell grep -e '^Version:' DEBIAN/control | cut -d' ' -f2 | tr -d [:blank:])
DEBPKG_NAME?=$(APP_NAME)_$(VERSION)_all

RSYNC=rsync -Ca

BUILD_ROOT=build
BUILD_OPT=$(BUILD_ROOT)/opt/$(APP_NAME)
BUILD_VAR_LIB=$(BUILD_ROOT)/var/lib/$(APP_NAME)
BUILD_ETC=$(BUILD_ROOT)/etc/$(APP_NAME)
BUILD_INIT_D=$(BUILD_ROOT)/etc/init.d

dist: update_build_tree
	@echo '------ creating Debian package...'
	fakeroot dpkg --build $(BUILD_ROOT) $(DEBPKG_NAME).deb

update_build_tree: 
	@echo '------ copying files in build area...'
	mkdir -p $(BUILD_OPT)/bin $(BUILD_VAR_LIB) $(BUILD_ETC) $(BUILD_INIT_D)

	# dpkg files
	cp -ar DEBIAN $(BUILD_ROOT)

	# application bin
	cp -a src/bin/*.py $(BUILD_OPT)/bin

	# application lib
	$(RSYNC) \
		--filter "-s_*/.*" \
		--include "*.py" \
		--include "*/" \
		--include "*.html" \
		--include "*.html" \
		--include "*.js" \
		--include "*.css" \
		--include "*.png" \
		--include "*.jpg" \
		--include "*.jpeg" \
		--include "*.gif" \
		--include "*.svg" \
		--include "*.pdf" \
		--exclude "*" \
		src/lib/ $(BUILD_OPT)/lib

	# init script
	cp -a src/init.d/$(APP_NAME) $(BUILD_INIT_D)

	# teams list
	cp -a src/var/* $(BUILD_VAR_LIB)

clean:
	@echo '------ cleaning all...'
	rm -rf $(BUILD_ROOT) $(DEBPKG_NAME).deb

