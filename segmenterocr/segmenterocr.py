from pprint import pprint
from math import floor

class SegmenterOCR(object):
    """
        Parent class for Segmenter/OCRs. Two children classes are implemented: cv2tesseract and tesserocr
    """
    def __init__(self, tmpfile):
        self.image = None
        self.blocks = []
        self.w = 0
        self.h = 0

    def headFootBlocks(self):
        """
        Detect header and footer blocks and perform OCR on them
        """
        hfblocks = {"top": [], "bottom": []}
        for p in ["top", "bottom"]:
            for b in self.blocks:
                if not (p == "top" and b["pos"] ==0) and not (p == "bottom" and b["pos"] == 3):
                    continue
                hfblocks[p].append(b)
            # Keep only blocks y-close enough to the top or bottom-most block (could use that only)
            def yclose_filter(bb, ratio=0.01):
                return (bb["y"] - hfblocks[p][0 if p == "top" else -1]["y"]) / float(self.h) < ratio
            hfblocks[p] = list(filter(yclose_filter, hfblocks[p]))
            # Sort according to x-coordinate
            hfblocks[p] = sorted(hfblocks[p], key=lambda b: b["x"])
            # Perform OCR
            for i, b in enumerate(hfblocks[p]):
                hfblocks[p][i]["ocr"] = self.OCRBlock(b)
        return hfblocks
        
    def detectBlocks(self, region=None):
        # Sort by y coordinate
        self.blocks = sorted(self.blocks, key=lambda b: b["y"])
        # Set positions
        for i, b in enumerate(self.blocks):
            self.blocks[i]["pos"] = floor(3.0 * b["y"] / self.h)
        return

    def _cleanOCR(self, out):
        out = out.split("\n")
        out = list(filter(lambda x: not (x.isspace() or len(x) == 0), out))   # Remove empty lines
        return out
    
    def OCRBlock(self, b):
        return
        
        
