"""<module>
This module extracts documentation from python programs
"""
from types import *
import pdb
import ast
import re
import sys
import cgi

from PyHtmlGen.document import *

from common import *
from constants import *
import microdom


def dictToArgStr(d,skip):
  ret = []
  for (k,v) in d.items():
    if not k in skip:
      ret.append("%s='%s'" % (k,cgi.escape(v)))
  return " ".join(ret)

def extractSingleLineComment(byLine,idx):
    result = []
    firstSrcLine = None
#-    print byLine[idx]
    excerpt = False
    try:
    # First find all the comment lines
      while 1:
          line = byLine[idx].strip()
          if line[0:3]=="//?":
            result.append(line[3:])
            idx+=1
            if "<excerpt" in line:
              tmp = []
              while 1:
                l2 = byLine[idx]
                if "</excerpt>" in l2:
                  result.append("<![CDATA[" + "".join(tmp) + "]]>")
                  break
                else:
                  tmp.append(l2 + "\n")
                idx += 1
          elif line[0:2]=="//":
            result.append(line[2:])
            idx+=1
          else:
            break

        # Next pass over any whitespace lines
      while not line:
          idx+=1
          line = byLine[idx].strip()
      # Ok, this is the line the comment refers to
      firstSrcLine = line
    except IndexError, e:
      firstSrcLine = ""
    return(idx-1," ".join(result),firstSrcLine)

def extractMultiLineComment(byLine,idx):
    result = []
    firstSrcLine = None
    while 1:
      try:
        line = byLine[idx].strip()
      except IndexError, e:
        idx = idx-1
        break
      idx+=1
      if line:
        cleaned = line
        if cleaned[0:3] == '/*?': cleaned = cleaned[3:] #- Strip off the start and typical commend block stuff
        cleaned = cleaned.replace("*/","")
        if cleaned and cleaned[0] == '*': cleaned = cleaned[1:] # Strip off double stars
        result.append(cleaned)          
        if line.find("*/") != -1:
          break
    
    line = byLine[idx].strip()
    while not line:
      idx+=1
      try:
        line = byLine[idx].strip()
      except IndexError, e:
        line=""
        break
      
    firstSrcLine = line

    return(idx-1," ".join(result),firstSrcLine)


def extractCodeDoc(byLine,idx):
  result = []
  nLines = len(byLine)
  while idx < nLines:
    line = byLine[idx]
    if line[0:4] == "//?]":
      break
    result.append(line)
    idx+=1

  result.insert(0,"<![CDATA[")
  result.append("]]>")
  return (idx,"\n".join(result),"")
    

def extractComments(text):
  """<fn>Pull the comments out of a C/C++ file
     <arg name='text'>A single string containing python source code</arg>
     </fn>"""
  byLine = text.split("\n")
  num=0
  comments = []
  idx = 0
  while idx<len(byLine):
    line = byLine[idx]
    
    stripped = line.strip()
    #- TODO: search for strings and remove them
    if stripped:
      if stripped[0:4] == "//?[":
          (idx,comment,srcLine) = extractCodeDoc(byLine,idx)
          comments.append((idx,comment,srcLine))          
      elif stripped[0:3] == "//?":
          (idx,comment,srcLine) = extractSingleLineComment(byLine,idx)
          comments.append((idx,comment,srcLine))
      elif -1 != line.find("//?"):
          (srcLine,sep,comment) = line.partition("//?")
          comments.append((idx,comment,srcLine))
      elif stripped[0:3] == "/*?":
          # pdb.set_trace()
          (idx,comment,srcLine) = extractMultiLineComment(byLine,idx)
          comments.append((idx,comment,srcLine))          

    idx+=1

  return comments

def addLineAttr(match,lineNum):
  s = "<%s linenum='%d'" % (match.groups()[0],lineNum)
#-  print s
  return s

def addAttrClosure(attr,val):

  def fn(match):
    m = match.groups()
    if m[1].find(attr)==-1:  # Its not in there, so add it (if it is already defined we won't override)
      s = "<%s %s %s='%s'>" % (m[0],m[1],str(attr),str(val))
    else:
      s = "<%s %s>" % (m[0],m[1])
    return s

  return fn

def addTag(tag):
  def fn(match):
    m = match.groups()
    if m[0]=="_":  # Its not in there, so add it (if it is already defined we won't override)
      return "<%s %s>" % (tag,m[1])
    else:
      return "<%s %s>" % (m[0],m[1])
  return fn

def addCloserTag(tag):
  def fn(match):
    m = match.groups()
    if m[0]=="_":  # Its not in there, so add it (if it is already defined we won't override)
      return "</%s>" % (tag)
    else:
      return "</%s>" % (m[0])
  return fn

