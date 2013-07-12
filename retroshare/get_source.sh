#!/bin/bash

if ! [ -d retroshare-svn ] ;then
svn co svn://svn.code.sf.net/p/retroshare/code/trunk retroshare-svn
fi
cd retroshare-svn
svn up
cd -
