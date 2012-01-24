#!/usr/bin/env python
import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

# win/linux diffs
import os

# reuse README as package long description
with open('README.txt') as file:
    long_description = file.read()

try:
    import sys,commands,traceback,os
    from distutils import sysconfig
    from distutils.core import setup,Extension
    from distutils.command.build_ext import build_ext
    from distutils.errors import CCompilerError
    from string import *
    import platform
except:
    traceback.print_exc()
    print "Unable to import python distutils."
    print "You may want to install the python-dev package on your distribution."
    sys.exit(1)

############## Init some vars

library_dirs = []
include_dirs = []
libraries = []
extra_link_args = []
IMagCFlag = []
IMagCLib = []
extra_compile_args = ["-DImMagick"]

if os.name == 'nt': # windows
    magick_dir = 'C:\Program Files (x86)\ImageMagick-6.7.4-Q16'
    library_dirs = [magick_dir + "\\lib"]
    include_dirs = [magick_dir + "\\include"]
    libraries = ["CORE_RL_Magick++_","CORE_RL_magick_"]
    extra_compile_args += ["-DWIN32"]
    extra_compile_args += ["-D__WIN32__"]
    extra_compile_args += ["-D_CONSOLE"]
    extra_compile_args += ["-D_VISUALC_"]
#TODO-2 make sure any other performance/size related switch needs to be toggled
#    extra_compile_args += ["-DNeedFunctionPrototypes"]
#    extra_compile_args += ["-D_DLL"]
    extra_compile_args += ["-D_MAGICKMOD_"]
else: # *nix
    hasIMagick=0
    extra_compile_args += [ "-DLinuxBuild","-g"] 
    extra_link_args += ["-g"] #TODO-0 remove debug
    print "#################################### Check ImageMagick"
    try:
        fnd=0
        pathvar=os.environ["PATH"]
        for pv in split(pathvar,':'):
            if os.path.exists(pv+'/Magick++-config') or os.path.exists(pv+'Magick++-config'):
                fnd=1
        if fnd:
            IMagCFlag=os.popen("Magick++-config --cxxflags --cppflags").read()
            if find(IMagCFlag,"-I") != -1:
                IMagCFlag=replace(IMagCFlag,"\n"," ")
                IMagCFlag=split(IMagCFlag,' ')
                IMagCLib=os.popen("Magick++-config --ldflags --libs").read()
                IMagCLib=replace(IMagCLib,"\n"," ")
                IMagCLib=split(IMagCLib,' ')
                hasIMagick=1
        else:
            print "--- WARNING ---\nUnable to find Magick++-config. Are you sure you have ImageMagick and it's development files installed correctly?"
    except:
        traceback.print_exc()

for cf in IMagCFlag:
    cf=strip(cf)
    if not cf: continue
    extra_compile_args.append(cf)
for cf in IMagCLib:
    cf=strip(cf)
    if not cf: continue
    extra_link_args.append(cf)
print "Found the following arguments:"
print "extra_compile_args",extra_compile_args
print "extra_link_args",extra_link_args

class fallible_build_ext(build_ext):
    """the purpose of this class is to know when a compile error ocurred """
    def run(self):
        try:
            build_ext.run(self)
        except CCompilerError:
            traceback.print_exc()

# force C++ linking
from distutils import sysconfig
config_vars = sysconfig.get_config_vars() #TODO-2 is this really still necessary?
for k, v in config_vars.items():
    if k.count('LD') and str(v).startswith('gcc'):
        config_vars[k] = v.replace('gcc', 'g++')
            
def find_data_files(d):
    matches = []
    for root, dirnames, filenames in os.walk(d):
      for filename in filenames:
          matches.append(os.path.join(root[3:], filename))
    return matches

print "#################################### Installing"
setup(name="isk-daemon",
      version='0.9.3',
      description="Server and library for adding content-based (visual) image searching to any image related website or software.",
      long_description=long_description,
      keywords = "imgseek iskdaemon image cbir imagedatabase isk-daemon database searchengine",
      author="Ricardo Niederberger Cabral",
      author_email="ricardo.cabral at imgseek.net",
      url="http://server.imgseek.net/",
      download_url = "http://www.imgseek.net/isk-daemon/download",
      platforms = ['Linux','Windows','Mac OSX'],
      cmdclass = { 'build_ext': fallible_build_ext},
      ext_modules = [
        Extension("_imgdb",["imgSeekLib/imgdb.cpp",
                           "imgSeekLib/haar.cpp",
                           "imgSeekLib/imgdb.i",
                           "imgSeekLib/bloom_filter.cpp"
                                      ],
                  include_dirs = include_dirs,
                  library_dirs = library_dirs,
                  extra_compile_args = extra_compile_args,
                  extra_link_args = extra_link_args,
                  libraries = libraries,
                  swig_opts = ['-c++']
                 )],
      py_modules = ['imgdb'],
      license = 'GPLv2',
      packages=['imgSeekLib', 'ui','plugins','core'],
      package_data={'imgSeekLib': ['*.so','*.pyd','*.dll'],
                    'ui': find_data_files('ui/admin-www'), 
                    },
      scripts= ['iskdaemon.py'],
      install_requires = ['Twisted >= 8',
                          'simplejson',
                          'fpconst',
                          'SOAPpy',
                          ],
      dependency_links = ["http://sourceforge.net/project/showfiles.php?group_id=26590&package_id=18246",
                         ],
     )

print "See http://www.imgseek.net/isk-daemon/documents-1/usage for some next steps."
print "See http://www.imgseek.net/isk-daemon/documents-1/faq for some common questions."
