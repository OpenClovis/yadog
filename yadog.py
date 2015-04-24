"""?? YaDoG: Yet Another DOcumentation Generator.
This is the top-level "main" file for YaDoG.
"""

import pdb
import sys
import os.path
import types

import microdom
import dp
import dc
import dt
import d2html

from constants import *

import sys


def info(type, value, tb):
   """?? This function is an exception hook (sys.excepthook) that automatically starts the debugger in postmortem mode if there is a tty"""
   if hasattr(sys, 'ps1') or not sys.stderr.isatty():
      # we are in interactive mode or we don't have a tty-like
      # device, so we call the default hook
      sys.__excepthook__(type, value, tb)
   else:
      import traceback, pdb
      # we are NOT in interactive mode, print the exception...
      traceback.print_exception(type, value, tb)
      print
      # ...then start the debugger in post-mortem mode.
      pdb.pm()

sys.excepthook = info


def fileWalkFlatten(oswalk, butnot=None):
  if butnot is None: butnot = []
  f = []
  for (path,dnames,fnames) in oswalk:
    cnt = 0
    # eliminate specified directories
    while cnt < len(dnames):
      if dnames[cnt] in butnot:
        del dnames[cnt]
      else: cnt+=1

    for fil in fnames:
        f.append(os.path.join(path,fil))
  return f

oldcfg={"sections":["section","file","class","fn","var"],
     "html":
       {
       "pageimplementers": {"class":"classpage","file":"filepage"},
       "indeximplementers": { "class":"classindexpage","fileindex":"fileindexpage"}
       }
     }

#js
yadogcfg={"project":{'name':'YaDoG: Yet Another Documentation Generator','version':'0.0.1.0','date':"Oct 29,2009",'author':"G. Andrew Stone",'homepage':None},
     "sections":["section","file","class","fn","var"],
     "html":
       {
       "dir":"layouts/basicJson",
       "skin":"yadogskin",
       "pageimplementers": {"class":"jsclasspage","file":"jsfilepage"},
       "nav": [ ("home","jshome"),("search","jssearch"),("idx","jsindex") ],
       "indeximplementers": { "class":"jsclassindexpage","file":"jsfileindexpage","section":"jssectionindespage"},
       "quicklists": {"History":"jsqhist","Sections":"jsqsec","Classes":"jsqclass","Files":"jsqfile"},
       "misc": { "frame":"jsframe"}
       }
     }

juicedPyShellcfg={"project":{'name':'Juiced PyShell: A blending of Firefox and Python','version':'0.0.7.0','date':"Jan 13,2010",'author':"G. Andrew Stone",'homepage':None},
     "sections":["section","file","class","fn","var"],
     "html":
       {
       "dir":"layouts/basicJson",
       "skin":"juicedskin",
       "pageimplementers": {"class":"jsclasspage","file":"jsfilepage"},
       "nav": [ ("home","jshome"),("Examples","jssection",("Examples",)), ("search","jssearch"),("idx","jsindex") ],
       "indeximplementers": { "class":"jsclassindexpage","file":"jsfileindexpage","section":"jssectionindexpage"},
       "quicklists": {"History":"jsqhist","Sections":"jsqsec","Classes":"jsqclass","Files":"jsqfile"},
       "misc": { "frame":"jsframe"}
       }
     }

Lightuinocfg={"project":{'name':'Lightuino: An Arduino compatible for LEDs (and more)','version':'2.0.1.0','date':"Feb 8,2010",'author':"G. Andrew Stone",'homepage':None},
     "sections":["section","file","class","fn","var"],
     "html":
       {
       "dir":"layouts/basicJson",
       "skin":"lightuinoskin",
       "pageimplementers": {"class":"jsclasspage","file":"jsfilepage"},
       "nav": [ ("home","jshome"),("examples","jssection",("examples",)), ("search","jssearch"),("idx","jsindex") ],
       "indeximplementers": { "class":"jsclassindexpage","file":"jsfileindexpage","section":"jssectionindexpage"},
#       "quicklists": {"History":"jsqhist","Sections":"jsqsec","Classes":"jsqclass","Files":"jsqfile"},
       "misc": { "frame":"jsframe"}
       }
     }


def split(selFn,lst):
  a = []
  b = []
  for l in lst:
    if selFn(l): a.append(l)
    else: b.append(l)
  return (a,b)

