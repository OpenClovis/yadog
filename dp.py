"""?
<desc>This module extracts documentation from python programs</desc>
"""
from types import *
import pdb
import ast
import re

import sys
sys.path.append(".")
from PyHtmlGen.document import *

from common import *
import microdom

#? <_> comment </_>
i = 10

#?<_>Multiline comment test
# </_>
j = 11

#?? Shorthand notation test. This tests the shorthand notation.
k = 12

#?? Shorthand notation without a brief
l = 13

class TestDoc:
  """?<class> This tests the docstring"""

  #? <method>constructor</method>
  def __init__():
    self.foo = 1  #? <member>the foo variable</member>
    #?<member>The bar variable</member>
    self.bar = 2

#?</class>


from constants import *

def extractComments(text):
  """?<fn>Pull the comments out of a Python file
     <arg name='text'>A single string containing python source code</arg>
     </fn>"""
  byLine = text.split("\n")
  num=0
  skip = 0
  justPound = False
  comments = []
  for line in byLine:
    num += 1
    if skip: # This allows you to skip a line in case it confuses the doc generator
      skip -= 1
      justPound=False
      continue
    stripped = line.strip()
    # TODO: search for strings and remove them
    if stripped:
      if justPound and stripped[0] == '#':    # For a comment block you don't need the ? on each line
        comments.append((num,stripped,False))
      else: 
        justPound=False
        if stripped == "#-": # skip the next line
          skip = 1
        #-  
        if stripped[0:2] == "#?":
          comments.append((num,stripped,False))
          justPound = True
        else:
          #-
          col = stripped.find("#?")
          if col != -1:
            comments.append((num,stripped[col:],True))

  ret = []

  # Join multiline comments
  idx = 0
  while idx<len(comments):
    c = comments[idx]
    if c[2]: # Its a one-liner
      ret.append((c[0],c[1]))
      idx+=1                 
    else:
      startLine = c[0]
      curLine = startLine
      running = c[1]
      idx += 1
      while idx<len(comments) and comments[idx][2] == False and comments[idx][0] == curLine+1:
        curLine+=1
        running += comments[idx][1][1:] # The comment without the hash
        idx+=1
      ret.append((startLine,running))
  #pdb.set_trace()
    
  return ret

def UnusedaddBriefDesc(s):
  """?? Transforms s into brief and desc sections.  This function splits s by sentences.  The first sentence will be wrapped in a 'brief' xml tag, the rest in 'desc'.
  <arg name='s'>The string to transform</arg>
  <returns>The transformed (or untouched) string</returns>
  """
  Xbrief = ("<%s>" % TagBrief,"</%s>" % TagBrief)
  Xdesc  =  ("<%s>" % TagDesc,"</%s>" % TagDesc)

  sentence = s.split(".") # The brief is the first sentence
  if len(sentence) > 1:
    return "<%s>" % TagBrief + sentence[0].strip() + "</%s>" % TagBrief + "<%s>" % TagDesc + s + "</%s>" % TagDesc
  return "<%s>" % TagDesc + s + "</%s>" % TagDesc

def fixupComments(comments):
  ret = []
  for (line,comment) in comments:  # If the comment begins with a ?, then replace it with the generic xml tag
    if comment[0:2] == '#-': #- It is NOT part of the doc
      comment = None
    elif comment.find('#-') != -1:
      print "REMOVING: %s" % comment
      comment = None
    elif comment[0:3] == '#??': #-
      #print "Adding tag: %s" % comment
      #comment = "<_>" + addBriefDesc(comment[3:]) + "</_>"
      comment = "<_>" + comment[3:] + "</_>"
    elif comment[0:2] == '#?':  #- Strip off the #
      comment = comment[2:]
    elif comment[0] == '#':  #- Strip off the #
      comment = comment[1:]
    if comment:
      ret.append((line,comment))

  return ret

def fixupDocstrings(comments):
  ret = []
  for (line,comment) in comments:  # If the comment begins with a ?, then replace it with the generic xml tag
    if comment[0:2] == '??':
      #comment = "<_>" + addBriefDesc(comment[2:]) + "</_>"
      comment = "<_>" + comment[2:] + "</_>"
    elif comment[0] == '?': # It is NOT part of the doc
      comment = comment[1:]
    else: comment = None

    if comment:
      ret.append((line,comment))

  return ret
      

#?<fn>Pull the docstrings out of an ast tree
#  <returns>A list of (linenumber,docstring) tuples</returns>
#</fn>
def extractDocstrings(node):

  def recurse(nlst):
   dsr=[]
   for node in nlst:
    if isInstanceOf(node,ast.Module):
      ds = ast.get_docstring(node)
      if ds: dsr.append((1,ds))
      dsr += recurse(node.body)
    if isInstanceOf(node,ast.FunctionDef):
      ds = ast.get_docstring(node)
      if ds: dsr.append((node.lineno,ds))
    elif isInstanceOf(node,ast.ClassDef):
      ds = ast.get_docstring(node)
      if ds: dsr.append((node.lineno,ds))
      dsr += recurse(node.body)
   return dsr

  return recurse([node])


