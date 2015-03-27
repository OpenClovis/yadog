import pdb
from gen import *
from document import *
from htmldoc import *
from chunk import *
from attribute import *
from imagehtml import *

try:
  import Image
except ImportError:
  pass

"""
    for x in self.im:
      x.styles["position"] = "absolute"
      x.styles["top"]  = length(0,"px")
      x.styles["border"]  = 0
  
    self.im[self.Left].styles["z-index"]    = 2
    self.im[self.Stretch].styles["z-index"] = 0
    self.im[self.Right].styles["z-index"]   = 1

    self.im[self.Left].styles["left"]       = length(0,"px")
    self.im[self.Stretch].styles["left"]    = length(0,"px")
    self.im[self.Right].styles["right"]     = length(0,"px")

    self.im[self.Stretch].styles["width"]    = length(100,"%")
    self.im[self.Stretch].styles["height"]    = length(self.im[self.Stretch].size[1],"px")
"""
 

  


class BarImages:
  """Creates a horizontal bar out of 3 images; a beginning, a stretchable middle, and and end"""
  Left = 0
  Stretch = 1
  Right = 2
  def __init__(self,Leftim,Stretchim,Rightim, myId = None):
    # id is a global var that you can override
    self.id   = myId
    if self.id is None:
      self.id   = GenUniqueId("BarImages")
    self.im = cvt2Image([Leftim,Stretchim,Rightim])
    
    self.maxheight = length(max([x.size[1] if x else 0 for x in self.im]),"px")

    self.relOrAbs = 'relative'
    
    if self.im[self.Left]: 
      p = self.im[self.Left]
      p.id = self.id + "Left"
      noOvr(p.styles,    [('position',self.relOrAbs),('z-index',2),('left',length(0,'px')),('top',length(0,'px')),('border',0)])
            
    if self.im[self.Stretch]:
      p = self.im[self.Stretch]
      p.id = self.id + "Center"
      noOvr(p.styles, [('position',self.relOrAbs),('z-index',0),('left',length(0,'px')),('top',length(0,'px')),('border',0),('width',length(100,'%')),('height',length(p.size[1],'px'))])

    if self.im[self.Right]:
      p = self.im[self.Right]
      p.id = self.id + "Right"
      noOvr(p.styles,    [('position',self.relOrAbs),('z-index',1),('right',length(0,'px')),('top',length(0,'px')),('border',0)])
    

  def gen(self,doc):
    s = "#%s { position:relative }\n" % (self.id)

    doc.Insert([chunkStr(s)],doc.style,Before)

    doc.Insert([chunkStr("<div %s>" % Kv("id",self.id))],doc.body,Before)
    genDoc(doc,self.im)
    doc.Insert(chunkStr("</div>"),doc.body,Before)
    # The last div throws in a real char with dimensions, so that this bar's dimensions become part of the document
    #doc.Insert([chunkStr("<div style='height:%s'>&nbsp;</div></div>"  % self.maxheight)],doc.body,Before)

bad = """
class BarStretchFailsMozilla:
  def __init__(self,Stretch,loItems):
    self.id   = GenUniqueId("BarStretch")
    self.imid = GenUniqueId("StretchImage")
    self.contentid = GenUniqueId("Content")
    self.imName = Stretch
    self.imidheight = length(Image.open(Stretch).size[1],"px")
    self.items = loItems
    

  def gen(self,doc):
    s = "#%s { position:relative ; background-color:transparent }\n#%s { position:absolute; left:0px; top:0px; width:100%%; height:%s; border:0; z-index:-1}\n#%s { position:absolute; left:0px; top:0px; z-index:0; background-color: transparent; color: rgb(255,0,0)  }\n" % (self.id,self.imid, self.imidheight, self.contentid)

    doc.Insert([chunkStr(s)],doc.style,Before)
    
    s = '<div %s><img %s src="%s" /><span %s>' % (Kv("id",self.id), Kv('id',self.imid), ImagePathFixup(self.imName),Kv('id',self.contentid))

    doc.Insert([chunkStr(s)],doc.body,Before)

    genDoc(doc,self.items)

    doc.Insert([chunkStr("</span></div>")],doc.body,Before)
"""

class BarRepeatClass:
  """Creates an image 'bar' with the image stretched across the entire distance"""
  def __init__(self,Stretch,loItems=[],height=None,myId = None):
    self.id   = myId
    if self.id is None:
      self.id   = GenUniqueId("BarRepeatClass")

    #self.imid = GenUniqueId("StretchImage")
    self.contentid = GenUniqueId("Content")
    self.imName = Stretch
    if self.imName is not None and height is None:
      self.imidheight = length(Image.open(Stretch).size[1],"px")
    else:
      self.imidheight = height
    self.items = loItems
    
  def SetHeightStretch(self,len):
    "Deprecated"
    self.imidheight = len

  def SetHeight(self,len):
    self.imidheight = len

  def gen_old(self,doc):
    s = "#%s { position:relative ; left:0px; top:0px; width:100%%; height:%s; border:0 }\n#%s {position:absolute; background-image:url('%s'); left:0px; top:0px; width:100%%; height:%s; border:0 }\n" % (self.id, self.imidheight, self.imid, ImagePathFixup(self.imName), self.imidheight)

    doc.Insert([chunkStr(s)],doc.style,Before)

    s = "<div %s><div %s>" % (Kv('id',self.id),Kv('id',self.imid))
    doc.Insert([chunkStr(s)],doc.body,Before)
    genDoc(doc,self.items)
    doc.Insert([chunkStr("</div></div>")],doc.body,Before)

  def gen(self,doc):
    s = "#%s { position:relative ; left:0px; top:0px; width:100%%; height:%s; background-image:url('%s'); border:0 }\n" % (self.id, self.imidheight, ImagePathFixup(self.imName))

    doc.Insert([chunkStr(s)],doc.style,Before)

    s = "<div %s>" % (Kv('id',self.id))
    doc.Insert([chunkStr(s)],doc.body,Before)
    genDoc(doc,self.items)
    doc.Insert([chunkStr("</div>")],doc.body,Before)


