Release checklist
-----------------

    cd imgSeekLib
    python test_all.py

    sed -i '' -e's/iskVersion = \"0.9\"/iskVersion = \"0.9.1\"/' core/imgdbapi.py 
    sed -i '' -e's/0.9/0.9.1/' ui/admin-gwt/src/net/imgseek/server/admin/client/Iskdaemon_admin.java
    sed -i '' -e's/Jan 2012/Jan 2012/' ui/admin-gwt/src/net/imgseek/server/admin/client/Iskdaemon_admin.java
 
    git commit -a
    git push
    git tag "v1.3"
    git push --tags        

    python setup.py register
    python setup.py sdist --formats=gztar,zip
    python setup.py bdist

    scp dist/*.gz rnc@192.168.0.108:
    scp dist/*.gz rnc@192.168.0.107:

    ssh rnc@192.168.0.107
    rm -fr deb
    mkdir deb
    mv *.gz deb
    cd deb
    export DEBFULLNAME="Ricardo Niederberger Cabral"
    export DEBEMAIL="ricardo.cabral@imgseek.net"
    tar zxvf ~/*.gz
    cd isk-daemon
    debuild -us -uc 
    sudo debi
    isk-daemon.py

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

    Packaging tutorial: https://wiki.ubuntu.com/PackagingGuide/Python

    export DEBFULLNAME="Ricardo Niederberger Cabral"
    export DEBEMAIL="ricardo.cabral@imgseek.net"


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

