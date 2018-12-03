import sys
import pathlib
import clr

_here = pathlib.Path(__file__).parent

# UWPBluetoothPython
sys.path.append(str(pathlib.Path(__file__).parent))
print(str(pathlib.Path(__file__).parent))
clr.AddReference("UWPBluetoothPython")
