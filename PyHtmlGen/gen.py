import pdb
import inspect
from types import *


true  = 1
false = 0

curId = 0

# Debugging stuff
debug = 0 # 1
debugShowTableEdges = 0 # 1

dbgFast = true  # Lower quality, faster processing (on images for example)
# dbgSkip = true  # Skip stuff that I probably did in the last successful run (like generate smaller images)
dbgSkip = false

# Default screen size - YUCK, can we query using javascript and then fix up?
scrnSize = (1024,768)  

BR = "<br/>"
HR = "<hr/>"

idLst = {}

def isInstanceOf(obj,objType):
  """Is the object an instance (or derived from) of the class objType)?"""
  if type(obj) is InstanceType and objType in inspect.getmro(obj.__class__): return True
  return False


def inlif(cond,tru,fal):
  """Inline 'if' statement.  But note that both tru and fal are actually evaluated"""
  if cond: return tru
  return fal

def Kv(key,val):
  ret = "%s='%s'" % (str(key),str(val))
  return ret  

def GenUniqueId(s="i",num=None):
  return genUniqueId(s,num)

def genUniqueId(s=None,num=None):
  """Returns a unique id.  
     If a prefix is passed, then it is used so long as it has not been used before.  If it has been used before than a number is added to the end
  """
  global curId
  global idLst
  if s is None: s = "i"
  if num is None:  # return w/ no list
    if s in idLst:
      idx = idLst[s]
      ident = s + str(idx)
    else:
      ident = s
      idx = 0
      idLst[ident] = idx
    return ident
  else: # return as a list
    ret = []
    for r in range(0,num):
      curId += 1
      ret.append(s + str(curId))
    return ret


def list2String(separator, lst):
  if len(lst):
    ret = str(lst[0])

    for l in lst[1:]:
      ret += separator + str(l)

    return ret
  return ""

def noop(x): return x

def noOvr(dict,lst):
  """Add a tuple to a dictionary if it does NOT currently exist"""
#  print '%s, %s' % (dict,lst)
  for (name,val) in lst:
#    print '%s, %s' % (name,val)
    if name not in dict:
#      print "ovr\n"
      dict[name] = val
#    else: print '%s, %s\n' % (name,dict[name])

def pairwise(x,y):
  ret = []
  i = 0
  while i < len(x):
    ret.append((x[i],y[i]))
    i += 1
  return ret
    

def TFO(obj,default):
  "True/false/other returns (true/false, obj/default)"

  if obj is None: return(0,default)
  if type(obj) == type(0):
    if obj == 1:
      return(obj,default)
  return (1,obj)

def strChk(obj):
  if obj is None:
    return ""
  return str(obj)

def FixId(i):
  if i: idstr = "id = '%s'" % i
  else:  idstr = ""

  return idstr


def PairIterator(obj):
  if type(obj) is DictType:
    return obj.items()
  if type(obj) is TupleType:
    return [obj]
  if type(obj) is ListType:
    return obj
  if obj is None: return []
  return obj 

def WriteFile(fname,chunk,doc=None):
  """Turn a chunk html definition into a file.  By default use the html template for document generation """
  from chunk import chunkStr
  from htmldoc import HtmlSkel
  from document import Before
  if not doc:
    doc = HtmlSkel()
  if type(chunk) is not type([]): chunk = [chunk]
#  pdb.set_trace()
  doc.genDoc(chunk)
  doc.Insert([chunkStr(BR + BR + "\n\n\n")],doc.body,Before)

  dstr = str(doc)
  
  # print "FILE: %s" % fname, "\n",dstr,"\n\n\n"

  import xml.dom.minidom
  dom = xml.dom.minidom.parseString(dstr)

  fil = open(fname,'w')
  #dom.writexml(fil,"","  ","\n")
  s = dom.toprettyxml()
  (xmldecl,nl,theRest) = s.partition("\n")  # I do not want to output <?xml version="1.0" ?>
  fil.write(theRest)
#  fil.write(str(doc))
  fil.close()

def WriteStr(chunk,doc=None):
  """Turn a chunk html definition into a string.  By default use the html template for document generation"""
  from chunk import chunkStr
  from htmldoc import HtmlSkel
  from document import Before
  if not doc:
    doc = HtmlSkel()
  if type(chunk) is not type([]): chunk = [chunk]

  doc.genDoc(chunk)
  doc.Insert([chunkStr(BR + BR + "\n\n\n")],doc.body,Before)

  dstr = str(doc)
  #print "STR: ",dstr,"\n\n\n"

  import xml.dom.minidom
  dom = xml.dom.minidom.parseString(dstr)

  fil = open(fname,'w')
  #dom.writexml(fil,"","  ","\n")
  s = dom.toprettyxml()
  (xmldecl,nl,theRest) = s.partition("\n")  # I do not want to output <?xml version="1.0" ?>
  return(theRest)