def mergeDocList(doc1,doc2):
  result = []
  while doc1 or doc2:       
    if not doc2:
      result.append(doc1[0])
      doc1 = doc1[1:]
    elif not doc1:
      result.append(doc2[0])
      doc2 = doc2[1:]
    elif doc1[0][0] < doc2[0][0]:
      result.append(doc1[0])
      doc1 = doc1[1:]
    else:
      result.append(doc2[0])
      doc2 = doc2[1:]
  return result

#mergeDocList([(2,"foo")],[(1,"bar")])  

def addLineAttr(match,lineNum):
  s = "<%s linenum='%d'" % (match.groups()[0],lineNum)
#  print s
  return s


def comments2MicroDom(comments,filename):
  """?<fn>Convert a list of (line number,comment) to an xml doc</fn>"""
  
  # Add a line num attribute to all xml tags  
  text = []
  pat = re.compile("<(\w+)")
  
  for (line,comment) in comments:
    print "c2md:", line,comment
    newcomment = re.sub(pat,lambda x,y=line: addLineAttr(x,y),comment)
    text.append(newcomment)
 
  #print text
  xml = "<%s name='%s' language='python'>" % (TagFile,filename) + "".join(text)+"</%s>" % TagFile
  try:
    dom = microdom.parseString(xml)
  except microdom.ExpatError,e:
    print "XML ERROR!", str(e)
    print str(xml)
    pdb.set_trace()
    
  return dom


def findRelevantTag(midom,line):
  """?<fn>Finds the nearest microdom entry to the specified line that is either ON the line or after it.  In essence, find the tag that any text on the line most likely refers to.
       <arg name='midom'>The microdom tree, tags must have 'linenum' attributes</arg>
       <arg name='line'>The line number to you are interested in</arg>       
     </fn>"""

  def recurse(node,bd,bt):

    for c in node.children_:
      if isInstanceOf(c,microdom.MicroDom):
        if c.attributes_.has_key("linenum"):
          dist = line-int(c.linenum)
          if dist>=0: # that is the comment is ABOVE or on the same line as the code
            if dist<bd:
              bd=dist
              bt=c
        if c.children_:
          bd,bt = recurse(c,bd,bt)
    return bd,bt
  
  bestDist,bestTag = recurse(midom,10000,None)      
  return bestTag

def fixupFileDocstring(xml):
  # This is a docstring that should be associated with the whole file
  tmp = filter(lambda x: isInstanceOf(x, microdom.MicroDom), xml.children_)
  if tmp:  # If there is ANY documentation at all:
    t = tmp[0]
    if int(t.linenum) == 1:
      #pdb.set_trace()
      if t.tag_ == "_":
        (briefText,sp,desc) = t.data_.partition("\n")
        t.data_ = desc.strip()
#        if type(t.children_[0]) in StringTypes:  # Clean it up in the children list as well
#          (briefText,sp,desc) = tmp[0].partition("\n")
#          t.children_[0] = desc.strip()

        xml.addChild(microdom.MicroDom({"tag_":TagBrief},[briefText.strip()]))
        t.reTag(TagDesc)
      for c in t.children_:   # Pull all the tags that shouldn't be in the Desc out of it
        if isInstanceOf(c,microdom.MicroDom) and c.tag_ in NoDescTags:
          c.reParent(xml)



def xmlAttrInsert(xml,d):
  for (k,v) in d.items():
    if not xml.attributes_.has_key(k):
      xml.attributes_[k] = v
    else:
      if xml.attributes_[k] == "_":  # _ means that I should replace it with the right value
        xml.attributes_[k] = v
        if k == "tag_": xml.tag_ = v

def getLvalue(node):
  if type(node) is ast.Tuple:
    # TODO uncompile it
    return "(tuple)"
  try:
    return node.id
  except AttributeError:
    # Handle case where it is an _ast.Attribute object
    return node.value.id + "." + node.attr
  

