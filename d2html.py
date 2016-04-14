"""?? This file is the engine that converts the xml to html
"""
import pdb
import os
import types

from common import *

import microdom

#? <section name="Helper Functions">

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
