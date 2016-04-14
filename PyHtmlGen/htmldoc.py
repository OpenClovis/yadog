import pdb
from types import *

from gen import *
from attr import *

from document import *
from chunk import *

LocationRoot = 1
LocationMe   = 2
LocationBoth = LocationRoot | LocationMe

def OTagify(s):
  if s:
    return "<%s>" % s
  else: return ""

def CTagify(s):
  if s:
    return "</%s>" % s.split(" ")[0]
  else: return ""

class HtmlSkel(Doc):
  def __init__(self,parent=None,prefix="",htmlTag="html",headTag="head",bodyTag="body"):
    Doc.__init__(self)

    self.body       = self.NewMarker("body")
    self.parent     = parent
    self.scratchPad = {}
    self.styleSheets = []
    
    if prefix is not None:
      # The current position marker is the only one that should be overridden
      if not parent:
        self.head       = self.NewMarker("head")
        self.style      = self.NewMarker("style")
        self.Insert(prefix,Start,Before)
        self.Insert([chunkStr(OTagify(headTag)),self.head,chunkStr("<style type='text/css'>"),"\n#nothing {}\n",self.style,chunkStr("</style>%s" % CTagify(headTag))],Start,After)
        self.Insert([chunkStr(OTagify(bodyTag)),self.body,chunkStr(CTagify(bodyTag))],End,Before)
        self.Insert([chunkStr(OTagify(htmlTag))],Start,Before)
        self.Insert([chunkStr(CTagify(htmlTag))],End,After)
      else:
        self.head       = parent.head
        self.style      = parent.style
        self.Insert([self.body],End,Before)

  def HasModule(self,s,location=LocationBoth):
    ret = 0
    if self.parent and location&LocationRoot:
      ret = ret | self.parent.HasModule(s)
    if location&LocationMe:
      ret = ret | (s in self.__dict__)
    return ret

  def SubDocFactory(self):
    return HtmlSkel(self)
    

  unused = """
  def AddScript(loToks):
    if type(loToks) is not type([]):
      loToks = [loToks]

    if not self.HasModule("js"):
      self.js = self.NewMarker("javaScript")
      self.Insert(["<script language='JavaScript'>\n",self.js,"</script>\n"],self.head,After)

    self.Insert(loToks,self.js,Before)
  """

  # The content of a module is a list of (modules and content to insert in those modules)
  def AddModule(self,module, where=LocationRoot):
    """Add a module into this document.  A module is a chunk of text that has to occur exactly once"""
    #print "AddModule: %s" % str(module)

    if where&LocationRoot and self.parent: self.parent.AddModule(module)

    # If the user explicitly wants to load the module in this document, or
    # there is no parent, and
    # the document is not already loaded
    if (where&LocationMe or not self.parent) and not self.HasModule(module[0],LocationMe): 
      (name,NewMarkers,content) = module

      for (mod,info) in content:
        #print "LINK ", mod
        #if not mod in self.__dict__:
        if not mod in self.markers:
          print "Link %s not found; Cannot insert module %s." % (mod, module[0]) 
          return false

      # Add any markers this module defines into this class.
      self.__dict__[name] = NewMarkers
      self.NewMarker(name)

      #print "Content", content
      for (mod,info) in content:
        # print "Module adding to '%s', Adding %s" % (mod,info)
        marker = self.__dict__[mod]  # Find the marker from its name
        if type(info) is not type([]): info = [info]
        self.Insert(info,marker,Before)
      
    return true

  def AddStyleSheet(self,fil):
    if not fil in self.styleSheets:
      self.styleSheets.append(fil)
      self.Insert([chunkStr('<link rel="stylesheet" type="text/css" href="%s" />' % fil)],self.head,After)

class HtmlFragment(HtmlSkel):
  """? This describes a file that is just a chunk of HTML, not a full HTML document.
  Its purpose is to be loaded and included in a full document either by javascript or by server-side scripting
  """
  def __init__(self,parent=None,prefix=" ",htmlTag="div",headTag=None,bodyTag=None):
    HtmlSkel.__init__(self,parent,prefix,htmlTag,headTag,bodyTag)



class DocHtmlSections(DocSections):
  def __init__(self,name=None):
    DocSections.__init__(self,name=name)
    self.body       = self.NewMarker("body")
    self.head       = self.NewMarker("head")
    self.style      = self.NewMarker("style")
    self.parent     = None

  def HasModule(self,s,location=LocationBoth):
    ret = 0
    if self.parent and location&LocationRoot:
      ret = ret | self.parent.HasModule(s)
    if location&LocationMe:
      ret = ret | (s in self.__dict__)
    return ret
 
  def AddStyleSheet(self,fil):
    if not fil in self.styleSheets:
      self.styleSheets.append(fil)
      self.Insert([chunkStr('<link rel="stylesheet" type="text/css" href="%s" />' % fil)],self.head,After)

  # The content of a module is a list of (modules and content to insert in those modules)
  def AddModule(self,module, where=LocationRoot):
    """Add a module into this document.  A module is a chunk of text that has to occur exactly once"""

    if where&LocationRoot and self.parent: self.parent.AddModule(module)

    # If the user explicitly wants to load the module in this document, or
    # there is no parent, and
    # the document is not already loaded
    if (where&LocationMe or not self.parent) and not self.HasModule(module[0],LocationMe): 
      (name,NewMarkers,content) = module

      for (mod,info) in content:
        #print "LINK ", mod
        #if not mod in self.__dict__:
        if not mod in self.markers:
          print "Link %s not found; Cannot insert module %s." % (mod, module[0]) 
          return false

      # Add any markers this module defines into this class.
      self.__dict__[name] = NewMarkers
      self.NewMarker(name)

      #print "Content", content
      for (mod,info) in content:
        #print "Module adding to '%s', Adding %s" % (mod,info)
        marker = self.__dict__[mod]  # Find the marker from its name
        if type(info) is not type([]): info = [info]
        self.Insert(info,marker,Before)
      
    return true




def Test():
  
  def xf(item):
    return "pfx:" + str(item)

  doc = HtmlSkel()

  doc.AddXform(StringType,xf)
  doc.AddStyleSheet("style.css")
  doc.genDoc(["hello", "there", 1])

  print str(doc)