#-
remacro = re.compile(r"\A\s*#define\s+(?P<name>[a-zA-Z_]+\w*)\s+(?P<value>\w+)")
remacrofn = re.compile("\A\s*#define\s+(?P<name>[a-zA-Z_]+\w*)\s*(?P<args>\([^\)]*\))+(?P<value>.*)$")
renamespace = re.compile(r"\A\bnamespace\b\s*(?P<name>[a-zA-Z_]+\w*)")
reclass = re.compile(r"\A\bclass\b\s*(?P<name>[a-zA-Z_]+\w*)")
restruct = re.compile(r"\A\bstruct\b\s*(?P<name>[a-zA-Z_]+\w*)")
refn = re.compile(r"\A(?:\bvirtual\b|\bstatic\b)?\s*(?P<type>[\w<>,:&*\s]*?)\s+(?P<name>\b[a-zA-Z_]\w*\b)\s*(?P<args>\(.*?\)\s*(?:\bconst\b)?)\s*(?P<semicolon>;+)?\s*")
reglobalfn = re.compile(r"""\A(?:extern\s*)(?:"C"\s*)(?:\bvirtual\b|\bstatic\b)?\s*(?P<type>[\w<>,:&*\s]*?)\s+(?P<name>\b[a-zA-Z_]\w*\b)\s*(?P<args>\(.*?\)\s*(?:\bconst\b)?)\s*(?P<semicolon>;+)?\s*""")
rector = re.compile(r"\A(?P<name>\b[a-zA-Z_]\w*\b)\s*(?P<args>\(.*?\))\s*(?P<semicolon>;+)?\s*")
revardecl = re.compile(r"""\A\s*(?P<typequal>(?:(?:extern|"C"|const)\s)*)(?P<type>[\w<>:,&*\s]*?)\s+(?P<name>\b[a-zA-Z_]\w*\b)""")
#reargdecl = re.compile(r"\A\s*(?P<type>[\w<>,&*\s]*?)\s+(?P<name>\b[a-zA-Z_]\w*\b)")
reargdecl = re.compile(r"\A\s*(?P<typequal>(?:(?:unsigned|signed|const|volatile|long|struct)\s)*)(?P<type>[\w<>,:&*\s]*?)\s+(?P<name>\b[a-zA-Z_]\w*\b)?")
reassignment = re.compile(r"\A\s*(?P<name>\b[a-zA-Z_]\w*\b)\s*=\s*(?P<value>\w+)")
resymbol = re.compile(r"\A\s*(?P<name>\b[a-zA-Z_]\w*\b)\s*")

res = [("macro",remacrofn),(TagConst,remacro),(TagSection,renamespace),(TagClass,reclass),(TagClass, restruct),(TagFunction,reglobalfn),(TagFunction,refn),(TagCtor,rector),(TagConst, reassignment),(TagVariable,revardecl),(TagConst,resymbol)]

reKeys = ['name','value','type','args','virtual','static','typequal']

# don't put these matched keys into the final xml as attributes
skipKeys = ['semicolon']

#- This pattern matches an xml opener tag with an arbitrary number of attributes and returns
#- the tag as the first group and all attributes and values as a string in the second
xmlpat = re.compile(r"""<\s*(\w+)((?:\s+\w+\s*=\s*['"][^'"]*['"])*)\w*\s*>""")

# If the user wants us to fill stuff in, it must START with xml opener tag
xmlfillerpat = re.compile(r"""\A\s*<\s*(\w+)((?:\s+\w+\s*=\s*['"][^'"]*['"])*)\w*\s*>""")
#- This pattern matches an xml closer 
xmlcloserpat = re.compile(r"""</\s*(\w+)\s*>""")

#- pat.match("<foo>").groups()
#- pat.match("< foo >").groups()
#- pat.match("<foo >").groups()
#- pat.match("< foo>").groups()
#- pat.match("<foo bar='1'>").groups()
#- pat.match("""<foo bar='1' zerg="2">""").groups()

