from datetime import datetime as dt
from datetime import date
import datetime
import csv
from pdf2image import convert_from_path
from PIL import Image
import os
import tempfile

def add_kort2(billedefil, filNavn, path):

    #path2 = os.getcwd()
    #path2 = path
    with tempfile.TemporaryDirectory(dir = path) as nytdir:
        #headTail = billedefil.filename
        #head = (headTail.split(sep="."))[0]
        #fil_resultater = os.path.join(nytdir, 'tempkonvert.jpg')
        #with billedefil as fil_resultater:
        images = convert_from_path(billedefil, poppler_path=r'C:\Users\sba\OneDrive\Dokumenter\Python40\poppler\bin')
        for i in range(len(images)):
            nytfilnavn = filNavn + '.jpg'
            outfile = os.path.join(path, nytfilnavn)
            images[i].save(outfile, dpi=(300, 300))

        #jpegkonfil = anvil.media.from_file(outfile, "image/jpeg")
    return nytfilnavn

def add_billede(billedefil, filNavn, path):
    path2 = path
    with tempfile.TemporaryDirectory(dir = path2) as nytdir:
        #headTail = billedefil.filename
        #head = (headTail.split(sep="."))[0]
        fil_resultater = os.path.join(nytdir, 'tempkonvert.png')
        with billedefil as fil_resultater:
            images = convert_from_path(fil_resultater)
            for i in range(len(images)):
                nytfilnavn = filNavn + '.png'
                outfile = os.path.join(path, nytfilnavn)
                images[i].save(outfile, dpi=(300, 300))

        #jpegkonfil = anvil.media.from_file(outfile, "image/jpeg")
    return outfile