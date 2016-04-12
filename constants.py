#? <section name='xmlAttributes'>
AttrTag   = "tag_"              #? <var>The microdom 'attribute' that is really the node's tag</var>
AttrName  = "name"              #?? This attribute is the defined symbol name.  For example given the declaration "int a", the "name" is "a"
AttrValue = "value"             #?? This attribute is the assigned value.  For example given the declaration "int a = 5", the "value" is "5". OPTIONAL
AttrType  = "type"              #?? This attribute is the type.  For example given the declaration "int a = 5", the "type" is "int". Although this field is OPTIONAL (will be defaulted to ""), it is especially important to supply the type or the valid types (in function arguments) for "untyped" languages so the user/caller knows what to expect.
#? </section>

#? <section name='xmlTags'>

# 

TagConst    = "const"           #?? A Constant definition, for example 'const int b' or '#define FOO'
TagVariable = "var"             #?? Variable definition, for example: 'int a'
TagFunction = "fn"              #?? Function definition
TagParam    = "arg"             #?? An argument to a function. Must be a child of TagFunction
TagClass    = "class"           #?? Class definition
TagMethod   = "method"          #?? Class method definition. Must be a child of TagClass
TagField    = "field"           #?? Field (class/structure member) definition. Must be a child of TagClass
TagCtor     = "ctor"            #?? Constructor definition. Must be a child of TagClass
TagFile     = "file"            #?? File node.  All child nodes are defined in this file.
TagDoc      = "doc"
TagSection  = "section"         #?? Section definition.  A section is an arbitrary construct (i.e. not extracted from to the programming language) that you may use to organise your documentation
TagBrief    = "brief"           #?? Brief help.  Must be a child of a ConstructTag tag.
TagDesc     = "desc"            #?? The full documentation of this item.  Must be a child of a ConstructTag tag.
TagDecl     = "decl"            #?? The function declaration, for example: 'foofn(int a, int b)'.  Must be a child of TagFunction

TagRequires = "requires"        #?? This module requires another library (or include file)

TagRef      = "ref"             #?? A reference to another function or class
TagLicense  = "license"         #?? The file's license
TagReturn   = "return"          #?? The return value
TagException = "exception"      #?? A exception that can be raised

TagVerbatim = "verbatim"        #?? Include the full source text, exactly as shown
TagExcerpt = "excerpt"          #?? Include the full source text, but still interpreting XML
TagInsert = "insert"            #?? Replace this XML object with whatever it references, i.e. <verbatim id="foo">interesting text</verbatim> ... <insert ref="foo" /> becomes <verbatim id="foo">interesting text</verbatim> ... <verbatim id="foo">interesting text</verbatim>
#? </section>

#?? These tags represent language constructs
ConstructTags = [TagVariable,TagFunction,TagClass,TagMethod,TagCtor,TagFile,TagConst,TagSection]

#?? These tags must have a "type" attribute
TypedTags = [TagParam,TagVariable,TagDecl,TagFunction,TagMethod,TagConst,TagException]

#?? These tags are the bottom of the tree
LeafTags = [TagDesc,TagBrief,TagParam,TagField,TagException]

#?? These tags get their own generated files
TagsWithOwnFile = [TagClass,TagFile]

#?? These tags are pulled out of description blocks to be part of the parent block
NoDescTags = [TagBrief,TagParam,TagLicense,TagReturn,TagException,TagRequires, TagDecl] + ConstructTags

#?? There can only be one child tag of this type and name.  If there are 2, they will be merged into one node.
CombinedTags = [TagSection]


#?? Output directory
FilePrefix = "html/"
