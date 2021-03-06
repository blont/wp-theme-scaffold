#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, shutil, pystache, re, pwd, pprint, shutil, codecs, subprocess, string
from datetime import date
from pprint import pprint

# def rm_wp(str):
# 	return re.sub(r'(?i)^(WP|WordPress\s?)','',str).strip()
#
def slugify(str,separator='_'):
	return re.sub(r'[^\w\d]+',separator,str.strip()).lower()

def camelcase( str ):
	str = re.sub(r'[-_\s]',' ', str.strip() )
	return re.sub(r'\s','', string.capwords( str ) )

#print camelcase('King-Dings')
#sys.exit()
# def plugin_slug(str):
# 	return slugify(rm_wp(str))
#
# def plugin_classname(str):
# 	return ''.join(x for x in rm_wp(str).title() if not x.isspace())

class wp_theme:
	defaults = {
		'theme_author'		: '',
		'this_year'			: '',
		'theme_name'		: '',
		'theme_slug'		: '',
		'theme_slug_dash'	: '',
		'theme_slug_camel'	: '',
		'template'			: '2.0'
	}

	def __init__(self,config):
		self.config			= self.process_config( config )
		self.theme_dir		= os.getcwd() + '/' + slugify( self.config['theme_name'], '-' )
		self.theme_source	= os.path.dirname( os.path.realpath( __file__ ) ) + '/theme/'+self.config['template']+'/'

	def process_config(self,config):
		author 						= pwd.getpwuid( os.getuid() ).pw_gecos

		config['theme_author'] 		= author.decode('utf-8')#.encode('utf-8')
		config['this_year'] 		= str( date.today().year )

		config['theme_name'] 		= config['theme_name']
		config['theme_slug'] 		= slugify( config['theme_name'] )
		config['theme_slug_dash']	= slugify( config['theme_name'], '-' )
		config['theme_slug_camel']	= camelcase( config['theme_slug_dash'] )

		return config

	def make(self):
		try:
			os.mkdir(self.theme_dir)
		except OSError as e:
			return e

		ignore = []
		f = codecs.open(self.theme_source+'.gitignore','rb',encoding='utf-8')
		ignore = f.readlines()
		f.close()
		ignore = [x.replace('\n','') for x in ignore if len(x) > 0 and x[0] != '#']
		ignore.append('.git/')
		ignore.append('node_modules/')
		ignore.append('.DS_Store')

		subst = ['php','md','scss','js','css','txt','json']

		for root, subdirs, files in os.walk(self.theme_source):
			relroot = root.replace( self.theme_source, '' ) + '/'

			# ignore files
			if [x for x in ignore if relroot.find(x) >= 0]:
				continue;

			dir = self.theme_dir + '/' + self._substitute_filename( relroot )

			# make subdirs if needed
			if not os.path.exists(dir):
				os.makedirs(dir)

			# copy file and substitute _bs
			for file in files:
				if [x for x in ignore if file.find(x) >= 0]:
					continue;
				source = root + '/' + file
				target = dir + '/' + self._substitute_filename( file )

				print file

				if  [x for x in subst if re.findall('\.'+x+'$',file)]:
					#
					# content = pystache.render( self._read_file_contents(source),self.config)
					content = self._read_file_contents(source)#.decode("utf-8")
					for key,value in self.config.items():
						#print(repr(content),repr(key),repr(value))
						s = u'___%s___' % (key)
						content = content.replace( s, value )

					fout = codecs.open( target , 'wb' , encoding='utf-8' )
					fout.write(content);
					fout.close()
				else:
					shutil.copyfile(source , target)

		pass


	def _read_file_contents( self , file_path ):
		if not os.path.exists(file_path):
			return ''
		f = codecs.open(file_path,'rb',encoding='utf-8')
		contents = f.read()
		f.close()
		return contents


	def _substitute_filename(self, str):
		repl = {
			'__theme_slug__'		: self.config['theme_slug'],
			'__theme_slug_dash__'	: self.config['theme_slug_dash'],
			'__theme_slug_camel__'	: self.config['theme_slug_camel'],
		}
		for s,r in repl.iteritems():
#			print s
 			str = str.replace(s,r)
		return str


usage = '''
usage ./theme.py 'Theme Name' [template] [ --force ]
'''

defaults = config = wp_theme.defaults


try:
	config['theme_name']	= sys.argv[1]
	try:
		if sys.argv[2] != '--force':
			config['template']	= sys.argv[2]
	except IndexError as e2:
		pass
except IndexError as e:
	print usage
	sys.exit(0)


print "Generating Theme:", config['theme_name']
maker = wp_theme(config)

if '--force' in sys.argv and os.path.exists(maker.theme_dir):
	shutil.rmtree( maker.theme_dir )

result = maker.make()

if isinstance(result, Exception):
	print 'Theme exists:',result
	print 'use --force to override existing theme'
else:
 	print 'Setup gulp'
 	os.chdir( maker.theme_dir );
 	subprocess.call( ['npm', 'install'])
 	subprocess.call( ['gulp', 'fontello'])
 	print 'Init git'
	subprocess.call( ['git', 'init'])
	subprocess.call( ['git', 'add', '.'])
	subprocess.call( ['git', 'commit', '-m "Initial"'])
 	print 'Edit'
	subprocess.call( ['atom', '.'])
