import pdb

import os.path

from constants import *
from common import *

import microdom

def filenameify(s):
  s = s.replace(" ","_")
  return s

def htmlify(s):
  s = s.replace(" ","_")
  return s

def render(obj):
  if isInstanceOf(obj,microdom.MicroDom):
    if obj.tag_ == "html":
      return obj.write()
    else:
      return obj.writeChildren()
  else: return str(obj)


def obj2file(obj):
  p = obj.findParent(TagsWithOwnFile)  # Find a parent object by tag for a tag that has its own .html file
  if p: p = p[0]
  else: p = obj

  n = os.path.basename(p.name)  # Behave like the name is a file to automatically rip off anything that would seem like a directory (and besides, it MAY be a file)  
  return p.tag_ + "_" + n + ".html"

def obj2anchor(obj):
  if obj.tag_ in TagsWithOwnFile:
    return "top"
  p = obj.findParent(TagsWithOwnFile)[0]
  t = obj
  name = []
  while t != p:
    try:
      portion = t.name
      name.insert(0, htmlify(portion))
    except:  # skip if t.name does not exist
      pass
    t = t.parent_
  return "_".join(name)

def obj2link(obj,loadFile=None):
  if loadFile is None: loadFile = obj2file(obj)
  return "<a href='%s'>%s</a>" % (loadFile,obj.name)

def obj2tlink(obj,replacement,text=None,loadFile=None):
  if not obj: return ""
  if not text: text = obj.name
  if replacement[0] != "'":
    pdb.set_trace()
  if loadFile is None: loadFile = obj2file(obj)
  # return """<span onClick="ReplaceChildrenWithUri(%s,'%s'); location.hash='%s';" onMouseout="this.setAttribute('style','');" onMouseover="this.setAttribute('style','color:Blue;');">%s</span>""" % (replacement,loadFile,obj2anchor(obj),text)
  return """<a class='invis' onclick="ReplaceChildrenWithUri(%s,'%s'); location.hash='%s'; return false;" href="%s">%s</a>""" % (replacement,loadFile,obj2anchor(obj),loadFile, text)

def refobj2tlink(obj,replacement,text=None,loadFile=None):
  if not obj: return ""
  if not text: text = obj.name
  if replacement[0] != "'":
    pdb.set_trace()
  if loadFile is None: loadFile = obj2file(obj)
  return """<a onclick="ReplaceChildrenWithUri(%s,'%s'); location.hash='%s'; return false;" href="%s">%s</a>""" % (replacement,loadFile,obj2anchor(obj),loadFile, text)

  # return """<span onClick="ReplaceChildrenWithUri(%s,'%s'); location.hash='%s';" onMouseout="this.setAttribute('style','');" onMouseover="this.setAttribute('style','color:Yellow;');">%s</span>""" % (replacement,loadFile,obj2anchor(obj),text)

def parenttLink(obj,tag,rep):
  # Figure out the upwards links
  fileobj = obj.findParent(tag)
  if fileobj: f = obj2tlink(fileobj[0],rep)
  else: f = ""
  return f

def parentLink(obj,tag):
  # Figure out the upwards links
  fileobj = obj.findParent(tag)
  if fileobj: f = obj2link(fileobj[0])
  else: f = ""
  return f
