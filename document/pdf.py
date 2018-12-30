"""
PDF implementation of the Document class
"""

from . import Document
import utils

from PyPDF2 import pdf as pyPDF
from cv2 import imread
from PIL import Image
from shutil import copyfile
from tempfile import NamedTemporaryFile, mkstemp
import re
from subprocess import call


class PDF(Document):
    def __init__(self, filename):
        Document.__init__(self, filename)
        self._r = pyPDF.PdfFileReader(self._f)
        self._w = pyPDF.PdfFileWriter()
        for i in self._r.pages:
            self._w.addPage(i)

    def close(self):
        Document.close(self)

    def extract(self, page, density = 300):
        """
        Extract page using convert
        """
        tmpfile = NamedTemporaryFile(suffix=".jpg")
        utils.call(["convert", "-density", str(density), "{}[{}]".format(self._filename, page), tmpfile.name])
        return tmpfile
        # if fmt == "cv2":
        #     return imread(tmpfile.name)
        # else:
        #     return Image.open(tmpfile.name)            
        # Alternatively, directly extract from PDF
        # see also http://stackoverflow.com/a/34116472/194594
        # g = list(self._r.getPage(page)["/Resources"]["/XObject"].items())
        # g = g[0][1].getObject()
        # tmpfile = NamedTemporaryFile(suffix=".jbig2")
        # with open(tmpfile.name, "wb") as f:
        #     f.write(g._data)
        # return imread(tmpfile.name)

    def extractText(self, page):
        # Alternatively, use https://pythonhosted.org/PyPDF2/PageObject.html#PyPDF2.pdf.PageObject.extractText
        page = str(page)
        return utils.call(["pdftotext", self._filename, "-f", page, "-l", page, "-"]).decode("utf-8")

    def numberPages(self):
        return self._r.getNumPages()

    def write(self, filename):
        with open(filename, "wb") as f:
            self._w.write(f)

    def repaginate(self, pagination):
        """
        Repaginate by directly modifying the file
        """
        nums = pyPDF.ArrayObject()
        # Add initial roman numberings (pages are shifted if this is missing)
        nums.append(self._PDFfloat(0))
        nums.append(self._PDFdict({self._PDFname("S"): self._PDFname("r")}))
        for k, p in pagination.items():
            nums.append(self._PDFfloat(k - 1))
            nums.append(self._PDFdict({self._PDFname("S"): self._PDFname("D"), self._PDFname("St"): self._PDFfloat(p)}))
        labels = self._PDFdict({self._PDFname("Nums"): nums})
        self._w._root_object.update({self._PDFname("PageLabels"): labels})
        # Alternative method: manually edit file and fix xref table with pdftk
        # # Create new string
        # s = "\n/PageLabels << /Nums ["
        # s = s + " 0 << /S /r >>\n"
        # for k, p in pagination.items():
        #     s = s + str(k - 1) + " << /S /D /St {} >>\n".format(p)
        # s = s + "]\n>>"
        # # Replace string in file
        # self._f.seek(0)
        # t = self._f.read() # TODO: avoid to read file into memory
        # t = re.sub(b"/Type/Catalog", lambda x: x.group(0) + bytes(s, "utf8"), t)
        # # Write file
        # with NamedTemporaryFile(mode="wb") as f:
        #     f.write(t)
        #     # Fix broken xref table
        #     _, f2 = mkstemp()
        #     call(["pdftk", f.name, "output", f2])
        #     self.close()
        #     self.__init__(f2)

    def _PDFname(self, s):
        return pyPDF.NameObject("/" + s)

    def _PDFfloat(self, f):
        return pyPDF.FloatObject(f)

    def _PDFdict(self, d):
        return pyPDF.DictionaryObject(d)

    def writeOutline(self, outline):
        """
        Adapted from https://github.com/psammetichus/PDF-Add-Outline
        (add in particular the support of depth)
        """
        self._w.setPageMode("/UseOutlines")
        self._addOutline(self._w, outline)

    def _page(self, name, page, pdfw, idorefs, previous, next, parent=None, first=None, last=None, children=None):
        """
        General page
        """
        if parent is None:
            parent = -1
        oli = pyPDF.DictionaryObject({self._PDFname("Title"): pyPDF.TextStringObject(name),
                                      self._PDFname("Parent"): idorefs[parent + 1],
                                      self._PDFname("Dest"): self._makeDest(pdfw, page)})
        if first is not None:
            oli.update({self._PDFname("First"): idorefs[first + 1]})
        if last is not None:
            oli.update({self._PDFname("Last"): idorefs[last + 1]})
        if children is not None:
            oli.update({self._PDFname("Count"): pyPDF.NumberObject(-1 * children)})
        if previous is not None:
            oli.update({self._PDFname("Prev"): idorefs[previous + 1]})
        if next is not None:
            oli.update({self._PDFname("Next"): idorefs[next + 1]})
        return oli

    def _parentPage(self, name, page, children, pdfw, idorefs, first, last, previous, next):
        return self._page(name, page, pdfw, idorefs, previous, next, -1, first, last, children)

    def _regularPage(self, name, page, parent, pdfw, idorefs, previous, next):
        return self._page(name, page, pdfw, idorefs, previous, next, parent)

    def _addOutlineItems(self, pdfw, outline, idorefs):
        """
        Add items to outline
        """
        olitems = []
        for i, n in enumerate(outline.nodes()):
            if outline.lastchild(i) is None:
                olitems.append(
                    self._regularPage(n["name"], n["page"] - 1, outline.parent(i), pdfw, idorefs, outline.previous(i), outline.next(i)))
            else:
                olitems.append(
                    self._parentPage(n["name"], n["page"] - 1, len(list(outline.children(i))), pdfw, idorefs, outline.firstchild(i),
                                     outline.lastchild(i), outline.previous(i), outline.next(i)))
        return olitems

    def _addOutline(self, pdfw, outline):
        """
        Add outline
        """
        # References
        idorefs = [pyPDF.IndirectObject(x + len(pdfw._objects) + 1, 0, pdfw) for x in range(outline.size() + 1)]
        # Add outline dict to pdf obj
        pdfw._addObject(pyPDF.DictionaryObject({self._PDFname("Type"): self._PDFname("Outlines"),
                                                self._PDFname("First"): idorefs[1],
                                                self._PDFname("Last"): idorefs[-1],
                                                self._PDFname("Count"): pyPDF.NumberObject(outline.size())}))
        for i in self._addOutlineItems(pdfw, outline, idorefs):
            pdfw._addObject(i)
        # Change catalog
        pdfw._root_object.update({self._PDFname("Outlines"): idorefs[0]})

    def _makeDest(self, pdfw, pg):
        d = pyPDF.ArrayObject()
        d.append(pdfw.getPage(pg).indirectRef)
        d.append(self._PDFname("XYZ"))
        for i in range(0, 3):
            d.append(pyPDF.NullObject())
        return d
