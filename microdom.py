"""?? The microdom module implements a DOM that is even simpler than minidom.  It creates a tree of MicroDom objects from valid XML and offers functions to find, select, prune, and transform the resulting tree."""
import pdb
from types import *
import inspect
import cgi
import xml.dom.minidom
from xml.parsers.expat import ExpatError

def isInstanceOf(obj,objType):
  """?<fn>Is the object an instance (or derived from) of the class objType)?</fn>"""
  if type(obj) is InstanceType and objType in inspect.getmro(obj.__class__): return True
  if type(obj) is objType: return True
  return False

def keyify(s):
  """?<_ doc='This helper function aids DOM attribute and child access through python field notation (ie. object.field) by transforming characters that are illegal in field notation to an _'/>"""
  s = s.replace(":","_")
  return s

class AnyChild:
  def __init__(self, microdom,recurse=False):
    self.microdom = microdom
    self.recurse = recurse

  def __getattr__(self,item):
    for c in self.microdom.children_:
      try:
        result = c[item]
        if result is not None: return result
      except:
        pass
    for (k,v) in self.microdom.attributes_.items():
      try:        
        if k == item: return v        
      except:
        pass

    if self.recurse:
      # Look for a tag
      result = self.microdom.filterByAttr({"tag_":item})
      if result: return result[0]
      # Look for an attribute
      result = self.microdom.filterByAttr({item:lambda x: not x is None})
#      print "attr:",result
      if result: 
        return result[0].attributes_[item]

    raise AttributeError(item)


  

