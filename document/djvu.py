from subprocess import Popen, PIPE
import utils

from .document import Document
from .pdf import PDF

class DJVU(Document):
    def __init__(self, filename):
        Document.__init__(self, filename)

    def close(self):
        return

    def writeOutline(self, output, outline):
    # print-outline
    #     Print the outline of the document. Nothing is printed if the document contains no outline. 
    # remove-outline
    #     Removes the outline from the document. 
    # set-outline [djvusedoutlinefile]
    #     Insert outline information into the document. The optional argument djvusedoutlinefile names a file containing the outline information. This file must contain data similar to what is produced by command print-outline. When the optional argument is omitted, the program reads the hidden text information from the djvused script until reaching an end-of-file or a line containing a single period.
    # http://www.ub-filosofie.ro/~solcan/wt/gnu/d/bdjv.html
        print("")

    def extract(self, page):
        utils.call(["ddjvu", "-format=pdf", "-page={}".format(page + 1), self._filename, "page.pdf"])
        p = PDF("page.pdf")
        return p.extract(0)

    def numberPages(self):
        p = Popen(["djvused", "-e", "n", self._filename], stdout=PIPE)
        out, err = p.communicate()
        return int(out)
