from .pdf import PDF
from .djvu import DJVU
import utils

def openDocument(filename):
    ext = utils.getExtension(filename)
    if ext == ".pdf":
        return PDF(filename)
    elif ext == ".djvu":
        return DJVU(filename)
    else:
        raise Exception("Unsupported file type")
