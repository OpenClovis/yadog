"""?? This file is the engine that converts the xml to html
"""
import pdb
import os
import types

from common import *
from constants import *
from htmlcommon import *
import microdom

#? <section name="Helper Functions">

def resolveRef(obj,tagDict):
  """?? resolves the reference described by obj"""
  try:
    searchString = obj.ref
  except AttributeError:
    searchString = obj.data_

  mustBeFn = False
  if searchString[-2:] == "()":
    searchString = searchString[:-2]
    museBeFn = True
  if ":" in searchString:
    srchLst = searchString.split(":")
  elif "." in searchString:
    srchLst = searchString.split(".")
  else:
    srchLst = [searchString]

  s = srchLst[0]
  loc = obj.parent_
  match=None
  top = None
  while loc and not match:
    top = loc
    match = loc.findByAttr({"name":s})
    if not match:
      match = loc.findByAttr({"tag_":s})
      if not match:
        loc = loc.parent_

  if not match:
    files = tagDict[TagFile]
    for f in files:  # Files have a . and could have directories so need to be specially handled
      if searchString in f.name:  
        match = f
        break
  else:
    match = match[0][1]

  if not match: return None

  for s in srchLst[1:]:
    pass # TODO

  return match

def writeChildrenPatch(self,indent):
  #pdb.set_trace()
  #print self
  d = self.oldWriteChildren(indent)
  ret = refobj2tlink(self.ref_,"'center'",text=d)  # TODO this should call a global function pointer that the renderer can set
  return ret

def resolveAllRefs(xml,tagDict):
  """?? Adds the target of all references in a microdom tree to the object in the tree
  """
  for node in xml.walk():
    if isInstanceOf(node,microdom.MicroDom):
      if node.tag_ == TagRef:
        tgt = resolveRef(node,tagDict)
        if not tgt:
          fil = node
          while fil and fil.tag_ != TagFile:
            fil = fil.parent_
          line = node.linenum if hasattr(node,"linenum") else "0"
          print "Unresolved ref %s at %s:%s" % (node.data_,fil.name,line)
          node.ref_ = None

        else:
          print "Resolved: %s to %s" % (node.dump(), tgt.name)
          node.ref_ = tgt
          node.oldWriteChildren = node.writeChildren
          node.writeChildren = types.MethodType(writeChildrenPatch,node)

def genTagDict(xml):
  """?? Converts a <ref>microdom</ref> tree into a dictionary of key: tag names, value: list of objects
  """
  tags = {}
  for node in xml.walk():
    if isInstanceOf(node,microdom.MicroDom):
      lst = tags.get(node.tag_,None)
      if lst is None:
        lst = []
        tags[node.tag_] = lst          
      lst.append(node)
  return tags

generEnv = globals()

def importAndRun(modul,cmdlst):
  try:
    print "Running module %s" % modul
    exec "import %s" % modul in generEnv
    for (c,locals) in cmdlst:
      (filename,html) = eval (c,generEnv,locals)
      #print "Generated %s" % filename
  except ImportError, e:
    print "Missing or Errored module: %s" % modul
    print "Import exception: %s" % str(e)

#? </section>

def gen(direc,xml,cfg):
  """?? Generate html from microdom.
  <arg name='direc'>Unused</arg>
  <arg name='xml'>The root of the microdom tree</arg>
  <arg name='cfg'>Configuration dictionary</arg>

  <desc>
  This function drives the generation of the html documentation given a microdom tree.  This tree is generally (but not necessarily) created by parsing source code.  The html generation is customized through the cfg object.  Here is an example of this object:
  Example configuration:
  <html><pre>
  cfg={"project":{'name':'YaDoG: Yet Another Documentation Generator','version':'0.0.1.0','date':"Oct 29,2009",'author':"G. Andrew Stone",'homepage':None},
     "sections":["section","file","class","fn","var"],
     "html":
       {
       "dir":"layouts/basicJson",
       "skin":"yadogskin",
       "pageimplementers": {"class":"jsclasspage","file":"jsfilepage"},
       "indeximplementers": { "search":"jssearch","idx":"jsindex","class":"jsclassindexpage","file":"jsfileindexpage"},
       "quicklists": {"History":"jsqhist","Sections":"jsqsec","Classes":"jsqclass","Files":"jsqfile"},
       "misc": { "home":"jshomepage"}
       }
     }
  </pre></html>
  </desc>
  """
  htmlcfg = cfg["html"]
  tagDict = genTagDict(xml)
  resolveAllRefs(xml,tagDict)
  # print "TAGS:",tagDict.keys()

  # Add the layout path to the environment so we can load the modules
  if htmlcfg.has_key("dir"):
    es = "import sys; sys.path.append('%s')\n" % htmlcfg["dir"]
    log.debug("Running: %s" % es)
    exec es in generEnv

  # Generate the top level page
  for (k,v) in htmlcfg["misc"].items():
    log.info("Generating '%s' using module '%s'" % (k,v))
    importAndRun(v,[("%s.generate(obj,cfg,args,td)" % v,{"obj":xml,"cfg":cfg,"args":None,"td":tagDict})])
    

  # Generate the lowest level pages
  for sect in cfg["sections"]:
    if tagDict.has_key(sect):
      # Look up the page implementation for this section
      pi = htmlcfg["sectionPageImplementers"].get(sect,htmlcfg["sectionPageImplementers"].get(sect.capitalize(),None))
      if pi:
        (name,filename,code,args) = parseCfgEntry(pi,sect)
        # importAndRun(code,[("%s.generate(obj,cfg)" % code,{"obj":obj,"cfg":cfg}) for obj in tagDict[sect]])
        importAndRun(code,[("%s.generate(obj,cfg,args,td)" % code,{"obj":obj,"cfg":cfg,"args":args, "td":tagDict}) for obj in tagDict[sect]  ])

      pi = htmlcfg["sectionIndexImplementers"].get(sect,htmlcfg["sectionIndexImplementers"].get(sect.capitalize(),None))
      if pi:
        (name,filename,code,args) = parseCfgEntry(pi,sect)
        importAndRun(pi,[("%s.generate(obj,cfg,args,td)" % pi,{"obj":tagDict[sect],"cfg":cfg,"args":args, "td":tagDict}) ])

  #for name,val in htmlcfg["indeximplementers"].items():
  #  log.info("Generating '%s' using module '%s'" % (k,v))
  #  importAndRun(v,[("%s.generate(obj,cfg,args,td)" % v,{"obj":xml,"cfg":cfg,"args":None, "td":tagDict})])

  for nav in htmlcfg["nav"]:
    if type(nav) is types.DictType:
      name = nav["name"]
      filename = nav.get("file", name)
      pi = nav["gen"]
      args = nav.get("args", None)
    else:
      name = nav[0]
      pi = nav[1]
      if len(nav) > 2:
        args = nav[2]
      else:
        args = None
    importAndRun(pi,[("%s.generate(obj,cfg,args,tagDict)" % pi,{"obj":xml,"cfg":cfg,"args":args,"tagDict":tagDict})])


def parseCfgEntry(nav,name=None):
 
    if type(nav) is types.DictType:
      name = nav["name"]
      filename = nav.get("file", name)
      pi = nav["gen"]
      args = nav.get("args", None)
    elif type(nav) is types.TupleType:
      name = nav[0]
      pi = nav[1]
      if len(nav) > 2:
        args = nav[2]
      else:
        args = None
    else:  # just a string
      pi = nav
      args = None
      filename = name

    return (name,filename,pi,args)
