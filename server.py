from dataclasses import dataclass
import socket #provides connection between client viz browser here and server
import json #provides json functionality
from urllib.parse import urlsplit, parse_qs
import cgi

BUFF_SIZE = 1024

class HTTPServer:#The actual HTTP server class.

    headers = {
        'Server': "Shubhi's server",#name of the server 
        'Content-Type': 'text/html',#type of content 
    }

    status_codes = { #status codes 
        200: 'OK',
        404: 'Not Found',
        301: 'Moved Permanently',
        400: 'Bad Request',
    }

    def __init__(self, host='127.0.0.1', port=8080):#address of server and port of server
        self.host = host
        self.port = port
        self.method = None
        self.uri = None
        self.http_version = '1.1' # default to HTTP/1.1 

    def start(self): #Method for starting the server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#create socket object with IP address and network type
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)#SO_REUSEADDR option should be set for all sockets being bound  to the port you want to bind multiple socket onto, not only for new socket.
        s.bind((self.host, self.port))#binds the socket object to the address and port
        s.listen(1)# start listening for connections here atmost 5 connections
        print("Listening at", s.getsockname())
        while True:
            c, addr = s.accept()#accept client requests
            print("Connected by", addr) 
            data = b''
            while True:
                dataNew = c.recv(BUFF_SIZE)
                data += dataNew
                if len(dataNew) < BUFF_SIZE:
                    break
            print("ALL DATA: ", data)
            print("length: ", len(data))
            response= self.handle_request(data)#handle_request method which will then returns a response
            c.sendall(response)# send back the data to client
            c.close()# close the connection
    
    def handle_request(self, data):#handles requests
        #print(data.decode())#decode the data
        lines = data.splitlines()#here we parse the request line to get the method , uri and http version
        request_line = lines[0].split()#request line is the first line of the request
        method, url = request_line[0].decode(), request_line[1].decode()#method is the first element of the request line and url is the second element
        path, query = urlsplit(url).path, urlsplit(url).query
        params = parse_qs(query)

        if(method == 'GET' and path == '/isPrime'):#if the method is GET and the endpoint is /isPrime
            return self.handle_isPrime(params)#return the response
        elif(method == 'POST' and path == '/upload'):#if the method is GET and the endpoint is /upload
            return self.handle_upload(data)#return the response
        else:
            return self.response(404, {'error': '404 Not found'})

    def handle_isPrime(self, params):
        if "number" not in params:
            return self.response(400, {'error': '400 Bad Request'})
        try:
            number = int(params["number"][0])
            body = {'number': number, 'isPrime': self.is_prime(number)}
            return self.response(200, body)
        except ValueError:
            return self.response(400, {'error': 'Lutfen tam sayi giriniz'})

    def is_prime(self,n):
        if(n > 1):
            for i in range(2,n):
                if (n%i) == 0:
                    return False
            return True
        return False
        
    def handle_upload(self, data):
        #print(data)
        return self.response(200, {'message': 'Uploaded'})  

    def response(self, status_code, body):# returns response line based on status code
        reason = self.status_codes[status_code]#key status returns corresponding values as reason
        response_line = 'HTTP/1.1 %s %s\r\n' % (status_code, reason)#HTTP/1.1 200 OK
        return b''.join([response_line.encode(), b'\r\n', json.dumps(body).encode()])#joins all the components together

if __name__ == '__main__':
    server = HTTPServer()
    server.start()