import os
import json
import math # only for get sqrt of number in checkPrime. this way (bound with sqrt(n)) is max optimized prime control. 

class Handler():

    # constructor method
    def __init__(self):
        # define status codes as dict
        self.status_codes = {
            200: 'OK',
            400: 'BAD REQUEST',
            404: 'NOT FOUND',
        }
        # define http header that is head of all response messages
        self.http_header = 'HTTP/1.1 %s %s\r\n'
        # buff size is length of each file.read() in download method
        self.BUFF_SIZE = 1024

    # creating response message method
    def response(self, status_code, body, download = False):
        # find reason message from code in dict
        reason = self.status_codes[status_code]
        response_line = self.http_header % (status_code, reason)
        # if endpoint is not download
        if not download:
            return b''.join([response_line.encode(), b'\r\n', json.dumps(body).encode()])
        # if endpoint is download
        # body is byte array of file content
        return b''.join([response_line.encode(), b'\r\n', b''.join(body)])

    # checking a number is prime or not method
    def checkPrime(self, number):

        if number < 2:
            return False
        # check primity with take mod of number with numbers bounded 2 and sqrt of number. this is enough for check
        for i in range(2, int(math.sqrt(number)) + 1):
            if (number % i) == 0:
                return False
        return True

    # /isPrime endpoint handler
    def isPrime(self, parameters):
            # check there is a "number" parameter
            if "number" not in parameters:
                return self.response(400, {'message': 'Missing <number> parameter'})
            # check "number" parameter is an integer
            elif not parameters["number"][0].isdigit():
                return self.response(400, {'message': 'Please enter an integer!'})
            # check this number is prime and return
            number = int(parameters["number"][0])
            primity = self.checkPrime(number)
            body = {'number': number, 'isPrime': primity}
            return self.response(200, body)
    
    # /upload endpoint handler
    def upload(self, filename, file_content):
        # open the file with filename and write content into it
        # remember: this methods parameters checks done in server.py before calling here
        with open(filename, 'wb') as file:
            file.write(file_content)
        return self.response(200, {'message': 'File uploaded successfully'})  

    # /rename endpoint handler   
    def rename(self, parameters):
        # check there are "oldFileName" and "newName" parameters
        if "oldFileName" not in parameters or "newName" not in parameters:
            return self.response(400, {'message': 'Missing <oldFileName> or/and <newName> parameter!'})
        # check "oldFileName" exits
        oldFileName = parameters["oldFileName"][0]
        newName = parameters["newName"][0]
        if not os.path.exists(oldFileName):
            return self.response(200, {'message': 'File cannot found!'})
        # if exists, rename it with "newName"
        os.rename(oldFileName, newName)
        return self.response(200, {'message': 'File succesfully renamed!'})

    # /remove endpoint handler
    def remove(self, parameters):
        # check there is "fileName" parameter
        if "fileName" not in parameters:
            return self.response(400, {'message': 'Missing <fileName> parameter'})
        # check "fileName" exits
        fileName = parameters["fileName"][0]
        if not os.path.exists(fileName):
            return self.response(200, {'message': 'File cannot found!'})
        # if exists, remove it
        os.remove(fileName)
        return self.response(200, {'message': 'File successfully deleted!'})

    # /download endpoint handler
    def download(self, parameters):
        # check there is "fileName" parameter
        if "fileName" not in parameters:
            return self.response(400, {'message': 'Missing <fileName> parameter'})
        # check "fileName" exits
        fileName = parameters["fileName"][0]
        if not os.path.exists(fileName):
            return self.response(200, {'message': 'File cannot found!'})
        # if exists, read it and append to array and send this array to response as body
        datas = []
        with open(fileName, 'rb') as file:
            while True:
                data = file.read(self.BUFF_SIZE)
                if data:
                    datas.append(data)
                else: 
                    break
        file.close()
        # remember response method's return changes according to "download" parameter. i send this parameter as True below
        return self.response(200, datas, True) 

        
