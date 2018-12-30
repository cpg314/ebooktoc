import utils
import time
import pickle
from pprint import pprint
from difflib import SequenceMatcher
import unicodedata
import multiprocessing as mp

from .page import PageProcessor
from .spellcheck import spellcheck
from document import Outline
from segmenterocr import TesserOCR, cv2Tesseract

class DocumentProcessor(object):
    def __init__(self, doc):
        self._doc = doc
        self._pages = []
        self.headers = []
        self.metadata = []
        self.processed = False

    def _checkProcessed(self):
        if not self.processed:
            raise Exception("Not processed")

    def _cleanPages(self):
        """
        Cleanup page numbers
        """
        pages = []
        for p in self._pages:
            p = list(p)
            p[2] = p[2].title()
            # Anomalies
            if utils.isType(p[1], int) and int(p[1]) > self._doc.numberPages():
                continue
            # Drop empty and non-numerical
            if p[1] is None or not utils.isType(p[1], int):
                continue
            # Check backward average
            h = [pages[-j][1] for j in range(1, 5) if j < len(pages)]
            if len(h) > 0:
                h2 = [hh for hh in h if utils.isType(hh, int)]
                if len(h2) > 0 and abs(p[1] - sum(h2) / len(h2)) > 10:
                    continue
            # Otherwise, add
            pages.append(p)
        self._pages = pages

    # Headers cleanup
    def _cleanHeader(self, h, spellchecking=False):
        """
        Cleanup single header
        """
        # Spell check
        if spellchecking:
            h = spellcheck(h)
        # Interactive correction
        # if interactive:
        #     h = utils.rlinput("Correct if needed: ", h)
        return h
        
    def _cleanHeaders(self):
        """
        Cleanup headers
        """
        for p in self._pages:
            if len(self.headers) == 0:
                self.headers.append(p[:]) # append a copy
                continue
            pr = self.headers[-1]
            # Distance between titles
            if any([SequenceMatcher(None, p[2], h[2]).ratio() > 0.7 for h in self.headers]):
                continue
            # If too close, pick the longest
            if p[0] - pr[0] < 3:
                if len(p[2]) > len(pr[2]):
                    self.headers[-1] = p[:]
                continue
            # Add
            self.headers.append(p[:])
        for h in self.headers:
            del h[1]
            h[1] = self._cleanHeader(h[1], False)

    def getOutline(self):
        """
        Extract outline from headers
        """
        self._checkProcessed()
        outline = Outline()
        for h in self.headers:
            print("{} {} {}".format(0, h[0], h[1]))
        outline.fromHeaders(self.headers)
        return outline

    def getPages(self):
        """
        Get correspondence between real and virtual pages
        """
        self._checkProcessed()
        return {p[0]: p[1] for p in self._pages}
    
    def _processPages(self, callback=None, caching=True):
        """
        Process document pages
        """
        docHash = self._doc.getHash()
        # Check cache
        if caching:
            cache = utils.getCached(docHash)
            if cache is not None:
                self._pages = cache  
                return
        # Setup
        nPages = self._doc.numberPages()
        pool = mp.Pool(processes=4)
        self._pages = []
        for i in range(1, nPages + 1):
            self._pages.append((i,
                                pool.apply_async(PageProcessor(self._doc.extract(i - 1), TesserOCR).process,
                                                 callback=lambda x: callback(None))))
        self._pages = [(i, ) + p.get() for i, p in self._pages]
        utils.cache(self._pages, docHash)
        return    

    # Metadata
    def _processMetadata(self, limit=5):
        """
        Extract metadata
        """
        for i in range(0, limit):
            metadata = PageProcessor(self._doc.extract(i), TesserOCR).processMetadata()
            if metadata is not None:
                self.metadata = metadata
                return
        return

    def getFilename(self):
        self._checkProcessed()
        if len(self.metadata) == 0:
            return None
        meta = self.metadata[0]        
        authors = [a.split(" ")[1] for a in meta["authors"]]
        authors = ", ".join(authors)
        filename = "{}-{}-{}-{}".format(authors, meta["title"], meta["publisher"], meta["year"])
        filename = unicodedata.normalize('NFKD', filename).encode('ascii', 'ignore').decode("utf-8")
        return filename

    
    def process(self, callback=None, caching=True):
        # self._processMetadata() # TODO: uncomment
        if False:
            # Profiling
            import cProfile
            cProfile.runctx("self._processPages(callback, caching)", globals(), locals(), sort="tottime")
        else:
            self._processPages(callback, caching)
        self._cleanPages()
        self._cleanHeaders()
        self.processed = True
        return
