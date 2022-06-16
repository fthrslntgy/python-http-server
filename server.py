from fileinput import filename
import socket
import re
from urllib.parse import urlsplit, parse_qs
from handler import Handler

HOST = "127.0.0.1"
PORT = 8080
BUFF_SIZE = 1024
global boundary
global null_filename

def recvall(sock):

    global boundary, null_filename

    data = b''
    packet = sock.recv(BUFF_SIZE)
    data += packet
    lines = packet.splitlines()
    boundary = None
    null_filename = False

    for line in lines:
        if b'boundary' in line:
            boundary = line.split(b'=')[1]
            if b'filename' not in packet or b'filename=""' in packet:
                null_filename = True
            break

    if boundary and not null_filename:
        while True:
            packet = sock.recv(BUFF_SIZE)
            if not packet:
                break
            data += packet
            if boundary + b'--' in packet:
                break
    return data

def handle_request(data, connection):

    lines = data.splitlines()
    request_line = lines[0].split()
    method, url = request_line[0].decode(), request_line[1].decode()
    path, query = urlsplit(url).path, urlsplit(url).query
    parameters = parse_qs(query)

    response = ""

    if(method == 'GET' and path == '/isPrime'):
        response = handler.isPrime(parameters)

    elif(method == 'POST' and path == '/upload'):

        global boundary

        if boundary:
            b_index = lines.index(b'--' + boundary)

            if null_filename:
                response = handler.response(404, {'message': 'Missing file!'})

            else:
                filename = lines[b_index+1].split(b'filename=')[1].split(b'\r\n')[0].decode().replace('"', '')
                m = re.search(b'Content-Type:(.+?)\r\n\r\n', data)
                file_content = data.split(m.group(1) + b'\r\n\r\n')[1].split(b'\r\n--' + boundary + b'--')[0]
                response = handler.upload(filename, file_content)
        
        else:
            response = handler.response(404, {'message': 'Boundary not found! Please enter correct multipart/form-data'})

    elif(method == 'DELETE' and path == '/remove'):
        response = handler.remove(parameters)

    elif(method == 'PUT' and path == '/rename'):
        response = handler.rename(parameters)

    elif(method == 'GET' and path == '/download'):
        response = handler.download(parameters)

    else:
        response = handler.response(404, {'message': 'Request not found!'})

    connection.sendall(response)


handler = Handler()
my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_socket.bind((HOST, PORT))
my_socket.listen(1)
print("Listening...")

while True:
    connection, address = my_socket.accept()
    print("Connection from: ", address) 
    data = recvall(connection)
    handle_request(data, connection)
    connection.close()

