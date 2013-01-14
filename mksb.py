#!/usr/bin/env python2

import os
import glob
import sys
import argparse
import shutil
import hashlib
import argparse

orig_dir = os.getcwd()
slackbuild_repo_dir = os.path.join(os.environ['HOME'], 'dev', 'slackbuilds')
template_dir = os.path.join(slackbuild_repo_dir, 'templates')
slackbuild_dir = None

prgnam = \
		prg_version = \
		prg_src = \
		src_url = \
		md5sum = \
		src_url_64 = \
		md5sum_64 = \
		home_page = \
		your_name = \
		your_mail = \
		build_type = \
		src_type = None
def make_token_dict(tok_dict):
	td = {}
	for t, v in tok_dict.items():
		td['%%%s%%' % t] = v or ''
	return td

def get_token_dict():
	d = {'prgnam':prgnam,
		'prg_version':prg_version,
		'prg_src':prg_src,
		'src_url':src_url,
		'md5sum':md5sum,
		'src_url_64':src_url_64,
		'md5sum_64':md5sum_64,
		'home_page':home_page,
		'your_name':your_name,
		'your_mail':your_mail,
		'build_type':build_type,
		'src_type':src_type}
	return make_token_dict(d)

def export_vals(vals):
	for k, v in vals.items():
		if v:
			print('set %s = %s' % (k,v))
			globals()[k] = v
		else:
			print('set %s = None' % k)
			globals()[k] = None

def parse_args():
	args = sys.argv[1:]
	argp = argparse.ArgumentParser()
	argp.add_argument('--pkg', dest='prgnam', required=True)
	argp.add_argument('--version', dest='prg_version', required=True)
	argp.add_argument('--src', dest='prg_src', required=True)
	argp.add_argument('--url', dest='src_url', required=False, default=None)
	argp.add_argument('--page', dest='home_page', required=False, default=None)
	argp.add_argument('--author', dest='your_name', required=False, default='N/A')
	argp.add_argument('--mail', dest='your_mail', required=False, default='N/A')
	argp.add_argument('--type', dest='build_type', required=False, default='autotools', choices=['autotools', 'cmake', 'perl', 'python', 'rubygem']) #eventually binary as well
	argp.add_argument('--srctype', dest='src_type', required=False, default='local', choices=['local', 'url', 'repo', 'git', 'svn', 'hg'])
	export_vals(vars(argp.parse_args(args)))

def cd(dir_name):
	if not os.path.exists(dir_name):
		os.makedirs(dir_name, 0755)
		print('made %s' % dir_name)
	os.chdir(dir_name)
	print('moved to %s' % dir_name)

def mv(file_glob, dest):
	manifest = glob.glob(file_glob)
	for i in manifest:
		shutil.move(i, dest)
		print('moved %s to %s' % (i,dest))

def copy_a(files_glob, dest):
	manifest = glob.glob(files_glob)
	print('copy %s to %s' % (files_glob, dest))
	for i in manifest:
		if os.path.isdir(i):
			dir_name = os.path.basename(i)
			shutil.copytree(i, os.path.join(dest, dir_name))
			print('copied %s to %s' % (i, dest))
		else:
			shutil.copy(i, dest)
			print('copied %s to %s' % (i, dest))

def read_file(file_name, mode='r'):
	f = open(file_name, mode)
	s = f.read()
	f.close()
	print('read %s' % file_name)
	return s

def write_file(file_name, string, mode='w'):
	f = open(file_name, mode)
	s = f.write(string)
	print('wrote %s to %s' % (string, file_name))
	f.close()

def replace_in_files(replacement_dict, file_glob):
	print('replace %s in %s' % (replacement_dict, file_glob))
	file_glob = glob.glob(file_glob)
	for i in file_glob:
		contents = read_file(i)
		for t, r in replacement_dict.items():
			contents = contents.replace(t,r)
		write_file(i, contents)


def mk_info_file():
	replace_in_files(get_token_dict(), '%s.info' % prgnam)

#def download(url, file_name=None):

def doinst_comments():
	comments = {'comment-desktopfile-update':'#',
			'comment-etc-install':'#',
			'comment-glib-schema-update':'#',
			'comment-icon-update':'#',
			'comment-init-install':'#',
			'comment-mimedb-update':'#',
			'comment-schema-install':'#'}
	# insert logic here
	replace_in_files(make_token_dict(comments), './doinst.sh')

def init_slackbuild():
	globals()['slackbuild_dir'] = os.path.join(slackbuild_repo_dir, prgnam)
	globals()['template_dir'] = os.path.join(template_dir, build_type, '*')
	os.makedirs(slackbuild_dir)
	copy_a(template_dir, slackbuild_dir)
	cd(slackbuild_dir)
	mv('*.info', prgnam+'.info')
	mv('*.SlackBuild', prgnam+'.SlackBuild')
	doinst_comments()
	mk_info_file()
	replace_in_files(get_token_dict(), './*')

def main():
	parse_args()
	init_slackbuild()
	os.chdir(orig_dir)

if __name__ == '__main__':
	main()
