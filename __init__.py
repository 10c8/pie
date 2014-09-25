##
 # Pie
 # Python Web Framework
 #
 # author William F.
 # version 1.0.9
##

import os, sys, re
from pieserver import PieServer

class Pie(object):
    versionTag = "<!-- Pie v1.0.9 -->\r\n"
    
    def __init__(self):
        print "[Pie] Initialized."
    
    def run(self, pie, pages, port=8080, path="www", fof="404.html"):
        try:
            print "[Pie] Running."
            
            self.server = PieServer(pie, pages, port, path, fof)
            self.server.run()
        except:
            print "[Pie] Failed to start."
            print sys.exc_info()
    
    def loadTemplate(self, template, replace):
        templatep = open(template)
        template = templatep.read()
        templatep.close()
        
        tags = re.compile("\{\w+\}").findall(template)
        
        for tag in tags:
            result = ""
            for item in replace[tag[1:-1]]:
                result += item
            template = template.replace(tag, result)
        
        return template
    
    def tag(self, name, attr="", *content):
        stag = "<"+ name +" "+ attr +">"
        etag = "</"+ name +">"
        
        tag = stag
        
        for line in content:
            tag += line
        
        return tag + etag

    def meta(self, name="", httpEquiv="", content=""):
        tag = "<meta"
        if name != "": tag += " name=\""+ name +"\""
        if httpEquiv != "": tag += " http-equiv=\""+ content +"\""
        if content != "": tag += " content=\""+ content +"\""
        tag += " />"
        
        return tag
    
    def script(self, src=""):
        return "<script src=\""+ src +"\"></script>"
    
    def link(self, rel="stylesheet", src=False, href=False, type=False):
        return ("<link rel=\""+ rel +"\" "+
               ("src=\""+ src +"\" " if src else "")+
               ("href=\""+ href +"\" " if href else "")+
               ("type=\""+ type +"\" " if type else "")+
                "/>")
        
    def query(self, name):
        if name in self._query:
            return self._query[name]
        else:
            return ""