class MicroDom:
  """?<_>A MicroDom Node"""
  def __init__(self, attributes,children,data=None,parent=None):
    """?<_>This constructor builds a single MicroDom node.  More likely you want the global functions that build MicroDom trees.</_>"""
    self.init(attributes,children,data,parent)

  def merge(self,other):
    """?? Remove the 'other' DOM node and combine it with this one, preferring this one's attributes if there are conflicts"""
    other.extract()  # Remove the other from its tree in prep to merge

    for c in other.children_:  # Add all the other's children into my child list
      self.addChild(c)
    for (k,v) in other.attributes_.items():
      self.attributes_.setdefault(k,v)


  def extract(self):
    """?? Remove myself (and any children under me) from the DOM tree"""
    if self.parent_:
      self.parent_.children_.remove(self)
      try:
        del self.parent_.child_[keyify(self.tag_)]
        del self.parent_.__dict__[keyify(self.tag_)]       
      except KeyError:
        pass
    self.parent_ = None

  def removeChildren(self):
    t = self.children_
    self.children_ = []

    for c in self.children_:
      try:
        del self.child_[keyify(self.tag_)]
        del self.__dict__[keyify(c.tag_)]
        c.parent_ = None
      except:
        pass
    return t


  def reset(self, attributes,children,data,parent=None):
    """?<_>This constructor builds a single MicroDom node.  More likely you want the global functions that build MicroDom trees.</_>"""

    self.extract()

    self.removeChildren()

    self.init(attributes,children,data,parent)
    

  def init(self, attributes,children,data,parent=None):
    """?<_>This constructor builds a single MicroDom node.  More likely you want the global functions that build MicroDom trees.</_>"""
    
    #? <section name='Formal (guaranteed correct) access'>
    self.tag_        = str(attributes["tag_"])    #?<_>Get the XML tag</_>
    self.attributes_ = {} #?<_>Get a dictionary of attributes, including the key 'tag_' which -> the XML tag</_>
    self.children_   = []                    #?<_>Get a list of children</_>
    self.child_      = {}                    #?<_>Get a child by xml TAG, or attributes "name" or "id"</_>
    self.data_       = data                  #?<_>All the characters under this XML tag that are not under a subtag</_>
    self.parent_     = parent                #?<_>The enclosing XML tag</_>

    if self.parent_:
      self.parent_.addChild(self)

    self.anychild_   = AnyChild(self)
    self.any_        = AnyChild(self,True)
    #? </section>

    for (k,v) in attributes.items():
      self.attributes_[k] = str(v) # remove unicode

    if self.data_ is None: self.data_ = ""

    # quick access
    #for (k,v) in attributes.items():
    #  try:
    #    self.__dict__[keyify(k)] = v
    #  except:
    #    pass
    
    if children: 
     for c in children:
      if type(c) in StringTypes:
        self.data_ = self.data_ + str(c)

      self.children_.append(c)

      try:
        c.parent_ = self
        self.__dict__[keyify(c.tag_)] = c
        self.child_[keyify(c.tag_)] = c
        if c.attributes_.has_key("id"):
          self.child_[keyify(c.attributes_["id"])] = c
        if c.attributes_.has_key("name"):
          self.child_[keyify(c.attributes_["name"])] = c
      except:
        pass

  def reParent(self,newparent):
    """?? Change my parent
    <arg name='newparent' type='MicroDom'>The new parent for this node</arg>
    """
    self.extract()
    newparent.addChild(self)

  def reTag(self,val):
    """?? Change my tag.  This function handles and updating the parent's dictionary as well.""" 
    try:
      if self.parent_.child_[keyify(self.tag_)] == self:
        del self.parent_.child_[keyify(self.tag_)]
        del self.parent_.__dict__[keyify(self.tag_)]
    except KeyError,e:  # There was a child name collision and then that other child was deleted, leaving this one without a dictionary lookup.
      pass

    self.tag_ = val
    self.parent_.child_[keyify(self.tag_)] = self
    self.parent_.__dict__[keyify(self.tag_)] = self

  def getItem(self,item,default=None):
    """?? Gets an attribute or child by key, or returns the default if it does not exist"""
    if self.attributes_.has_key(item): return self.attributes_[item]
    if self.child_.has_key(item): return self.child_[item]
    return default

  def addAttr(self,attr,val,override=True):
    if override or not self.attributes_.has_key(attr):
      self.attributes_[attr] = val

  def addChild(self,c):
    """?? Add a new child into the tree
    <arg name='c' type='MicroDom'>The child to add</arg>
    """
    if c in self.children_: return

    self.children_.append(c)
    try:
        c.parent_ = self
    except:
        pdb.set_trace()
    try:
        self.__dict__[keyify(c.tag_)] = c
        self.child_[keyify(c.tag_)] = c
        if c.attributes_.has_key("id"):
          self.child_[keyify(c.attributes_["id"])] = c
        if c.attributes_.has_key("name"):
          self.child_[keyify(c.attributes_["name"])] = c
    except:
        pdb.set_trace()
    

  def __getattr__(self,name):
    if self.attributes_.has_key(name): return self.attributes_[name]
    raise AttributeError
  
  def delve(self,lst,lstlen=0):
      """?<_>Traverse the tree to get a node
         <arg name='lst'>The path to the desired node.  For example to traverse the child "bar" and get the child "foo", pass ["bar","foo"]</arg>
         <returns>a MicroDom node or None</returns>
         </_>"""
      if not lstlen: lstlen = len(lst)

      c = self.child_.get(lst[0],None)
      if c:
        if lstlen>1:
          return c.delve(lst[1:],lstlen-1)
        else: return c
      if lst[0] == "any_":
        for c in self.children_:
          if isInstanceOf(c,MicroDom):
            result = c.delve(lst[1:],lstlen-1)
            if not result is None: return result  # Return the first match

      return None
  
  def children(self,filter = None):
    """?<_>Return all children of type MicroDom by default, or return the transformation function applied to all children, eliminating any that return None
    <arg name='filter'>A function that takes a single MicroDom argument.  And returns "None" to leave the object out of the result, or anything else to return that in the result</arg>
    <returns>A list of objects</returns>
    </_>"""
    ret = []
    for c in self.children_:
      if filter is not None:
        t = filter(c)
        if t is not None: ret.append(t)
      else:
        if isInstanceOf(c,MicroDom): ret.append(c)
    return ret

  def childrenWithAttr(self,attr,val):
    return self.children(lambda x,a=attr,v=val: x if isInstanceOf(x,MicroDom) and x.attributes_.get(a,None) == val else None)

  def get(self,item,d=None):
    try:
      d = self.__getitem__(item)
    except KeyError:
      pass
    return d

  def __getitem__(self,item):
    #print "ITEM: %s" % item
    if self.tag_ == item: return self.data_
    t = self.attributes_.get(item,None)
    if not t is None: return t
    t = self.child_.get(item,None)
    if not t is None: return t

    ilst = item.split(".")
    if len(ilst)>1: 
      ret = self.delve(ilst)
      if ret is not None: return ret
    raise KeyError(item)


  def attrMatch(self,attrs,missingIsOk=False):
    """?<method>Does this MicroDom node match the passed attributes?
    <arg name='attrs'>A dictionary whose keys are the attribute names.  The value can be either any item, or a function.  If any item then equality (==) is tested.  If a function the function is called with the class's attribute's value as an argument.  The fn should return "False" if this class's attribute does NOT match.</arg>
    <arg name='missingIsOk' default='False'>Pass True if attributes missing in the class can still "match"</arg>
    </method>"""
    for (k,v) in attrs.items():
      myval = self.attributes_.get(k,None)
      if type (v) is FunctionType:
        if not v(myval): return False
      if type(v) is ListType:
        if not myval in v: return False
      elif myval is not None:
        if not v == myval: return False
      elif not missingIsOk: return False
    return True

  def filterByAttr(self,attrs):
    """?<_>Recursively search the DOM tree, returning a list of all nodes that match the passed attributes
    </_>"""
    ret = []
    if self.attrMatch(attrs): ret.append(self)
    for c in self.children_:
      try:
        ret += c.filterByAttr(attrs)
      except AttributeError: # Its a leaf - ie. NOT a microdom object
        pass
    return ret

  def walk(self):
    """?<_>Recursively walk the DOM tree, 
    </_>"""
    ret = []
    yield self
    for c in self.children_:
      try:
        for w in c.walk():
          yield w
      except AttributeError,e: # its a leaf
        yield c

  def find(self,tagOrAttr):
    """?<_>Recursively search down the tree looking for all nodes with a particular tag, OR with a particular attribute (search by tag is attempted first). Note, to get all nodes with an attribute that equals a particular value or set of values, use <ref>filterByAttr</ref>
    <arg name='tagOrAttr'>A string specifying the tag or the attribute name</arg>
    </_>"""
    ret = self.findByAttr({"tag_":tagOrAttr})
    if not ret is None: return ret
    ret = self.findByAttr({tagOrAttr:lambda x: not x is None})
    if not ret is None: return ret
    return None

  def findParent(self,tagOrAttr):
    """?<_>Recursively search the up the tree looking for all nodes with a particular tag, OR with a particular attribute (search by tag is attempted first). 
    <arg name='tagOrAttr'>A string specifying the tag or the attribute name</arg>
    <returns>A list of matching parents, grandparents, etc, in closest to farthest order (ie ret[0] is the parent)</returns>
    </_>"""
    ret = self.findParentByAttr({"tag_":tagOrAttr})
    if not ret is None: return ret
    ret = self.findParentByAttr({tagOrAttr:lambda x: not x is None})
    if not ret is None: return ret
    return None
    

  def findByAttr(self,attrs,prefix=""):
    """?<_><brief>Recursively search down the tree looking for all nodes with a particular tag, OR with a particular attribute (search by tag is attempted first).</brief><desc> Note, to get all nodes with an attribute that equals a particular value or set of values, use <ref>filterByAttr</ref></desc>
    <arg name='attrs'>A <ref>attrMatch</ref> valid attribute spec</arg>
    <arg name='prefix'>A string that should be prepended to the beginning of returned nodepaths (include the final dot ie. "root.next.")</arg>
    <returns>A list of (nodepath,node) pairs, where nodepath is the dotted notation path to traverse to get to the node</returns>
    </_>"""
    ret = []
    if self.attrMatch(attrs): ret.append((prefix+self.tag_,self))
    for c in self.children_:
      try:
        ret += c.findByAttr(attrs,prefix + self.tag_ + ".")
      except AttributeError: # Its a leaf - ie. NOT a microdom object
        pass
    return ret

  def findParentByAttr(self,attrs):
    """?<_>Recursively search the up the tree (starting with myself) looking for all nodes with a particular attribute. 
    <arg name='attrs'>A string specifying the tag or the attribute name</arg>
    <returns>A list of matching parents, grandparents, etc, in closest to farthest order (ie ret[0] is the parent)</returns>
    </_>"""
    ret = []
    p = self

    while p:
      if p.attrMatch(attrs): ret.append(p)
      p = p.parent_
      
    return ret
      

  def getElementsByTagName(self,tag):
    """?<_>Return all nodes with a particular tag</_>"""
    return self.filterByAttr({"tag_":tag})

  def filterByTag(self,tag):
    """?<_>Return all nodes with a particular tag</_>"""
    return self.filterByAttr({"tag_":tag})

  def __repr__(self):
    return self.__str__()
    #return self.dump(True)

  def __str__(self):
    ps = self.pfxsfx()
    if len(ps) == 2:
      return ps[0] + "..." + ps[1]
    else: return ps[0]

  def pfxsfx(self,optimize=True):
    """?<_>Return a list of 2 strings containing the xml opener and closer for this node.  If there are no children the optimized format may be used, and the list will contain only 1 element
    <arg name='optimize' default='True'>Pass False if you always want separate XML opener and closers</arg>
    </_>"""

    if not optimize or (self.data_ or self.children_):
      full = 1
    else: full = 0
    
    if len(self.attributes_)>1:
      # Format attribute string, eliminating the tag_ attribute
      attrs = ["%s='%s'" % (k,v) for (k,v) in filter(lambda i: i[0] != 'tag_', self.attributes_.items())]
      attrs = " " + " ".join(attrs)
    else:
      attrs = ""

    if full:
      return ["<%s%s>" % (self.tag_,attrs),"</%s>" % self.tag_]
    else:
      return ["<%s%s />" % (self.tag_,attrs)]

  def writeChildren(self,indent=0):
    chlst = []
    # The data is also in the children_ list: chlst.append((" "*(indent+2)) + self.data_ + "\n" )
    if self.children_:     
      for c in self.children_:        
          try:
            chlst.append(c.write(indent+2))
          except AttributeError:
            s = str(c)
            # If html illegal characters are in the input then literalize it.  TODO: see if this looks like HTML.  If so, don't touch it.
            if "<" in c or ">" in c or "&" in c:
              s = "\n<![CDATA[\n" + s + "\n]]>"
            chlst.append((" "*indent) + s + "\n")
    return "".join(chlst)    

  def escapedContents(self):
    """?<_>Return an XML-escaped representation of the data in this node</_>"""
    return cgi.escape(self.data_)

  def write(self,indent=0):
    """?<_>Return a pretty-printed string of this XML tree</_>"""
    s=[]
    ps = self.pfxsfx()
    inner = self.writeChildren(indent)
    result = [(" "*indent) + ps[0] + "\n", inner]
    if len(ps)==2:
      result.append((" "*indent) + ps[1] + "\n")
    return "".join(result)

  def dumpChildren(self, recurse=True):
    """?<_>Return a compact string of this XML tree, without this nodes tag</_>"""

    # if self.data_: datastr = str(self.data_)
    # else: datastr = ""
    if self.children_:
      if not recurse: chstr = "[%d children]" % len(self.children_)
      else:
        chlst = []
        for c in self.children_:
          try:
            chlst.append(c.dump())
          except AttributeError:
            chlst.append(str(c))
        chstr = "".join(chlst)
    else: chstr = ""
    return chstr

  def dump(self, recurse=True):
    """?<_>Return a compact string of this XML tree</_>"""

    if self.children_:
      full = 1
    else: full = 0

    chstr = self.dumpChildren(recurse)

    if len(self.attributes_)>1:
      # Format attribute string, eliminating the tag_ attribute
      attrs = ["%s='%s'" % (k,v) for (k,v) in filter(lambda i: i[0] != 'tag_', self.attributes_.items())]
      attrs = " " + " ".join(attrs)
    else:
      attrs = ""

    if full:
      return "<%s%s>%s</%s>" % (self.tag_,attrs,chstr,self.tag_)
    else:
      return "<%s%s />" % (self.tag_,attrs)
