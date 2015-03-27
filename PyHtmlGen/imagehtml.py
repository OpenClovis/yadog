import pdb
import os

from gen import *
from document import *
from chunk import *
from attribute import *

try:
  import Image
except ImportError:  # PIL is not available under appengine
  class ImageC:
    def open(fname):
      return None
  Image = ImageC


def areaRect(url,x,y,x1,y1):
  return chunkStr("<area shape='rect' coords='%d,%d,%d,%d' href='%s' border='0'>" % (x,y,x1,y1,url) )

def areaPoly(url,loCoords):
  return chunkStr("<area shape='poly' coords='%s' href='%s' border='0'>" % (list2String(", ",loCoords),url) )

imagePrefix = ""
  
def SetImagePathPrefix(pfx):
  """Pass a string which is the base directory path to your image directory""" 
  # Note 1/15/2010 removed trailing os.sep; please add that into your pfx when calling
  global imagePrefix
  imagePrefix = pfx

def ImagePathFixup(image):
  """Internal function that takes an image filename and returns a string that is the appropriate directory name"""
  return imagePrefix + str(image)


class ImageSpec:
  def __init__(self,size,colBits,format):
    self.size = size
    self.col  = colBits
    self.format = format

  def __getitem__(self,idx):
    return self.size[idx]

class MapHtml:
  def __init__(self,loAreas):
    self.id    = genUniqueId("imMap")
    self.areas = loAreas

  def gen(self,doc):
    doc.Insert("<map name='%s' %s border='0'>\n" % (self.id, Kv('id',self.id)),doc.body,Before)

    genDoc(doc,self.areas)
      
    doc.Insert("</map>\n",doc.body,Before)
    

class ImageHtml(ChunkTag):
  def __init__(self, imname, pixmap=None,myId=None,localFileName=None):
    chunkTag.__init__(self,"img")
    self.id     = myId if myId else genUniqueId("img")
    self.name   = imname
    self.pixmap = pixmap
    if localFileName:
      try:
        self.im     = Image.open(localFileName)
      except IOError, e:
        print "WARNING: image %s format not understood or image not found" % imname
        self.im = None
    else:
      try:
        self.im     = Image.open(imname)
      except IOError, e:  # If the file isn't found try it relative to this directory, even though it may be specified relative to root
        try:
          self.im     = Image.open("." + imname)
        except IOError:
          print "WARNING: image %s not found!" % imname
          self.im = None

    if self.im: self.size   = self.im.size
    else: self.size = None
    self.mustSave = false
    self.sizeInBrowser = None

  def gen(self,doc):
    style = self.styleStr()
    
    if self.pixmap:
      self.pixmap.gen(doc)
      pixmapStr = " usemap='#%s'" % self.pixmap.id
    else:
      pixmapStr = ""

    # Tell the browser the image size to aid layout
    if self.sizeInBrowser:
      sz = [self.sizeInBrowser[0],self.sizeInBrowser[1]]
      if sz[0] is None:  # no X was given
        sz[0] = self.size[0] * sz[1] / self.size[1]
      if sz[1] is None:  # no Y was given
        sz[1] = self.size[1] * sz[0] / self.size[0]
    elif self.size:
      sz = self.size
    else: sz = None
#    sz = inlif(self.sizeInBrowser,self.sizeInBrowser,self.size)

    # Only set the picture size if it is not overridden, and we know the size
    if sz:
      if not (self.attrs.has_key('width') or self.styles.has_key('width')):
        self.attrs["width"] = sz[0]
      if not (self.attrs.has_key('height') or self.styles.has_key('height')):
        self.attrs["height"] = sz[1]
      
    if not style == "": doc.Insert("#%s {%s}\n" % (self.id, style), doc.style, Before)
    
    doc.Insert("<img %s src='%s'%s %s/>" % (Kv('id',self.id), ImagePathFixup(self.name), pixmapStr,self.attrStr()),doc.body,Before)
    if self.mustSave:
      self.save()

  def __str__(self):
    return ImagePathFixup(self.name)

  def browserSize(self,size):
    self.sizeInBrowser = size

  def resize(self,size):
    self.im = self.im.resize(size,inlif(dbgFast,Image.NEAREST, Image.BICUBIC))
    if not self.mustSave:
      self.name = None # Prevent accidental writing
    self.size = self.im.size
    self.mustSave = true

  def setname(self,fname):
    self.name = fname
    self.mustSave = true

  def save(self,fname=None):
    if not fname:
      fname = self.name
    if not dbgSkip:
      self.im.save(fname)
    self.name = fname
    self.mustSave = false
    
    
    

def cvt2Image(s):
  """Takes a filename or list of filenames and makes an (or a list of) image html object out of them"""
  if type(s) == type([]):
    return [ cvt2Image(x) for x in s]
  elif type(s) == type(""):
    return ImageHtml(s)
  else: return s  # If it already was of the image type -- I really should check that its not some other random type


def Test():
  LogoutButton = ImageHtml("images/logout.png",MapHtml([areaRect("testpage1.htm",1,1,50,20)]))
  TopbarBkg    = ImageHtml("images/topbarbk.png")

  doc = HtmlSkel()

  LogoutButton.gen(doc)
  TopbarBkg.gen(doc)

  f = open("tmp.html","w")
  f.write(str(doc))
  f.close()
 
  print str(doc)
  
