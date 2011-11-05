#!/usr/bin/env python
import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

# win/linux diffs
import os
# unfortunatelly this is not working
if os.name == 'nt': # fix windows stuff
    imgSeekLib_package_data = ['*.dll']
else: # linux
    imgSeekLib_package_data = ['*.so']
    
setup(name="isk-daemon",
      version='0.7',
      description="Server and library for adding content-based (visual) image searching to any image related website or software.",
      long_description ="This technology allows users of any image-related website or software to sketch on a widget which image they want to find and have the website reply to them the most similar images or simply request for more similar photos at each image detail page.",
      keywords = "imgseek iskdaemon image cbir imagedatabase isk-daemon database searchengine",
      author="Ricardo Niederberger Cabral",
      author_email="ricardo.cabral at imgseek.net",
      url="http://server.imgseek.net/",
      download_url = "http://server.imgseek.net/category/download/",
      platforms = ['Linux','Windows','Mac OSX'],
      license = 'GPLv2',
      packages=['imgSeekLib'],
      package_data={'imgSeekLib': imgSeekLib_package_data},
      scripts= ['isk-daemon.py','default_settings.py','settings.py'],
      install_requires = ['Twisted >= 8',
                          'simplejson',
                          'fpconst',
                          'SOAPpy == 0.11',
                          ],
      dependency_links = ["http://sourceforge.net/project/showfiles.php?group_id=26590&package_id=18246",
                         ],


     )