def BarRepeat(image, contents=None, attrs=None,styles=None,myId=None):
    if not styles: styles = {}
    if not styles.has_key("height"):
      im = cvt2Image(image)
      styles["height"] = "%spx" % im.size[1]

    item = Chunk(contents,attrs,styles,myId)
    BackImage(item, im, "x")
    return item

# Does not actually stretch the image
def BarStretch(image, contents=None, attrs=None,styles=None,myId=None):
    if not styles: styles = {}
    im = cvt2Image(image)
    if not styles.has_key("height"):
      styles["height"] = "%spx" % im.size[1]

    im.setStyles({"z-index":"0","width":"100%"})

    if contents:
      contents = Chunk(contents).setStyles({"position":"relative","z-index":"1","top": "-%s" % styles["height"]})
      item = Chunk([im, contents],attrs,styles,myId)
    else:
      im.setStyles(styles).setAttrs(attrs)
      if myId: im.id = myId
      item = im
    return item



class BarLmrStretch(BarRepeatClass):
  """Creates a horizontal bar out of 3 images; a beginning, a stretchable middle, and and end, and allows you to put other html in the middle"""
  def __init__(self,leftIm,midIm,rightIm,loItems,height=None):
    
    self.leftImage = cvt2Image(leftIm)
    self.leftImage.attrs['align'] = 'left'
    self.rightImage = cvt2Image(rightIm)
    self.rightImage.attrs['align'] = 'right'
    BarRepeatClass.__init__(self,midIm,[self.leftImage, self.rightImage] + loItems,height)


  


def Test():
  SetImagePathPrefix("./")

  pgname = "testbar.html"

  doc = HtmlSkel()
            
  hdef = BarImages("images/logo.png","images/topbarbk.png","images/logout.png")

  allbars = []

  pwind = Block(None,location(top,left,length(10),length(50),length(20),length(30),10),10*((5*"contents ") + BR),"fixed","scroll","red","images/clear.png")
  pop1 = AddHidden(pwind)

  PopLoc = Place()
#  ls = LinkShow(color(Color(0,0,0)," SHOW "),pwind,PopLoc)
#  lh = LinkHide(color(Color(0,0,0)," HIDE "),pwind)
#  sbar4 = BarStretch("images/bar1.png",[color(Color(255,0,0,0),"hidden"),"  Example.   ",anchor(pgname,"reload"),resize(3,[ls,lh]) ])
  sp = chunkStr(3*BR)

  leftim = ImageHtml("images/logo.png")
  leftim.attrs['align'] = 'left'
  rtim = ImageHtml("images/logout.png")
  rtim.attrs['align'] = 'right'
  sbar2 = BarStretch("images/topbarbk.png",[leftim,rtim,color(Color(255,0,0,0),"HI"),"  THERE.   ",anchor(pgname,"reload"),resize(3,[" SHOW "," HIDE "])])

  sbar3 = BarLmrStretch("images/logo.png","images/topbarbk.png","images/logout.png",[color(Color(255,0,0,0),"HI"),"  THERE.   ",anchor(pgname,"reload"),resize(3,[" SHOW "," HIDE "])])

  sbar = BarStretch("images/bar1.png",[color(Color(255,0,0,0),"HI"),"  THERE.   ",anchor(pgname,"reload"),resize(3,[" SHOW "," HIDE "]) ])

  #allbars.append( [sp,'BarImages(None,"images/bar1.png",None)',BarImages(None,"images/bar1.png",None),"Done"])

  #bar2 = BarStretchFailsMozilla("images/bar1.png",[color(Color(255,0,0,0),"HI"),"  THERE.   ",anchor(pgname,"reload")])


  allbars.append( ['BarRepeat',BarRepeat("images/bar1.png"),"BarRepeat bottom"])
  allbars.append([sp,'BarRepeatWithContents',BarRepeat("images/bar1.png",color(Color(255,255,255,0),"This will appear in the bar")),"BarRepeatWcontents bottom"])

  allbars.append([sp,'BarStretch',BarStretch("images/horizbarocean1.jpg",color(Color(255,255,255,0),"This will appear in the bar")),"BarStretch bottom"])
  allbars.append([sp,'BarStretchNoContent',BarStretch("images/horizbarocean1.jpg"),"BarStretch bottom"])

  allbars.append([sp,'BarImages',BarImages(None,"images/horizbarocean1.jpg",None),"BarImages bottom"])


  all = chunkBuffer([hdef,sp,PopLoc,sp,sbar2,sp,sbar3,sp,sbar,sp,allbars,pop1])
  #all = chunkBuffer(allbars)

  all.gen(doc)
          
  s = str(doc)           
  print s

  file = open('testbar.html','w')
  file.write(s)
  file.close


