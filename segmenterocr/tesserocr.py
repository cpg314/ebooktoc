from . import SegmenterOCR
import utils

import locale
locale.setlocale(locale.LC_ALL, 'C') # see https://github.com/sirfz/tesserocr/issues/137
import tesserocr
from PIL import Image

class TesserOCR(SegmenterOCR):
    """
    Use tesseract page segmenter and OCR engine through tesserocr,
    using tesseract's C API (no intermediary files written)
    """
    api = tesserocr.PyTessBaseAPI(psm=tesserocr.PSM.SPARSE_TEXT)
    def __init__(self, tmpfile):
        SegmenterOCR.__init__(self, tmpfile)
        self.image = Image.open(tmpfile.name)
        self.w, self.h = self.image.size        
        #self.api = tesserocr.PyTessBaseAPI(psm=tesserocr.PSM.AUTO)

    def __del__(self):
        #api.End()
        return

    def detectBlocks(self, region=None):
        # TODO: region
        TesserOCR.api.SetImage(self.image)
        self.blocks = TesserOCR.api.GetComponentImages(tesserocr.RIL.TEXTLINE, True, raw_padding=0)
        for i, b in enumerate(self.blocks):
            self.blocks[i] = b[1]
            if utils.isDebug():
                b[0].save("debug/{}.jpg".format(i))
        super().detectBlocks()
        return
        
    def OCRBlock(self, b):
        TesserOCR.api.SetRectangle(b["x"] - 2, b["y"] - 2, b["w"] + 4, b["h"] + 4) # TODO: check boundaries
        return self._cleanOCR(TesserOCR.api.GetUTF8Text())
