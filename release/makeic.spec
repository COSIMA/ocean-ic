# -*- mode: python -*-

block_cipher = None

a = Analysis(['../makeic.py'],
             pathex=['/short/v45/nah599/more_home/ocean-ic'],
             binaries=[('/home/599/nah599/more_home/anaconda2/lib/python2.7/site-packages/llvmlite/binding/libllvmlite.so', 'llvmlite/binding')],
             datas=None,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='makeic',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='makeic')
