Dev environment
---------------

sudo port install swig
sudo port install swig-python
sudo easy_install twisted
sudo port install imagemagick

imgdb lib dev
-------------

To update Python C++ wrappers

$ src/imgSeekLib/gen_swig.sh 
$ python src/imgSeekLib/build.py build

