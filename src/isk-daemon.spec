# -*- mode: python -*-

import os

def AllFilesIn(sdir):
    allfiles = []
    for root, dirs, files in os.walk(sdir):
        allfiles += [root+'/'+fname for fname in files]
    print 'allfiles',allfiles
    return allfiles

def Datafiles(filenames, **kw):
    def datafile(path, strip_path=True):
        parts = path.split('/')
        path = name = os.path.join(*parts)
        if strip_path:
            name = os.path.basename(path)
        return name, path, 'DATA'

    strip_path = kw.get('strip_path', False)
    return TOC(
        datafile(filename, strip_path=strip_path)
        for filename in filenames
        if os.path.isfile(filename))

a = Analysis([os.path.join(HOMEPATH,'support\\_mountzlib.py'), os.path.join(CONFIGDIR,'support\\useUnicode.py'), 'win32_svc_wrapper.py'],
             pathex=['E:\\iskdaemon\\3rd\\pyinstaller\\trunk'],
             hookspath=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name=os.path.join('build\\pyi.win32\\isk-daemon', 'isk-daemon.exe'),
          debug=False,
          strip=None,
          upx=True,
          icon='ui\\admin-www\\favicon.ico',
          console=False)
docfiles = Datafiles(['isk-daemon.conf','AUTHORS.txt','COPYING.txt','README.txt'] + AllFilesIn('ui\\admin-www')+ AllFilesIn('plugins'))
coll = COLLECT( exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               docfiles,
               strip=None,
               upx=True,
               name=os.path.join('dist', 'isk-daemon'))
