##
 # PieServer
 # Python Web Server
 #
 # author William F.
 # version 1.1.4
##

###
#   Libraries and Settings
###
import os, sys, socket, re
from os import walk

mime = {
    ## Pie
    ".pie"  : "text/html",
    
	## Text
    ".html" : "text/html",
	".htm"  : "text/html",
	".txt"  : "text/plain",
    ".css"  : "text/css",
	".xml"  : "text/xml",
	".json" : "text/json",
	
	## Application
    ".js"  : "application/javascript",
	".swf" : "application/x-shockwave-flash",
    ".pdf" : "application/pdf",
    ".zip" : "application/zip",
    ".rar" : "application/x-rar-compressed",
    ".ttf" : "application/octet-stream",
    ".otf" : "application/octet-stream",
	
	## Image
	".ico"  : "image/vnd.microsoft.icon",
    ".png"  : "image/png",
    ".gif"  : "image/gif",
    ".jpg"  : "image/jpeg",
    ".jpeg" : "image/jpeg",
    ".bmp"  : "image/bmp",
    ".svg"  : "image/svg+xml",
    
    ## Audio
    ".ogg"  : "audio/ogg",
    ".mp3"  : "audio/mpeg",
    ".webm" : "audio/webm",
    
    ## Video
    ".avi"  : "video/avi",
    ".mp4"  : "video/mp4",
    ".3gp"  : "video/mpeg"
}

###
#   Request Handling
###
class PieServer(object):
    messages = {
        "200": "HTTP/1.1 200 OK\r\n",
        "404": "HTTP/1.1 404 Not Found\r\n",
        "403": "HTTP/1.1 403 Forbidden\r\n"
    }
    
    serverHeader = "Server: PieServer 1.1.4 (Pie 1.0.9)\r\n"
    
    def __init__(self, pie, pages, port, path, fof):
        try:
            print "[PieServer] Server started at "+ str(port) +".\r\n"
            
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind(('', port))
            self.server.listen(256)
            
            self.path = (path + "/" if path[-1] != "/" else path)
            
            if type(fof) is str:
                self.fof = self.path + fof
            else:
                self.fof = fof
            
            self.pages = pages
            self.pie = pie
        except:
            print "[PieServer] Could not start server."
            print sys.exc_info()
    
    def run(self):
        while True:
            client, address = self.server.accept()
            
            request = client.recv(1024)
            
            if request != "":
                self.handleRequest(client, request, address[0])
    
    def handleRequest(self, client, request, address):
        filep = request.split()[1].split("?")[0]
        if filep == "/": filep = "index.html"
        else: filep = filep[1:].split("?")[0]
        
        ext = "." + filep.split(".")[-1]
        if ext in mime: ext = mime[ext]
        else: ext = "text/plain"
        
        reg = re.compile("(\w+)[=] ?(\w+)")
        self.pie._query = dict(reg.findall(request.split("\r\n")[0].split()[1]))
        
        print str(address) +" ["+ self.path + filep +"]"
        
        self.getFile(client, self.path + filep, ext)
    
    def getFile(self, client, filep, mime):
        def throwFof():
            client.send(
                self.messages["404"] +
                self.serverHeader +
                "Content-Type: text/html\r\n\r\n"
            )
            
            if type(self.fof) is not str:
                content = self.pie.versionTag + self.fof.Pie()
            
                for line in content:
                    client.send(line)
                
                print "File not found:", filep
            else:
                try:
                    fofp = open(self.fof, "r")
                    fof = fofp.read()
                
                    for line in fof:
                        client.send(line)
                
                    fofp.close()
                except:
                    print "File not found:", self.fof
                    
        if filep in self.pages:
            content = self.pie.versionTag + self.pages[filep].Pie()
            
            client.send(
                self.messages["200"] +
                self.serverHeader +
                "Content-type: "+ mime +"\r\n"
                "Content-Length: "+ str(len("".join(content))) +"\r\n\r\n"
            )
            
            for line in content:
                client.send(line)
        elif os.path.isdir(filep):
            try:
                if filep[-1] == "/":
                    filep = filep[:-1]
            
                for name in ["html", "htm", "pie"]:
                    if os.path.isfile(filep +"/index."+ name):
                        filep = filep +"/index."+ name
                        listFolder = False
                    else:
                        listFolder = True
                
                if listFolder:
                    if os.path.isfile(filep +"/.pie_disallow"):
                        client.send(
                            self.messages["403"] +
                            self.serverHeader +"\r\n"
                            "[PieServer] You don't have permission to access this folder."
                        )
                    else:
                        client.send(
                            self.messages["200"] +
                            self.serverHeader +
                            "Content-type: text/html\r\n\r\n" +
                            self.pie.versionTag +
                            """
                            <html>
                                <head>
                                    <title>Pie | /""" + filep + """</title>
                                </head>
                                <body>
                            """
                        )
                    
                        baseDir = os.listdir(filep)
                        currDir = filep.split("/")
                        currDir.remove(currDir[0])
                        currDir = "/".join(currDir)
                    
                        folders, files = ([], [])
                    
                        for name in baseDir:
                            path = os.path.join(filep, name)
                        
                            if os.path.isdir(path):
                                folders.append(path.split("/")[-1])
                            else:
                                files.append(path.split("/")[-1])
                    
                        for folder in folders:
                            client.send("<a href=\"/"+ currDir +"/"+ folder +"\">/"+ folder +"</a><br>")
                    
                        for name in files:
                            client.send("<a href=\""+ currDir.split("/")[-1] +"/"+ name +"\">"+ name +"</a><br>")
                    
                        client.send(
                            """
                                </body>
                            </html>
                            """
                        )
                    
                else:
                    contentp = open(filep, "r")
                    content = contentp.read()
                    
                    client.send(
                        self.messages["200"] +
                        self.serverHeader +
                        "Content-type: text/html\r\n"
                        "Content-Length: "+ str(len(content)) +"\r\n\r\n"
                    )
                    
                    for line in content:
                        client.send(line)
                    
                    contentp.close()
            except:
                print "File not found:", filep
        elif os.path.isfile(filep):
            try:
                contentp = open(filep, "r")
                content = contentp.read()
                
                client.send(
                    self.messages["200"] +
                    self.serverHeader +
                    "Content-type: "+ mime +"\r\n"
                    "Content-Length: "+ str(len(content)) +"\r\n\r\n"
                )
                
                for line in content:
                    client.send(line)
                
                contentp.close()
            except:
                print "File not found:", filep
        else: 
            throwFof()
        
        client.close()
