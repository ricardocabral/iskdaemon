Release checklist
-----------------

    sed -i '' -e's/iskVersion = \"0.9.1\"/iskVersion = \"0.9.2\"/' core/imgdbapi.py 
    sed -i '' -e's/0.9.1/0.9.2/' ui/admin-gwt/src/net/imgseek/server/admin/client/Iskdaemon_admin.java
    sed -i '' -e's/Jan 2012/Jan 2012/' ui/admin-gwt/src/net/imgseek/server/admin/client/Iskdaemon_admin.java
    sed -i '' -e's/0.9.1/0.9.2/' setup.py 
    sed -i '' -e's/0.9/0.9.2/' installer.nsi 

    compile GWT admin ui

    python test_imgdb.py
    python test/test_api.py
 
    # gen py docs
    epydoc -v --html --no-sourcecode --no-frames --no-private -o epyhtml core/imgdbapi.py
    open epyhtml/core.imgdbapi-module.html
    copy/paste to   
    http://www.imgseek.net/isk-daemon/documents-1/api-reference

    python setup.py sdist --formats=gztar,zip register upload
    #python setup.py register
    #python setup.py sdist register upload
    python setup.py bdist

    # Windows
    e:
    cd iskdaemon\src
    rmdir /S /Q dist\isk-daemon
    ..\3rd\pyinstaller\trunk\pyinstaller.py isk-daemon.spec 
    "c:\Program Files\NSIS\makensis.exe" installer.nsi

    # Linux
    scp dist/*.gz rnc@192.168.0.108:
    scp dist/*.gz rnc@192.168.0.107:

    ssh rnc@192.168.0.107
    rm -fr deb
    mkdir deb
    mv *.gz deb
    cd deb
    export DEBFULLNAME="Ricardo Niederberger Cabral"
    export DEBEMAIL="ricardo.cabral@imgseek.net"
    tar zxvf *.gz
    cd isk-daemon
    debuild -us -uc 
    sudo debi
    iskdaemon.py

    git commit -a
    git push
    git tag "v0.9.2"
    git push --tags        

    https://github.com/ricardocabral/iskdaemon/downloads
    git log --pretty=format:%s v0.9.2..
    http://www.imgseek.net/isk-daemon/changelog
    http://www.imgseek.net/isk-daemon/download
    http://www.imgseek.net/news
    http://freecode.com/

Yum based
---------

    sudo yum install ImageMagick-c++-devel swig gcc-c++ python-setuptools python-devel
 
OSX Dev environment
-------------------

    git config --global user.name "Ricardo Cabral"
    git config --global user.email "ricardo@isnotworking.com"

    sudo port install swig
    sudo port install swig-python
    sudo easy_install twisted
    sudo port install imagemagick
    sudo easy_install epydoc

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

    Install Visual Studio C++ express 2008 http://msdn.microsoft.com/en-us/express/future/bb421473
        (2010 express doesnt work well with python)
    Install Git http://code.google.com/p/msysgit/
    install imagemagick windows, select option to include dev headers:
        http://www.imagemagick.org/script/binary-releases.php#windows
        ImageMagick-6.7.4-8-Q16-windows-dll.exe
    32bit python: http://www.python.org/download/releases/2.7.2/
    http://pypi.python.org/packages/2.7/s/setuptools/setuptools-0.6c11.win32-py2.7.exe#md5=57e1e64f6b7c7f1d2eddfc9746bbaf20
    http://www.swig.org/download.html
        copy swigwin into C:\Program Files (x86),  add to PATH
    checkout using Git UI https://ricardocabral@github.com/ricardocabral/iskdaemon.git
    add C:\Python27 to PATH
    launch Visual Studio Command prompt, run C:\Program Files (x86)\Microsoft Visual Studio 9.0\Common7\Tools\vsvars.bat
    update imagemagick dir on setup.py (magick_dir)
    c:\python27\scripts\easy_install twisted
    this may be needed only on some cases: msvc9compiler.py from python27\distutils had to remove linker switch "/EXPORT:" (was getting "unresolved external initimgdb")
    http://nsis.sourceforge.net/Download
    http://www.pyinstaller.org/

Ubuntu packaging
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

