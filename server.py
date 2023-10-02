import os
import socketserver

class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024).strip()
        self.data = self.data.decode("utf-8")

        # Initial setup of variables and getting correct terms

        # split code for the first section of the header
        self.methodSplit = self.data.split("\r\n")[0].split(" ")

        # get the request type from the first parameter of the header
        self.requestType = self.methodSplit[0]

        # get request link
        self.requestLink = self.methodSplit[1]
        
        #base link which allow deal with local host vs 127.0.0.1 test so have same base url 
        self.baseUrl = self.data.split("\r\nHost: ")[1].split("\r\n")[0]

        # esnure that if not GET type request we can show 405 error
        if self.requestType != "GET":
            self.show_405_status()
        else:

            # handle getting correct file type for html or css
            self.requestExtension = ''
            if '.html' in self.requestLink or self.requestLink == '/' or self.requestLink == '/deep/' or  self.requestLink == '/hardcode' or  self.requestLink == '/hardcode/':
                self.requestExtension = 'html'
            if '.css' in self.requestLink:
                self.requestExtension = 'css'

            # base link redirect to 
            if self.requestLink == '/' :
                self.requestPath = self.get_path('/index.html')
            elif self.requestLink == "/hardcode" or self.requestLink == "/hardcode/" or self.requestLink == "/hardcode/index.html" :
                self.requestPath = self.get_path('/hardcode/index.html')
            elif self.requestLink == "/deep":
                self.send_301_request()
            elif self.requestLink == "/deep/":
                self.requestPath = self.get_path('/deep/index.html')
            elif self.requestLink in ['/deep/index.html', '/index.html', '/base.css', '/deep/deep.css']:
                self.requestPath = self.get_path(self.requestLink)
            else:
                self.show_404_status()
                return  # Return to stop processing further
              

            if os.path.exists(self.requestPath):
                    self.send_200_request(self.requestExtension, self.requestPath)
            else:
                self.show_404_status()

    # get base path absolute to www directory
    def get_path(self, requestPage):
        basePath = os.path.abspath("www")
        return (basePath + requestPage)

    def send_301_request(self):
        self.request.sendall(b'HTTP/1.1 301 Moved Permanently\r\n')
        self.request.sendall(bytearray('Location: http://'+self.baseUrl+'/deep/\r\n','utf8'))
        self.request.sendall(b'\r\n') 

    def show_404_status(self):
        self.request.sendall(b'HTTP/1.1 404 Not Found\r\n\r\n')
        self.request.sendall(b'404 Not Found\r\n')

    def show_405_status(self):
        self.request.sendall(b'HTTP/1.1 405 Method Not Allowed\r\n\r\n')
        self.request.sendall(b'405 Method Not Allowed\r\n')

    def send_200_request(self, requestType, path):
        # read file and open it 
        fileLocal = open(path).read()
        

        ## based on request type for page we pass in mime type for html  or css
        if requestType == 'css':
            mimeExtType = 'text/css'

        if requestType == 'html':
            mimeExtType = 'text/html'

            
        # send info
        self.request.sendall(b'HTTP/1.1 200 OK\r\n')
        self.request.sendall(bytearray('Content-Type: '+mimeExtType+'\r\n\r\n', 'utf-8'))
        self.request.sendall(bytearray(fileLocal, 'utf-8'))
    
if __name__ == "__main__":
    HOST, PORT = "127.0.0.1", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()


