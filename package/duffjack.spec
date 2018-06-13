# -*- mode: python -*-

block_cipher = None


a = Analysis(['duffjack.py'],
             pathex=['C:\\Users\\qnwch\\AppData\\Local\\Continuum\\Anaconda2\\Lib\\site-packages\\PyInstaller'],
             binaries=[],
             datas=[],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          name='duffjack',
          debug=False,
          strip=False,
          upx=True,
          console=False , icon='duff.ico')