def fixupComments(comments):
  ret = []
  pat = re.compile("<(\w+)")
  for (linenum,comment,srcline) in comments:  # If the comment begins with a ?, then replace it with the generic xml tag
      if srcline:
        isCommentXml = (re.search(xmlpat,comment) != None) or (re.search(xmlcloserpat,comment) != None)
        isFillerXml = xmlfillerpat.search(comment)
        matched = False
        if isFillerXml:  # Comment has XML in it.  Patch the XML with information derived from the source line
            for (tag,r) in res:  # Look through all of our language patterns
              t = r.search(srcline) # If it matches, apply that tag
              if t:
                matches = t.groupdict()
                if tag == "macro":  # Special case some handling for macros, then handle as a function
                  matches["type"] = "macro"
                  tag = TagFunction
                log.info('line [{num}] "{srcline}" matches [{tag}] as {gd}'.format(num=linenum,srcline=srcline,tag=tag,gd=matches))

                for key in reKeys:  # Put all the interesting data from the source line into the xml opener tag
                  if matches.has_key(key):
                    comment = re.sub(xmlfillerpat,addAttrClosure(key,cgi.escape(matches[key])),comment)
                    matched = True
                comment = re.sub(xmlfillerpat,addTag(tag),comment)
                comment = re.sub(xmlcloserpat,addCloserTag(tag),comment)
                break # only match the first pattern
        else: # Comment has no XML in it.  Figure out the appropriate tag from the source context and add it
            if not isCommentXml: 
              comment = cgi.escape(comment) # convert & to &amp; < to &lt; etc
            for (tag,r) in res:  # Look through all of our language patterns
              t = r.match(srcline) # If it matches, apply that tag
              if t:
                matches = t.groupdict()
                if tag == "macro":  # Special case some handling for macros, then handle as a function
                  matches["type"] = "macro"
                  tag = TagFunction
                  # pdb.set_trace()
                log.info('line [{num}] "{srcline}" matches [{tag}] as {gd}'.format(num=linenum,srcline=srcline,tag=tag,gd=matches))
                comment = "<%s %s>%s</%s>" % (tag,dictToArgStr(matches,skipKeys),comment,tag)
                if tag == TagFunction:
                  log.info("XML: {comment}".format(comment=comment))
                matched= True
                break # only match the first pattern
        if not matched:
          log.warning('line [{num}]: Unable to match to a C++ language construct: "{srcline}"'.format(num=linenum,srcline=srcline))

      comment = re.sub(pat,lambda x,y=linenum: addLineAttr(x,y),comment)
      # pdb.set_trace()
      ret.append(comment)
  return ret


def comments2MicroDom(comments,filename):
  """<fn>Convert a list of (line number,comment) to an xml doc</fn>"""
  
  xml = "<%s name='%s' language='c++'>" % (TagFile,filename) + "\n".join(comments)+"</%s>" % TagFile
  try:
    dom = microdom.parseString(xml)
  except microdom.ExpatError,e:
    print "Error: %s (error XML written to error.xml)" % str(e)
    print "> %s(%d)unknown()" % (filename,e.lineno)
    try:
      print "-> %s" % comments[e.lineno-1]
    except:
      pass
    # write the bad xml out to an analysis file
    f = open("error.xml","w")
    f.write(xml)
    f.close()
    raise
    
  return dom


def regularize(node):
  """? This function ensures that the tree is complete and regular.  For example it breaks descriptions into brief and desc tags.
  """
  if microdom.isInstanceOf(node,microdom.MicroDom):
    if node.tag_ in [TagCtor,TagMethod,TagFunction]:
      # Add the "decl" tag
      if node.tag_ in [TagCtor]:  # ctors have not type
        t = microdom.MicroDom({"tag_":TagDecl},[node.name + node.args])
      else:
        t = microdom.MicroDom({"tag_":TagDecl},[node.type + " " + node.name + node.args])
        # pdb.set_trace()

      node.addChild(t)

      # Supplement the args tags
      args = node.args
      args = args.replace("(","").replace(")","") # remove leading and trailing paren
      arglst = args.split(',')
      for arg in arglst:
        if arg != "void" and arg != "":
          matched = reargdecl.match(arg)
          if matched: # A normal function
            (typequal,atype,aname) = matched.groups()
          else:
            (typequal,atype,aname) = ("","macro arg",arg)

          argdefs = node.filterByAttr({AttrName:aname})
          if not argdefs:
            t = microdom.MicroDom({"tag_":TagParam,AttrType:typequal + atype,AttrName:aname},None,None)
            node.addChild(t)
          for t in argdefs:
            t.addAttr(AttrType,typequal + atype)
      

    for c in node.children_:
      regularize(c)

  return node

def extractXml(prjPfx, filename):
  
  logging.info("Extracting: %s" % filename)
  f = open(filename,"rb")
  text = f.read()

  comments = extractComments(text)

  comments = fixupComments(comments)

  if filename.startswith(prjPfx):
    filename = filename[len(prjPfx):]   

  xml = comments2MicroDom(comments,filename)
  regularize(xml)
  
  # print "Extracted XML:\n", xml.write()  
  return xml

def Test():
  pdb.set_trace()
  xml = extractXml("/me/hw/arduino/arduino-m5451-current-driver/latest/apps/lightuino_lib_dev/lightuino.h")
  #- xml = extractXml("microdom.py")



if __name__ == "__main__":
    Test()

#</module>
