# -*- mode: python -*-

block_cipher = None


a = Analysis(['MainMenu.py'],
             pathex=['C:\\Users\\she384\\AppData\\Local\\Programs\\Python\\Python36\\Lib\\site-packages\\scipy\\extra-dll', 'C:\\Users\\she384\\Documents\\Tests', 'C:\\Users\\she384\\AppData\\Local\\Programs\\Python\\Python36\\Lib\\site-packages\\scipy',
			 'C:\\Users\\she384\\Documents\\HyPro2'],
             binaries=[],
             datas=[],
             hiddenimports=['numpy.random', 'pyqtgraph'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
			 noarchive=False)
			 
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
			 
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='HyPro v0.20',
          debug=False,
          strip=False,
          upx=False,
          runtime_tmpdir=None,
          console=True, icon='assets/2dropsshadow.ico',
		  version = 'C:\\Users\\she384\\OneDrive - CSIRO\\Documents\\HyPro2\\hypro_version.rc')
