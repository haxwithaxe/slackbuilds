#!/bin/bash

## automatically update pianobar from the git repository
OWD=`pwd`
GIT_REPO=pianobar-git
BRANCH=master
SLACKBUILD='..'

cd $GIT_REPO
git pull origin $BRANCH
version=`grep Realease ChangeLog | head -n1 | cut -d' ' -f2`
cd ..
cp -r $GIT_REPO ${PRGNAM}-${VERSION:-$version}
tar zcvf ${PRGNAM}-${VERSION:-$version}.tar.gz ${PRGNAM}-${VERSION:-$version}
mv ${PRGNAM}-${VERSION:-$version}.tar.gz $SLACKBUILD
cd $SLACKBUILD

export VERSION=${VERSION:-$version}
export PRGNAM=${PRGNAM}

. ${PRGNAM}.SlackBuild

cd $OWD
