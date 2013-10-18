config() {
  NEW="$1"
  OLD="$(dirname $NEW)/$(basename $NEW .new)"
  # If there's no config file by that name, mv it over:
  if [ ! -r $OLD ]; then
    mv $NEW $OLD
  elif [ "$(cat $OLD | md5sum)" = "$(cat $NEW | md5sum)" ]; then
    # toss the redundant copy
    rm $NEW
  fi
  # Otherwise, we leave the .new copy for the admin to consider...
}

preserve_perms() {
  NEW="$1"
  OLD="$(dirname $NEW)/$(basename $NEW .new)"
  if [ -e $OLD ]; then
    cp -a $OLD ${NEW}.incoming
    cat $NEW > ${NEW}.incoming
    mv ${NEW}.incoming $NEW
  fi
  config $NEW
}

schema_install() {
  SCHEMA="$1"
  GCONF_CONFIG_SOURCE="xml::etc/gconf/gconf.xml.defaults" \
  chroot . gconftool-2 --makefile-install-rule \
    /etc/gconf/schemas/$SCHEMA \
    1>/dev/null
}
%comment_schema_install%schema_install blah.schemas
%comment_init_install%preserve_perms etc/rc.d/rc.INIT.new
%comment_etc_install%config etc/configfile.new

%comment_desktopfile_update%if [ -x /usr/bin/update-desktop-database ]; then
%comment_desktopfile_update%	/usr/bin/update-desktop-database -q usr/share/applications >/dev/null 2>&1
%comment_desktopfile_update%fi

%comment_mimedb_update%if [ -x /usr/bin/update-mime-database ]; then
%comment_mimedb_update%  /usr/bin/update-mime-database usr/share/mime >/dev/null 2>&1
%comment_mimedb_update%fi

%comment_icon_update%if [ -e usr/share/icons/hicolor/icon-theme.cache ]; then
%comment_icon_update%  if [ -x /usr/bin/gtk-update-icon-cache ]; then
%comment_icon_update%    /usr/bin/gtk-update-icon-cache usr/share/icons/hicolor >/dev/null 2>&1
%comment_icon_update%  fi
%comment_icon_update%fi

%comment_glib_schema_update%if [ -x /usr/bin/glib-compile-schemas ]; then
%comment_glib_schema_update%  /usr/bin/glib-compile-schemas /usr/share/glib-2.0/schemas/
%comment_glib_schema_update%fi

