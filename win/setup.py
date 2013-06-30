from distutils.core import setup
import py2exe

#setup(console=["hx.py"])
setup(
  options = {
    "py2exe": {
        "dll_excludes": ["MSVCP90.dll"],
        "compressed": 1,
        "optimize": 2, 
        "bundle_files": 2
    }
  },
    version = "0.1.0",
    zipfile=None,
    console=["main.py"]
)