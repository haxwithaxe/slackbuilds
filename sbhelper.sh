#!/bin/bash

gitroot=$(dirname $0)

get_with_git(){
	if [ ! -d $CWD/$PRGNAM ] ;then
		git clone $GITREMOTE $CWD/$PRGNAM
	fi
	cd $CWD/$PRGNAM
	git clean -dxf
	git checkout $GITBRANCH
	git pull
	cd -
	get_from_dir $CWD/$PRGNAM
}

get_with_hg(){
	if [ ! -d $CWD/$PRGNAM ] ;then
		hg clone $DOWNLOAD $CWD/$PRGNAM
	fi
	cd $CWD/$PRGNAM
	if ! hg status -un ;then hg status -un | xargs rm ;fi
	hg update -c $BRANCH
	hg pull -u
	cd -
    get_from_dir $CWD/$PRGNAM
}

get_from_url(){
	#FIXME handle multiple urls
	SRCURL=${SRCURL:-$1}
	SRCEXT=${SRCEXT:-$2}
    if [ ! -e $PRGNAM-$VERSION${SRCEXT} ] ;then
		wget "$SRCURL" -O $PRGNAM-$VERSION${SRCEXT}
	fi
	get_from_arch $PRGNAM-$VERSION${SRCEXT}
}

get_from_arch(){
	SRC_ARCHIVE=${SRC_ARCHIVE:-$1}
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
	SRCDIR=${SRCDIR:-$1}
	cp -r $SRCDIR $TMP/$PRGNAM-$VERSION
}

make_real_git(){
	gitmodules_file=$1
	name=$2
	submodule=${submodule_copy:-$3}
	section=false
	while read line ;do
		if [ $( grep -q "^#" >/dev/null 2>&1 <<< $line ) ] && \
			[ ! -z "$line" ] ;then
				if [ $( sed 's/[[:space:]]\+//' <<< ${line} | egrep -q '^\[' ) ] ;then
					if $section ;then 
						break
					else
						section_name=$(sed 's/^[^"]*"//;s/"[^"]*$//;s/^[/]*\///' <<< $line)
						if [ "$section_name" = "$name" ] ;then
							section=true
						else
							section=false
							break
						fi
					fi
				elif [ $section ] ;then
					eval "$(sed '/[[:space:]]*=[[:space:]]*/="/;s/[[:space:]]*$/"/' <<< $line)"
				fi
		fi
	done < $gitmodules_file
	mv $submodule/.git $submodule/.git.submodule
	mkdir -p $submodule/.git
	touch $submodule/.git/config
	cat - > $submodule/.git/config <<EOF
[core]
	repositoryformatversion = 0
	filemode = true
	bare = false
	logallrefupdates = true
[remote "origin"]
	url = $url
	fetch = +refs/heads/*:refs/remotes/origin/*
[branch "master"]
	remote = origin
	merge = refs/heads/master
EOF
}

copy_git_submodule(){
	submodule=$1
	submodule_copy=$2
	gitroot=${GITROOT:-".."}
	cp -a $submodule $submodule_copy
	make_real_git $gitroot/.gitmodules $submodule $submodule_copy
}