#?</_>


def LoadFile(fil):
  """?<_>Create a MicroDom tree from file(s)
  <arg name='fil'>A filename or list of filenames from which to create the XML tree.  Note the files must have a single top level node</arg>
  <returns>a MicroDom tree or a list of them</returns>
  </_>"""
  if type(fil) is ListType:
    return [LoadFile(f) for f in fil]

  dom = xml.dom.minidom.parse(fil)
  return LoadMiniDom(dom.childNodes[0])

def parseString(s):
  """?<_>Create a MicroDom tree from a string
  <arg name='s'>the string.  Note the string must have a single top level node</arg>
  <returns>a MicroDom tree</returns>
  </_>"""
  try: 
    dom = xml.dom.minidom.parseString(s)
  except ExpatError:
    raise
  return LoadMiniDom(dom.childNodes[0])


def LoadMiniDom(dom):
  """?<_>Create a MicroDom tree from a minidom tree
  <arg name='dom'>the dom tree</arg>
  <returns>a MicroDom tree</returns>
  </_>"""
  if type(dom) is ListType:
    return [LoadMiniDom(d) for d in dom]

  childlist = []
  attrlist = { "tag_": dom.nodeName}

  if dom.childNodes:
    for child in dom.childNodes:
      if child.nodeName == '#text' or child.nodeName == '#cdata-section':  # Raw data
        childlist.append(child.nodeValue)
      else:
        childlist.append(LoadMiniDom(child))

  for (key,val) in dom._attrs.items():
    attrlist[key] = val.value

  try: 
      data = dom.data
  except AttributeError:
      data = None

  return MicroDom(attrlist, childlist, data)


def Merge(topTag,children):
  """?<_>Take a list of DOMs and put them all under one top tag</_>"""
  return MicroDom({"tag_":topTag},children,None)


def MicroDom2Dict(listofDoms, keyXlat=None, valueXlat=None, recurse=None):
  """?<_>Take a list of Doms and transform them into a dictionary using an overrideable key and value.
    By default the key will be the dom tag, and the value the node
    But you can pass in transformation functions that take the node as a parameter and return a key.  If you don't want this node in the dictionary, return None
    ditto for value and recurse
    <arg name='keyXlat'>Key transformation function</arg>
    <arg name='valueXlat'>Value transformation function</arg>
    <arg name='recurse'>recursion selection function.  The function should return true if you want to go into that node</arg>
    <returns>A nested dictionary</returns>
    </_>"""
  ret = {}
  if keyXlat is None: keyXlat = lambda x: x.tag_
  if valueXlat is None: valueXlat = lambda x: x
  for n in listofDoms:
    k = keyXlat(n)
    if k is not None:
      ret[keyXlat(n)] = valueXlat(n)
    if recurse and recurse(n):
      ret.update(MicroDom2Dict(n.children_,keyXlat,valueXlat,recurse))

  return ret


