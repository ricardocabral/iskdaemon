OSX Dev environment
-------------------

    sudo port install swig
    sudo port install swig-python
    sudo easy_install twisted
    sudo port install imagemagick

Ubuntu Dev environment
----------------------

    sudo apt-get install build-essential devscripts ubuntu-dev-tools debhelper dh-make diff patch cdbs quilt gnupg  fakeroot lintian  pbuilder piuparts
    sudo apt-get install swig
    sudo apt-get install python-twisted-web
    sudo apt-get install libmagick++-dev
    sudo apt-get install git-core
    sudo apt-get install python-dev 

    mkdir ~/prj
    cd ~/prj
    git clone git@github.com:ricardocabral/iskdaemon.git
    git config --global user.name "Ricardo Niederberger Cabral"
    git config --global user.email "ricardo@isnotworking.com"

Windows
-------

Install Visual Studio express
install imagemagick windows, option to include dev headers

msvc9compiler.py from python27\distutils had to remove linker switch "/EXPORT:" (was getting "unresolved external initimgdb")

ubuntu packaging
----------------

https://wiki.ubuntu.com/PackagingGuide/Complete

    sudo pbuilder create --distribution $(lsb_release -cs) \
     --othermirror "deb http://archive.ubuntu.com/ubuntu $(lsb_release -cs) main restricted universe multiverse"


imgdb lib dev
--------------

To update Python C++ wrappers

    cd src/imgSeekLib
    gen_swig.sh 
    python build.py build
    ln -s build/lib.macosx-10.7-x86_64-2.7/imgdb.so _imgdb.so





debian install notes





running build_ext
building 'imgdb' extension
creating build/temp.linux-i686-2.6
creating build/temp.linux-i686-2.6/imgSeekLib
gcc -pthread -fno-strict-aliasing -DNDEBUG -g -fwrapv -O2 -Wall -Wstrict-prototypes -fPIC -I/usr/include/python2.6 -c imgSeekLib/imgdb.cpp -o build/temp.linux-i686-2.6/imgSeekLib/imgdb.o -DImMagick -DLinuxBuild -g
gcc: error trying to exec 'cc1plus': execvp: No such file or directory
Traceback (most recent call last):
  File "setup.py", line 96, in run
    build_ext.run(self)
  File "/usr/lib/python2.6/distutils/command/build_ext.py", line 340, in run
    self.build_extensions()
  File "/usr/lib/python2.6/distutils/command/build_ext.py", line 449, in build_extensions
    self.build_extension(ext)
  File "/usr/lib/python2.6/distutils/command/build_ext.py", line 499, in build_extension
    depends=ext.depends)
  File "/usr/lib/python2.6/distutils/ccompiler.py", line 621, in compile
    self._compile(obj, src, ext, cc_args, extra_postargs, pp_opts)
  File "/usr/lib/python2.6/distutils/unixccompiler.py", line 180, in _compile
    raise CompileError, msg
CompileError: command 'gcc' failed with exit status 1
running build_scripts
creating build/scripts-2.6

solved with:
    sudo apt-get install build-essential 

-------------------------------------------------------------------------------------------------------------------
--- WARNING ---
Unable to find Magick++-config. Are you sure you have ImageMagick and it's development files installed correctly?
Found the following arguments:
extra_compile_args ['-DImMagick', '-DLinuxBuild', '-g']

should block and tell user to:

    sudo apt-get install libmagick++-dev

-------------------------------------------------------------------------------------------------------------------


imgSeekLib/imgdb_wrap.cxx:149:20: error: Python.h: No such file or directory
imgSeekLib/imgdb_wrap.cxx:2976:4: error: #error "This python version requires swig to be run with the '-classic' option"

had to install:

    sudo apt-get install python-dev 

-------------------------------------------------------------------------------------------------------------------

swigging imgSeekLib/imgdb.i to imgSeekLib/imgdb_wrap.cpp
swig -python -c++ -o imgSeekLib/imgdb_wrap.cpp imgSeekLib/imgdb.i
unable to execute swig: No such file or directory
error: command 'swig' failed with exit status 1

    sudo apt-get install swig



 
