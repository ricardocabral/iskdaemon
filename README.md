# About

isk-daemon is an open source database server capable of adding [content-based (visual) image searching](http://en.wikipedia.org/wiki/Content-based_image_retrieval) to any image related website or software.

This technology allows users of any image-related website or software to sketch on a widget which image they want to find and have the website reply to them the most similar images or simply request for more similar photos at each image detail page.

A desktop version of this technology is available as the open-source [imgSeek project](http://sourceforge.net/projects/imgseek/).

# Key features

* Query for images similar to one already indexed by the database, returning a similarity degree for the images on database that most resemble the target query image;
* Query for images similar to one described by its signature. A client-side widget may generate such signature from what a user sketched and submit it to the daemon;
* Network interface for easy integration with other web or desktop applications: XML-RPC, SOAP;
* Fast indexing of images one-by-one or in batch;
* Associate keywords to images and perform image-similarity queries filtering by keywords;
* Quickly remove images from database one-by-one or in batch;
* Built-in web-based admin interface with statistics and ad-hoc maintenance commands/API testing;
* Optimized image processing code (implemented in C++).

# Install instructions

Here is a quick guide to build from a cloned git repo. You may want to ``sudo`` all these commands if you have permission errors.
I assume you know how to build from source and have all build tools (most are installed on the next steps) and libraries installed for your system.

##Ubuntu Quick Start

This one is tested with Ubuntu 14.12

1. Install prerequisited if they're not on your system already:

    ``apt-get install swig ImageMagick libmagick++-dev python-dev``

2. cd to ./src and run: ``python setup.py install``

##MacOS Quick Start

1. Go to http://brew.sh and install ``Homebrew``

2. Install swig: ``brew install swig``

3. Install ImageMagick: ``brew install ImageMagick``

4. Install pkg-config: ``brew install pkg-config``

5. Cd to ./iskdaemon/src/ and run ``python setup.py install``

Alternatively, you can try it with ``macports``.

# Credits

imgSeek and isk-daemon portions copyright Ricardo Niederberger Cabral (ricardo.cabral at imgseek.net).

Image loading code is credited to "ImageMagick Studio LLC" and library linkage adheres to statements on ImageMagick-License.txt

# Support or Donate

Help on improving this software is needed, feel free to submit patches to either the documentation or code.  Thanks!

Money donations are also welcome:

[![Flattr this git repo](http://api.flattr.com/button/flattr-badge-large.png)](https://flattr.com/submit/auto?user_id=rnc000&url=https://github.com/ricardocabral/iskdaemon&title=iskdaemon&language=en_GB&tags=github&category=software)

Or 

[Donate using PayPal](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=J7XSCK2JNJB52&lc=US&item_name=imgSeek%20project&currency_code=USD&bn=PP%2dDonationsBF%3abtn_donate_SM%2egif%3aNonHosted)
