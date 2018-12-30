from .spellcheck import error_rate
from .metadata import *
import utils

import re
from math import floor

class PageProcessor(object):
    def __init__(self, tmpfile, SegmenterOCR):
        """
        :param segmentocr: SegmenterOCR subclass.
        """
        self.segmenterocr = SegmenterOCR(tmpfile)

    def _cleanHeading(self, t):
        m = re.match("(\d+\.)*\s*(.*)\s*", t)
        return m.group(2)

    def _detectNumberHeader(self, block, p):
        """
        Detect heading texts and page numbers in header
        No cleanup is done at this point
        """
        # TODO: store all potential page numbers
        page = None
        heading = []
        ocr = block["ocr"]
        if len(ocr) > 0:
            ocr = "".join(ocr)
            utils.log("\t{}".format(ocr))
            if utils.isType(ocr, int):
                page = int(ocr)
                utils.log("\t-> Found page number")
            elif re.match("^[MDCLXVI]+$", ocr.upper()):
                page = ocr
                utils.log("\t-> Found latin page number")
            elif p == "top":
                #if len(ocr) > 5 and error_rate(ocr) < 0.5:
                heading.append(ocr)
                utils.log("\t-> Found heading")
        return page, heading

    def process(self):
        """
        Extract the candidate page and headings of a regular page.
        Output: page number and headings
        """
        utils.log("Processing page")
        utils.log("Detecting blocks")
        self.segmenterocr.detectBlocks()
        #print(self.segmenterocr.blocks)
        utils.log("Detect header and footer blocks and OCR them")
        hfblocks = self.segmenterocr.headFootBlocks()
        page = None
        heading = []
        # hfblocks = hfblocks["top"]
        for k, blocks in hfblocks.items():
            for b in blocks:
                page2, heading2 = self._detectNumberHeader(b, k)
                heading = heading + heading2
                if page2 is not None:
                    page = page2
        return page, " ".join(heading)

    # Metadata
    def processMetadata(self):
        """
        Try to find ISBN number on page, and fetch book metadata
        Output: candidate books metadata
        """
        utils.log("Looking for metadata")
        self.segmenterocr.detectBlocks()
        reg = re.compile(r"(?:978-)*\d{1,5}-\d{1,7}-\d{1,5}-[\dX]")
        for b in self.segmenterocr.blocks:
            ocr = " ".join(self.segmenterocr.OCRBlock(b))
            ocr = re.findall(reg, ocr)
            if len(ocr) > 0:
                return getMetadata(ocr[0])
        return None
    
    # Table of contents
    
    def findTOC(self):
        """
        Check whether the page contains a table of contents
        """
        return False

    def processTOC(self):
        """
        Extract table of contents
        To test
        """
        # TODO: adapt with SegmenterOCR
        # utils.log("Extracting TOC")
        # return
        # sections = []
        # pagenumbers = []
        # # Extract blocks
        # blocks = detectTextBlocks(self._image)
        # utils.log("{} blocks extracted".format(len(blocks)))
        # for i, b in enumerate(blocks):
        #     utils.log("Process block {}/{}".format(i + 1, len(blocks)))
        #     # OCR block
        #     ocr = OCR(self._image, b, False, 3)
        #     xratio = float(b[0]) / self._imgwidth # Position ratio
        #     wratio = float(b[2]) / self._imgwidth # Width ratio
        #     utils.log("\txratio: {}, wratio: {}".format(xratio, wratio))
        #     if xratio < 0.3:  # Section(s)
        #         utils.log("\tSection")
        #         sections = sections + [self._cleanHeading(t) for t in ocr]
        #     elif (xratio > 0.5 and wratio < 0.3):  # Page number(s)
        #         utils.log("\tPage number")
        #         pagenumbers = pagenumbers + [l for l in ocr if utils.isType(l, int)]
        #     else:
        #         utils.log("\tUnknown")
        #     if utils.isDebug():
        #         cropped = utils.region(self._image, b)
        #         imwrite("debug/" + str(i) + ".png", cropped)
        # utils.log("Block processing finished")
        # utils.log("{} sections and {} page numbers processed".format(len(sections), len(pagenumbers)))
        # # Number of sections matches with number of page numbers
        # if len(sections) == len(pagenumbers):
        #     return [(sections[i], pagenumbers[i]) for i, _ in enumerate(pagenumbers)]
        # else:
        #     return []
        #      # TODO
