from . import Outline
import utils


class Document(object):
    def __init__(self, filename):
        self._filename = filename
        self._f = open(filename, "rb")

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        self._f.close()

    def getHash(self):
        return utils.sha1_file(self._filename)

    def writeOutline(self, outline):
        """
        :type outline: Outline
        """
        return

    def repaginate(self, pagination):
        """
        Repagination of the document

        :param pagination: A dictionnary of the form {page : display page}
        """
        return

    def extract(self, page, density=300):
        """
        Extract page as image

        :param page: Page number
        """
        return

    def extractText(self, page):
        """
        Extract text embedded in page

        :param page: Page number
        """
        return

    def numberPages(self):
        """
        Returns number of pages of the document
        """
        return
    
    def write(self, filename):
        """
        Write document to file
        """
        return

