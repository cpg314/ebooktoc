from . import SegmenterOCR
from cv2 import imread, imwrite, cvtColor, threshold, getStructuringElement, dilate, findContours, boundingRect, COLOR_BGR2GRAY, MORPH_CROSS, THRESH_BINARY_INV, RETR_EXTERNAL, CHAIN_APPROX_NONE, INTER_CUBIC, resize
from tempfile import NamedTemporaryFile
import utils

class cv2Tesseract(SegmenterOCR):
    """
    Segment page with OpenCV and use tesseract from the command line
    """
    def __init__(self, tmpfile):
        SegmenterOCR.__init__(self, tmpfile)
        self.image = imread(tmpfile.name)
        self.w, self.h = self.image.shape[:2]
        
    def detectBlocks(self, region=None):
        """
        Inspired by http://stackoverflow.com/a/23556997/194594
        """
        image = self.image
        # Extract image
        if region is not None:
            image = utils.region(image, region)
        # Pre-processing
        # image = resize(image, None, fx=0.5, fy=0.5, interpolation = INTER_CUBIC)
        image = cvtColor(image, COLOR_BGR2GRAY)
        _, image = threshold(image, 150, 255, THRESH_BINARY_INV)
        kernel = getStructuringElement(MORPH_CROSS, (3, 3))
        image = dilate(image, kernel, iterations=15)  # or iterations=10
        # Find contours
        _, contours, _ = findContours(image, RETR_EXTERNAL, CHAIN_APPROX_NONE)
        self.blocks = []
        for contour in contours:
            [x, y, w, h] = boundingRect(contour)
            if region is not None:
                # Adjust coordinates
                x = x + region[0]
                y = y + region[1]
            self.blocks.append({"x": x, "y": y, "w": w, "h": h})
        super().detectBlocks()
        return

    def OCRBlock(self, b):
        tmpfiles = [NamedTemporaryFile(suffix=".jpg"), NamedTemporaryFile()]
        image2 = utils.region(self.image, b)
        imwrite(tmpfiles[0].name, image2)
        # Run tesseract
        mode = 6
        utils.call(["tesseract", tmpfiles[0].name, tmpfiles[1].name, "-psm", str(mode)])
        # Read results
        with open(tmpfiles[1].name + ".txt") as f:
            out = f.read()
        return self._cleanOCR(out)
