import socket
import re # only used for get file content's index bounds
from urllib.parse import urlsplit, parse_qs # only used for parse url request line (ex. /isPrime?number=13, it parses endpoint and parameters) 
from handler import Handler # imports handler.py

# hosti port and buffsize can set from here as constant
HOST = "127.0.0.1"
PORT = 8080
BUFF_SIZE = 1024
# this globals helps catch wrong requests in /upload endpoint
global boundary, null_filename

def receive(sock):

    global boundary, null_filename
    data = b''
    data += sock.recv(BUFF_SIZE) 
    # check filename argument in data (first received)
    null_filename = False
    if b'filename' not in data or b'filename=""' in data:
        null_filename = True
    # check boundary in data (first received)
    boundary = None
    lines = data.splitlines()
    for line in lines:
        if b'boundary' in line:
            boundary = line.split(b'=')[1]
            break
    # if boundary exists and filename is not wrong, it means its /upload endpoint. take other packets if exists.
    if boundary and not null_filename:
        # get packets until find last packet
        while True:
            new_data = sock.recv(BUFF_SIZE)
            if not new_data: # means last packet
                break
            data += new_data
            if boundary + b'--' in new_data: # means last packet as eof
                break
    return data

def request(data, connection):
    
    lines = data.splitlines()
    request_line = lines[0].split() # first line is request line that includes connection infos (method, endpoint, parameters)
    method = request_line[0].decode() # get method from request_line
    url = request_line[1].decode() # get url from request_line
    endpoint, query = urlsplit(url).path, urlsplit(url).query # parse url as endpoint and query
    parameters = parse_qs(query) # parse parameters

    response = ""
    # handle GET endpoints
    if method == 'GET':
        if endpoint == '/isPrime':
            response = handler.isPrime(parameters)
        elif endpoint == '/download':
            response = handler.download(parameters)
        else:
            response = handler.response(404, {'message': 'Request not found!'})
    # handle POST endpoints
    elif(method == 'POST' and endpoint == '/upload'):
        # boundary must be correct in upload method
        global boundary
        if boundary:
            if null_filename: # filename cannot be null in upload method
                response = handler.response(404, {'message': 'Missing file!'})
            else:
                boundary_index = lines.index(b'--' + boundary) # get boundary index
                # get filename in line thats after the line of boundary places
                filename = lines[boundary_index+1].split(b'filename=')[1].split(b'\r\n')[0].decode().replace('"', '') 
                content_type = re.search(b'Content-Type:(.+?)\r\n\r\n', data)
                # get file content it places after content type and finishes at --boundary
                file_content = data.split(content_type.group(1) + b'\r\n\r\n')[1].split(b'\r\n--' + boundary + b'--')[0]
                response = handler.upload(filename, file_content)
        # if endpoint is upload and there is not a correct boundary, there is an error
        else:
            response = handler.response(404, {'message': 'Boundary not found! Please enter correct multipart/form-data'})
    # handle DELETE endpoints
    elif(method == 'DELETE' and endpoint == '/remove'):
        response = handler.remove(parameters)
    # handle PUT endpoints
    elif(method == 'PUT' and endpoint == '/rename'):
        response = handler.rename(parameters)
    # if method could not be handled, response 404 ERROR
    else:
        response = handler.response(404, {'message': 'Request not found!'})

    connection.sendall(response)


handler = Handler() # call handler class
my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # default socket options
my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # this closes socket completely. it blocks "Port is already open" error
my_socket.bind((HOST, PORT))
my_socket.listen(5) # only 5 client at a time
print("Listening...") 

while True: 
    # listen socket in infinite loop
    connection, address = my_socket.accept()
    print("Connection from: ", address) # info message 
    data = receive(connection) # call receive method to get packets
    request(data, connection) 
    connection.close()

