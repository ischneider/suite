#!/bin/bash

. functions

build_info

# grab files
DOCS=opengeosuite-$REV-doc.zip
get_file $BUILDS/$DIST_PATH/$DOCS yes

# clean out old files
rm -rf opengeo-docs/opengeo-docs

# unpack
unzip files/$DOCS -d opengeo-docs
checkrc $? "unpacking docs"

# build
build_deb opengeo-docs

# publish
publish_deb opengeo-docs