def extractXml(prjPfx, filename):
  
  def recurse(nlst,context=None,forceParentNode=None):
 
   for node in nlst:
    xmlnode = findRelevantTag(xml,node.lineno)
    #print xmlnode
    if xmlnode is None: xmlnode = xml

    # Imports
    if isInstanceOf(node,ast.ImportFrom):
      fdxml = xmlnode.findParent(TagFile)[0]
      fdxml.addChild(microdom.MicroDom({"tag_":"requires","module":node.module,"linenum":node.lineno},[],None))
      
    if isInstanceOf(node,ast.Import):
      fdxml = xmlnode.findParent(TagFile)[0]
      for mod in node.names:
        fdxml.addChild(microdom.MicroDom({"tag_":"requires","module":mod.name,"linenum":node.lineno},[],None))

    # Assignment / Variable declaration
    elif isInstanceOf(node,ast.Assign):
      if context == TagCtor:
        varnames = []
        for tgt in node.targets:
          try:
            varnames.append(tgt.attr)
          except AttributeError:
            print "Skipping ctor assignment %s" % str(tgt)
            pass

      else:
        varnames = [getLvalue(tgt) for tgt in node.targets]
        
      if len(varnames) == 1:
        varnames = varnames[0]

      # I'm trying to grab the value of an assignment to put into the documentation, i.e. MY_CONST = 50
      val=None
      try:
        val = node.value.n # for numbers
      except: pass     
      try:
        val = node.value.s # for strings
      except: pass
      try:
        val = node.value.id # for names (modules)
      except: pass
      
      if val == None:
        # But if the assignment is complex, then it does not make any sense to grab it
        # But maybe you can make sense of these and figure out some cool documentation to add?
        if isInstanceOf(node.value,ast.Subscript): pass
        elif isInstanceOf(node.value,ast.Dict): pass
        elif isInstanceOf(node.value,ast.List): pass
        elif isInstanceOf(node.value,ast.Call): pass
        elif isInstanceOf(node.value,ast.Attribute): pass
        elif isInstanceOf(node.value,ast.BinOp): pass
        elif isInstanceOf(node.value,ast.IfExp): pass
        elif isInstanceOf(node.value,ast.Tuple): pass
        elif isInstanceOf(node.value,ast.Lambda): pass
        elif isInstanceOf(node.value,ast.ListComp): pass
        elif isInstanceOf(node.value,ast.Compare): pass
        else:
          pdb.set_trace()
      
      xmlAttrInsert(xmlnode,{AttrTag:TagVariable,AttrName:varnames,AttrValue:val})

    # Function handling
    elif isInstanceOf(node,ast.FunctionDef):
      fdxml = xmlnode.findParent(TagFunction)
      if not fdxml: fdxml = xmlnode
      else: fdxml=fdxml[0]
 
      
      if node.name == fdxml.attributes_.get("name", node.name): # If it HAS a name, its has to be == or I've got the wrong comment
 
      # The comments form an XML tree, and the language structure forms a tree as well.
      # If the language structure's tree should override the XML tree, then forceParentNode
      # will be true and so this comment will be extracted from its current location and pushed under the forceParentNode
      # This happens when a class defines its member functions, for example and the user uses ?? instead of correctly matching
      # xml class scope with the true class scope.
        if forceParentNode and forceParentNode != fdxml:
          fdxml.extract()
          forceParentNode.addChild(fdxml)

        xmlAttrInsert(fdxml,{AttrTag:TagFunction,AttrName:node.name})
      # If its a constructor, hunt thru for member variables
      if node.name == "__init__": recurse(node.body,TagCtor)

    # Class handling  
    elif isInstanceOf(node,ast.ClassDef):
      fdxml = xmlnode.findParent(TagClass)
      if not fdxml: fdxml = xmlnode
      else: fdxml=fdxml[0]

      fp = None

      # TODO: This class has no documentation, create it based on configuration option
      if fdxml.tag_ != TagClass and fdxml.tag_ != "_":
        pass
      else:
        xmlAttrInsert(fdxml,{AttrTag:TagClass,AttrName:node.name})
        recurse(node.body,TagClass,fdxml)

    elif isInstanceOf(node,ast.Expr) or isInstanceOf(node,ast.If):
      pass
      #- pdb.set_trace()    
    else:
      print "unrecognised node %s" % str(node)


  print "Parsing %s" % filename
  try:
    f = open(filename,"rb")
  except IOError:  # A broken symlink could cause this to be unopenable even though the directory entry exists
    print "Cannot open %s" % filename
    return ""

  text = f.read()

  if filename.startswith(prjPfx):
    filename = filename[len(prjPfx):]   

  parsedFile = ast.parse(text,filename)

  comments = extractComments(text)
  print "Step 1 Extract Comments: %s" % comments
  comments = fixupComments(comments)
  print "Step 2 Fixup Comments: %s" % comments
  docStrings = extractDocstrings(parsedFile)
  print "Step 3 Extract Docstrings: %s" % docStrings
  docStrings = fixupDocstrings(docStrings)
  print "Step 4 Fixup Docstrings: %s" % docStrings
  
  allDocs = mergeDocList(comments,docStrings)
  print "Step 5 Merge: %s" % allDocs
  
  xml = comments2MicroDom(allDocs,filename)

  parsedFile = ast.parse(text,filename)

  xmlpos = None

  recurse(parsedFile.body)

  fixupFileDocstring(xml)

  # print "Extracted XML:\n", xml.write()  
  return xml

def Test():
  xml = extractXml("dp.py")
  #- xml = extractXml("microdom.py")



if __name__ == "__main__":
    Test()

