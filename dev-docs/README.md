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
    git config --global user.email ricardo@isnotworking.com

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

 
