Release checklist
-----------------

    cd ~/Projects/iskdaemon/src
    sed -i '' -e's/iskVersion = \"0.9.2\"/iskVersion = \"0.9.3\"/' core/imgdbapi.py 
    sed -i '' -e's/0.9.2/0.9.3/' ui/admin-gwt/src/net/imgseek/server/admin/client/Iskdaemon_admin.java
    sed -i '' -e's/Jan 2012/Jan 2012/' ui/admin-gwt/src/net/imgseek/server/admin/client/Iskdaemon_admin.java
    sed -i '' -e's/0.9.2/0.9.3/' setup.py 
    sed -i '' -e's/0.9.2/0.9.3/' installer.nsi 

    compile GWT admin ui

    python test_imgdb.py
    python test/test_api.py
 
    # gen py docs
    epydoc -v --html --no-sourcecode --no-frames --no-private -o epyhtml core/imgdbapi.py
    open epyhtml/core.imgdbapi-module.html
    copy/paste to   
    http://www.imgseek.net/isk-daemon/documents-1/api-reference
    edit HTML and remove occurences of core.imgdbapi-module.html

    # Windows
    Git shell
        cd /c/prj/iskdaemon
        git pull
    Visual Studio Prompt
    cd /c/prj/iskdaemon
    python setup.py build
    rmdir /S /Q dist\isk-daemon
    python ..\..\pyinstaller\PyInstaller.py isk-daemon.spec   
    "c:\Program Files (x86)\NSIS\makensis.exe" installer.nsi
    run installer
    upload installer to https://github.com/ricardocabral/iskdaemon/downloads


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
    git tag "v0.9.3"
    git push --tags        

    python setup.py sdist --formats=gztar,zip register upload
    #python setup.py register
    #python setup.py sdist register upload
    python setup.py bdist

    https://github.com/ricardocabral/iskdaemon/downloads
    git log --pretty=format:%s v0.9.2..
    http://www.imgseek.net/isk-daemon/changelog
    http://www.imgseek.net/isk-daemon/download
    http://www.imgseek.net/news
    http://freecode.com/

    Notify users on:
    https://docs.google.com/a/imgseek.net/spreadsheet/ccc?key=0Am8ZmW0g7_c-dEFQb3hxOXlwYThMUUJ1VnpjMmRDWWc&hl=en_US#gid=0

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

New dev
=======
    Install Visual Studio C++ express 2008 http://msdn.microsoft.com/en-us/express/future/bb421473
        (2010 express doesnt work well with python)
    Install Git http://code.google.com/p/msysgit/
    mkdir /prj
    cd /prj
    git clone https://ricardocabral@github.com/ricardocabral/iskdaemon.git
    git config --global user.name "Ricardo Niederberger Cabral"
    git config --global user.email "ricardo@isnotworking.com"

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
    http://www.pyinstaller.org/  (just extract on a folder)
    http://sourceforge.net/projects/pywin32/files/pywin32/
    http://nsis.sourceforge.net/NSIS_Simple_Service_Plugin

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

