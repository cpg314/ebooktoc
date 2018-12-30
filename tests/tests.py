from document import PDF
from document import Outline
from processor import PageProcessor, DocumentProcessor
from segmenterocr import TesserOCR, cv2Tesseract
import utils

import unittest
import hashlib
from pprint import pprint
import logging
import shutil
import os

# Debug setup
logging.basicConfig(level=logging.DEBUG)
if not os.path.isdir("debug"):
    os.mkdir("debug")
# if os.path.isdir("debug"):
#     shutil.rmtree("debug")
# os.mkdir("debug")

class TestProcessors(unittest.TestCase):
    def setUp(self):
        self.documents = [PDF("tests/1.pdf"), PDF("tests/2.pdf")]
        #self.documents = [PDF("tests/2.pdf")]
        
        self.processors = []
        for d in self.documents:
            self.processors.append(DocumentProcessor(d))
        # self.TOCPage = 3

    def tearDown(self):
        for d in self.documents:
            d.close()

    def test_OCR(self):
        d = self.documents[0]
        s = [TesserOCR(d.extract(49, "PIL")), cv2Tesseract(d.extract(49))]
        for ss in s:
            ss.detectBlocks()
        
    def test_pageProcessor(self):
        for so in [TesserOCR, cv2Tesseract]:
            d = self.documents[0]
            # self.assertEqual(PageProcessor(d.extract(15), so).process(), (9, "CHAPTER 1"))
            self.assertIn(PageProcessor(d.extract(16), so).process(), [(10, "1. ARITHMETIC FUNCTIONS"), (10, "ARITHMETIC FUNCTIONS")])
            # self.assertEqual(PageProcessor(d.extract(49), so).process(), (43, "CHAPTER 3"))
            # Metadata
            d = self.documents[1]            
            metadata = PageProcessor(d.extract(4), so).processMetadata()
            self.assertEqual(metadata, [{'authors': ['Jürgen Neukirch'], 'publisher': 'Springer',
                                         'title': 'Algebraische Zahlentheorie',
                                         'year': '1992'}])

    def test_documentProcessor(self):
        for p in self.processors:
            p.process(callback=None, caching=True)
            print(p.getFilename())

    def test_repagination(self):
        for i, d in enumerate(self.documents):
            proc = self.processors[i]
            proc.process(callback=None, caching=True)
            d.repaginate(proc.getPages())
            d.write("debug/{}-repaginated.pdf".format(d.getHash()))
            # self.assertEqual(utils.sha1_file("debug/repaginated.pdf"), "")
        
    def test_outline(self):
        for i, d in enumerate(self.documents):
            proc = self.processors[i]
            proc.process(callback=None, caching=True)
            pprint(proc.getHeaders())
            out = proc.getOutline()
            print(out.show())
            print("Write outline")
            d.writeOutline(out)
            d.write("debug/{}-outlined.pdf".format(d.getHash()))

    def test_outline_repaginate(self):
        for i, d in enumerate(self.documents):
            proc = self.processors[i]
            proc.process(callback=None, caching=True)
            d.writeOutline(proc.getOutline())
            d.repaginate(proc.getPages())
            d.write("debug/{}.pdf".format(d.getHash()))


class TestDocuments(unittest.TestCase):
    def setUp(self):
        # Create outline
        self.outline = Outline()
        self.p = []
        self.p.append(self.outline.create_node("Top3", 14))
        self.p.append(self.outline.create_node("Top1", 10))
        self.p.append(self.outline.create_node("Top2", 13))
        self.outline.create_node("Child11", 11, self.p[1])
        self.outline.create_node("Child12", 12, self.p[1])
        self.outline.create_node("Child31", 20, self.p[0])
        self.outline.sort()

    def test_outline(self):
        self.assertEqual(self.outline.size(), 6)
        self.assertEqual(self.outline.firstchild(0), 1)
        self.assertEqual(self.outline.lastchild(0), 2)
        self.assertEqual(self.outline.next(0), 3)

        self.assertEqual(self.outline.previous(3), 0)
        self.assertEqual(self.outline.next(3), 4)
        self.assertEqual(utils.sha1(self.outline.show().encode("utf-8")), "42ecfe943d426f069eb8e185cf21c22885a9a584")

    def test_PDF(self):
        with PDF("tests/2.pdf") as d:
            p = d.extract(16)
        with PDF("tests/1.pdf") as d:
            self.assertEqual(d.getHash(), "24a276e6961ed1fadea2116bb299307b68a2c0be")
            # Extract page
            self.assertEqual(utils.sha1(d.extract(10).dumps()), "0640c6eeaa62df69a56e5a383a5407a77fd51615")
            # # Number of pages
            self.assertEqual(d.numberPages(), 610)
            # # Repagination
            d.repaginate({1: 5, 2: 8})
            d.write("debug/repaginated.pdf")
            self.assertEqual(utils.sha1_file("debug/repaginated.pdf"), "5e0793e28b09be9245f91ccb65a7e6f733ba0367")
            # # Outline
            d.writeOutline(self.outline)
            d.write("debug/outlined.pdf")
            self.assertEqual(utils.sha1_file("debug/outlined.pdf"), "5e0793e28b09be9245f91ccb65a7e6f733ba0367")


if __name__ == '__main__':
    unittest.main()
