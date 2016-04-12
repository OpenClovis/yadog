"""?
<desc>This module extracts documentation from text files</desc>
"""
from types import *
import pdb
import ast
import re

from PyHtmlGen.document import *

from common import *
import microdom

from constants import *
      

def extractXml(prjPfx, filename):
  
  print "Parsing %s" % filename
  try:
    f = open(filename,"rb")
  except IOError:  # A broken symlink could cause this to be unopenable even though the directory entry exists
    print "Cannot open %s" % filename
    return ""

  text = f.read()

  if filename.startswith(prjPfx):
    filename = filename[len(prjPfx):]   

  xmltxt = "<%s name='%s' language='text'>" % (TagFile,filename) + text + "</%s>" % TagFile

  try:
    xml = microdom.parseString(xmltxt)
  except microdom.ExpatError,e:
    print "File %s: XML ERROR '%s'" % (filename,str(e))
    f = open("error.xml","wb")
    f.write(xmltxt)
    f.close()
    print "Errored file written to 'error.xml'"
    # print xmltxt
    pdb.set_trace()
    
  return xml


def Test():
  xml = extractXml("readme.txt")
  #- xml = extractXml("microdom.py")

if __name__ == "__main__":
    Test()

