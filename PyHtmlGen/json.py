from htmldoc import *
from chunk import *
from module import *
from js import *

#? This global variable is used to specify where the javascript files are on the server.
JavascriptDir = "./"

#<_ view="internal">A Marker showing where the RPCs are installed</_>
rpcim = Marker("js")

rpcs=["""
<script language='JavaScript'>
var server = {};
// RPC calls are installed here
""", rpcim,"// End RPC call installation.\n</script>\n"]

#? The json module is defined
jsonModule = Module("json",jsm,[("head",["<script language='JavaScript' src='%sjson2.js'>1;</script>\n<script language='JavaScript' src='%sjsonreq.js'>1;</script>\n" % (JavascriptDir,JavascriptDir)] + rpcs) ])


class DefineRpc:
  def __init__(self,rpcname):
    self.name = rpcname

  def call(self,*jsargs):
    args = ",".join([str(x) for x in jsargs])
    return "server.%s(%s)" % (self.name,args)
    

  def gen(self,doc):
    doc.AddModule(jsModule,LocationBoth)  
    doc.AddModule(jsonModule,LocationBoth)
    doc.Insert("InstallFunction(server, '%s');\n" % self.name,rpcim)

def actionDynGet(element,uri):
  eid = None
  try:  # If its a chunk then use the id.
    eid = element.getId()
  except: # Otherwise assume that the user is passing the id in
    eid = str(element)

  return "ReplaceChildrenWithUri('%s','%s');" % (eid,str(uri))

def actionDynGetScript(element,uri,js):
  eid = None
  try:  # If its a chunk then use the id.
    eid = element.getId()
  except: # Otherwise assume that the user is passing the id in
    eid = str(element)

  return "ReplaceChildrenWithUri('%s','%s'); LoadScript('%s','%s');" % (eid,str(uri),eid + "script", js)



#<example>
def Test():
   import gen

   cdlt = Chunk("Click for Dynamic load test")
   replaceme = Chunk("this will be replaced")
   action(cdlt,"onClick",actionDynGet(replaceme,"testjsondyn.html"))

   rpc = DefineRpc("rpctest")
   b1 = Chunk("RPC")
   action(b1,"onClick",rpc.call("'arg1'",5))

   d = [cdlt,replaceme,rpc,b1]

   gen.WriteFile("testjson.html",d)
    
#</example>