def regularize(node,zzdepth=0):
  """?? This function ensures that the tree is complete and regular.  For example it breaks descriptions into brief and desc tags.
  """

  if 0: # Print the nodes
    try:
      t = node.pfxsfx()
      print "**" + ("  " *zzdepth) + t[0]
    except AttributeError:
      print "**" + str("  " *zzdepth) + str(node)

  # Regularize the children      
  try:
    children = node.children_
  except AttributeError:
    children = []
  
  for c in children:
    regularize(c,zzdepth+1)

  # Combine common children (in this case sections with the same name)
  lkup = {}
  for c in children:
    if microdom.isInstanceOf(c,microdom.MicroDom) and c.tag_ in CombinedTags: # It is a candidate to be merged
      if lkup.has_key(c.tag_ + c.name): # Yes there is another tag, so it must be merged
        orig = lkup[c.tag_ + c.name]
        orig.merge(c)
      else:
        lkup[c.tag_ + c.name] = c
          
  

  if microdom.isInstanceOf(node,microdom.MicroDom):

    # Add an empty "type" attribute if it does not have one
    if node.tag_ in TypedTags:
       if not node.attributes_.has_key(AttrType):
         node.attributes_[AttrType] = ""      

    if node.tag_ in ConstructTags:
     #print str(node)

     # Regularize the "brief" and "desc" children

     if not node.child_.has_key(TagDesc):
       # Split the children into who should go under the desc and who should go back under me 
       chLst = node.removeChildren()
       (descChildren,myChildren) = split(lambda x: (not microdom.isInstanceOf(x,microdom.MicroDom)) or (not x.tag_ in NoDescTags)  ,chLst)
       #descChildren = filter(lambda x: (not microdom.isInstanceOf(x,microdom.MicroDom)) or (not x.tag_ in NoDescTags)  ,node.children_)
       #myChildren   = filter(lambda x: not((not microdom.isInstanceOf(x,microdom.MicroDom)) or (not x.tag_ in NoDescTags))  ,node.children_)
 
       # Reset me with new children (but all else the same)
       #node.reset(node.attributes_,myChildren,None,node.parent_)
       for c in myChildren:
         node.addChild(c)
       # Add the Desc tag
       node.addChild(microdom.MicroDom({"tag_":TagDesc},descChildren,None,node))
       #node.addChild(microdom.MicroDom({"tag_":TagDesc},[],None,node))
       
       
     if not node.child_.has_key(TagBrief):
       tdesc = node.child_[TagDesc].dumpChildren()
       # candidate = node.data_.split("\n")[0].split(". ")[0]  # Get the first sentence in the first line
       candidate = tdesc.split("\n")[0].split(". ")[0]  # Get the first sentence in the first line
       if candidate: # If there is something then use it as the brief
         brief = candidate + "..."
       else:  # Or use the 1st sentence of the description
         brief = node.child_[TagDesc].data_.split(". ")[0] + "..."   
       t = microdom.MicroDom({"tag_":TagBrief},[brief],None)
       node.addChild(t)


     # If there is no "decl" then use the name
     # TODO: we could search for TagParam children to build the declaration
     # But really dp.py should generate the decl
     if node.tag_ in [TagFunction,TagMethod]:
       if not node.child_.has_key(TagDecl):
         t = microdom.MicroDom({"tag_":TagDecl},[node.name],None)
         node.addChild(t)
      
  return node

def go(prjPfx, allfiles, cfg):
  allxml = []
  for f in allfiles:
    ext = os.path.splitext(f)[1]
    if ext == ".py":
      allxml.append(dp.extractXml(prjPfx,f))
    elif ext in [".h",".hpp",".hxx",".c",".pde"]:  # .pde is Arduino
      allxml.append(dc.extractXml(prjPfx,f))
    elif ext in [".txt"]:
      allxml.append(dt.extractXml(prjPfx,f))
      
      
  xml = microdom.Merge("doc",allxml)

  pp = xml.write()
  f = open("rawdocout.xml","wb")
  f.write(pp)
  f.close()

  print "Regularize:"
  regularize(xml) 
  print "Regularize Complete:"

  try:
    os.makedirs("html")
  except OSError,e:  # File exists is ok
    pass

  pp = xml.write()
  f = open("docout.xml","wb")
  f.write(pp)
  f.close()

  d2html.gen("html",xml,cfg)


def genPaths(directories,butnot, cfg,prjPfx):
  allfiles = []
  for d in directories:
    allfiles += fileWalkFlatten(os.walk(d),butnot)
  go(prjPfx, allfiles,cfg)

def main(prjPfx, top,butnot, cfg):
  allfiles = fileWalkFlatten(os.walk(prjPfx + top),butnot)
  go(prjPfx, allfiles,cfg)

def Test():
  #pdb.set_trace()
  main("/me/hw/arduino/arduino-m5451-current-driver/latest/lightuino/", "", None, Lightuinocfg)
  # main("/me/code/", "juicedpyshell", None, juicedPyShellcfg)
  #main("/me/code/", "yadog",["kid"],yadogcfg)
#  main(".")

if __name__ == "__main__":
  top = sys.argv[1]
  main(top)

