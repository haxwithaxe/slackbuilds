#!/usr/bin/env python2

import os
import glob
import sys
import argparse
import shutil
import hashlib
import argparse
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


class SlackBuildTmpl:
	tokens = {'build_num':None,
		'comment_desktopfile_update':False,
		'comment_etc_install':False,
		'comment_glib_schema_update':False,
		'comment_icon_update':False,
		'comment_init_install':False,
		'comment_mimedb_update':False,
		'comment_schema_install':False,
		'comment_copy_docs':None,
		'documentation_files':None,
		'home_page':None,
		'install_to_pkgroot':None,
		'iX86_arch':None,
		'makepkg_chown':None,
		'makepkg_ext':None,
		'makepkg_link':None,
		'comment_man_pages':False,
		'md5sum':None,
		'md5sum_64':'',
		'prgnam':None,
		'prgnam_len':None,
		'src_url':None,
		'src_url_64':'',
		'untar_command':None,
		'version':None,
		'your_mail':None,
		'your_name':None}
	slackbuild_dir = None

	def __init__(self, *args, **kwargs):
		self.orig_dir = os.getcwd()
		self.slackbuild_repo_dir = os.path.join(os.environ['HOME'], 'dev', 'slackbuilds')
		self.template_dir = os.path.join(self.slackbuild_repo_dir, 'templates')
		self.slackbuild_dir = ''
		self.populate_token_dict()
		self.copy_a(self.template_dir, self.slackbuild_dir)
		self.cd(self.slackbuild_dir)
		self.tmpl_mv() # copy all template.* to their PRGNAM equiv
		self.mk_info_file()
		self.replace_in_files(self.tokens, os.path.join(self.slackbuild_dir, '*'))
		os.chdir(self.orig_dir)
	
	def load_commands(self):
		tmpl = os.path.join(self.template_dir, self.tokens['build_type'])
		tmpl_str = self.read_file(self, tmpl)
		if tmpl_str:
			self.tokens['install_to_pkgroot'] = tmpl_str
		if self.tokens['pkg_type'] == 'tgz':
			self.tokens['untar_command'] = 'tar zxvf $PRGNAM-$VERSION*.t*gz'
		elif self.tokens['pkg_type'] == 'tbz':
			self.tokens['untar_command'] = 'tar zxvf $PRGNAM-$VERSION*.t*gz'
		elif self.tokens['pkg_type'] == 'git':
			pass
		elif self.tokens['pkg_type'] == 'hg':
			pass
		elif self.tokens['pkg_type'] == 'svn':
			pass
		else:
			self.tokens['untar_command'] = 'tar zxvf $PRGNAM-$VERSION*.t*gz'

	def populate_token_dict(self):
		self.parse_args()
		for t, v in self.tokens.items():
			if type(v) == bool and t.startswith('comment'): v = {True:'#', False:''}[v]
			elif not v: v = ''
			self.tokens['%%%s%%' % t] = str(v)

	def parse_args(self):
		args = sys.argv[1:]
		argp = argparse.ArgumentParser()
		argp.add_argument('--pkg', dest='prgnam', required=True)
		argp.add_argument('--version', dest='version', required=True)
		argp.add_argument('--src', dest='prg_src', required=True)
		argp.add_argument('--url', dest='src_url', required=False, default=None)
		argp.add_argument('--page', dest='home_page', required=False, default=None)
		argp.add_argument('--author', dest='your_name', required=False, default='N/A')
		argp.add_argument('--mail', dest='your_mail', required=False, default='N/A')
		argp.add_argument('--type', dest='build_type', required=False, default='autotools', choices=['autotools', 'qmake', 'cmake', 'perl', 'python', 'rubygem','make','manual'])
		argp.add_argument('--srctype', dest='src_type', required=False, default='local', choices=['local', 'url', 'repo', 'git', 'svn', 'hg'])
		args_ns = argp.parse_args(args)
		self.tokens.update(vars(args_ns))
		self.cmd_template = os.path.join(self.template_dir, self.tokens['build_type'])
		self.slackbuild_dir = os.path.join(self.slackbuild_repo_dir, self.tokens['prgnam'])

	def cd(self, dir_name):
		if not os.path.exists(dir_name):
			os.makedirs(dir_name, 0755)
		logger.debug('made %s' % dir_name)
		os.chdir(dir_name)
		logger.debug('moved to %s' % dir_name)

	def mv(self, file_glob, dest):
		manifest = glob.glob(file_glob)
		for i in manifest:
			shutil.move(i, dest)
			logger.debug('moved %s to %s' % (i, dest))
	
	def tmpl_mv(self):
		sbdir = self.slackbuild_dir
		for f in glob.glob(os.path.join(sbdir, 'template*')):
			ext = os.path.splitext(f)[-1]
			dest = os.path.join(sbdir, '%s.%s' % (self.tokens['prgnam'], ext))
			self.mv(f, dest)

	def copy_a(self, files_glob, dest):
		manifest = glob.glob(files_glob)
		if not os.path.isdir(dest):
			if os.path.exists(dest) and os.path.isfile(dest):
				os.remove(dest)
			os.makedirs(dest, 0755)
		logger.debug('copy %s to %s' % (files_glob, dest))
		for i in manifest:
			if os.path.isdir(i):
				dir_name = os.path.basename(i)
				shutil.copytree(i, os.path.join(dest, dir_name))
				logger.debug('copied %s to %s' % (i, dest))
			else:
				shutil.copy(i, dest)
				logger.debug('copied %s to %s' % (i, dest))

	def read_file(self, file_name, mode='r'):
		f = open(file_name, mode)
		s = f.read()
		f.close()
		logger.debug('read %s' % file_name)
		return s

	def write_file(self, file_name, string, mode='w'):
		f = open(file_name, mode)
		s = f.write(string)
		logger.debug('wrote %s to %s' % (string, file_name))
		f.close()

	def replace_in_files(self, replacement_dict, file_glob):
		logger.debug('replace %s in %s' % (replacement_dict, file_glob))
		file_glob = glob.glob(file_glob)
		for i in file_glob:
			contents = self.read_file(i)
			for t, r in replacement_dict.items():
				contents = contents.replace(t,r or '')
			self.write_file(i, contents)

	def mk_info_file(self):
		self.replace_in_files(self.populate_token_dict(), '%sinfo' % self.tokens['prgnam'])

	def download(self):
		# if source not exists
		# then download or checkout based on cli args and return True
		# else return True
		# on errors return False
		pass

if __name__ == '__main__':
	SlackBuildTmpl()
	pass
