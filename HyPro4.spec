# -*- mode: python -*-

block_cipher = None


a = Analysis(['MainMenu.py'],
             pathex=['C:\\Users\\she384\\AppData\\Local\\Programs\\Python\\Python36\\Lib\\site-packages\\scipy\\extra-dll', 'C:\\Users\\she384\\Documents\\Tests', 'C:\\Users\\she384\\AppData\\Local\\Programs\\Python\\Python36\\Lib\\site-packages\\scipy'],
             binaries=[],
             datas=[],
             hiddenimports=['scipy.stats', 'scipy', 'scipy.special', 'scipy.optimize', 'scipy.integrate', 'scipy.optimize._trlib', 'cftime',
			 'scipy._lib.messagestream', 'scipy._lib', 'scipy.linregress'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
			 
			 
a.datas += Tree('./scipy-extra-dll', prefix=None)

			 
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
			 
			 
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='HyPro v0.02',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True, icon='2dropsshadow.ico')
