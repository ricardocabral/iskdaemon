Dev environment
---------------

sudo port install swig
sudo port install swig-python
sudo easy_install twisted
sudo port install imagemagick

imgdb lib dev
-------------

To update Python C++ wrappers

cd src/imgSeekLib
gen_swig.sh 
python build.py build
ln -s build/lib.macosx-10.7-x86_64-2.7/imgdb.so _imgdb.so

