#!/bin/bash

## automatically update from the git repository
GIT_REPO=${CWD}/${PRGNAM}-${VERSION}
REMOTE_REPO=git://github.com/PromyLOPh/pianobar.git

if [ ! -e $GIT_REPO ] ;then
	git clone $REMOTE_REPO $GIT_REPO
fi

cd $GIT_REPO
git pull
cd $1
