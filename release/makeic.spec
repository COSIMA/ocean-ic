# -*- mode: python -*-

block_cipher = None

extra_bins = [
    ('/home/599/nah599/more_home/anaconda2/lib/python2.7/site-packages/llvmlite/binding/libllvmlite.so', 'llvmlite/binding')
]

grid_def_datas = [
    ('/short/v45/nah599/more_home/ocean-ic/grid_defs/coordinates.nc', './grid_defs/'),
    ('/short/v45/nah599/more_home/ocean-ic/grid_defs/coordinates_grid_T.nc', './grid_defs/'),
    ('/short/v45/nah599/more_home/ocean-ic/grid_defs/coordinates_grid_U.nc', './grid_defs/'),
    ('/short/v45/nah599/more_home/ocean-ic/grid_defs/coordinates_grid_V.nc', './grid_defs/'),
    ('/short/v45/nah599/more_home/ocean-ic/grid_defs/data_1m_potential_temperature_nomask.nc', './grid_defs/'),
    ('/short/v45/nah599/more_home/ocean-ic/grid_defs/ocean_hgrid.nc', './grid_defs/'),
    ('/short/v45/nah599/more_home/ocean-ic/grid_defs/ocean_mask.nc', './grid_defs/'),
    ('/short/v45/nah599/more_home/ocean-ic/grid_defs/ocean_vgrid.nc', './grid_defs/'),
    ('/short/v45/nah599/more_home/ocean-ic/grid_defs/pottmp.2016.nc', './grid_defs/')
]

a = Analysis(['../makeic.py'],
             pathex=['/short/v45/nah599/more_home/ocean-ic'],
             binaries=extra_bins,
             datas=grid_def_datas,
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
