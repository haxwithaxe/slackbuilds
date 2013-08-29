#!/bin/bash

get_with_git(){
	if [ ! -d $PRGNAM ] ;then
		git clone $GITREMOTE $PRGNAM
	fi
	cd $PRGNAM
	git clean -dxf
	git pull
	cd -
	get_from_dir $PRGNAM
}

get_from_url(){
	SRCURL=${SRCURL:=$1}
	SRCEXT=${SRCEXT:=$2}
    if [ ! -e $PRGNAM-$VERSION${SRCEXT} ] ;then
		wget "$SRCURL" -O $PRGNAM-$VERSION${SRCEXT}
	fi
	get_from_arch $PRGNAM-$VERSION${SRCEXT}
}

get_from_arch(){
	SRC_ARCHIVE=${SRC_ARCHIVE:=$1}
	mime_type=`file --mime-type $SRC_ARCHIVE | sed 's/^[^:]*\:[[:space:]]//'`
	case "$mime_type" in
		"application/zip")
			unzip ${SRC_ARCHIVE}
			;;
		"application/x-gzip")
			tar zxvf ${SRC_ARCHIVE}
			;;
		"application/x-bzip2")
			tar jxvf ${SRC_ARCHIVE}
			;;
		*)
			echo -n
			;;
	esac
}

get_from_dir(){
	SRCDIR=${SRCDIR:=$1}
	cp -r $SRCDIR $PRGNAM-$VERSION
}

