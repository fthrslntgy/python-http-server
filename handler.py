import os
import re
import json
import math # only for get sqrt of number in checkPrime. this way (bound with sqrt(n)) is max optimized prime control. 

class Handler():

    # constructor method
    def __init__(self):
        # define status codes as dict
        self.status_codes = {
            200: 'OK',
            400: 'Bad Request',
            404: 'Not Found',
        }
        # define http header that is head of all response messages
        self.http_header = 'HTTP/1.1 %s %s\r\n'

    # creating response message method
    def response(self, status_code, body, download = False):
        # find reason message from code in dict
        reason = self.status_codes[status_code]
        response_line = self.http_header % (status_code, reason)
        if not download:
            return b''.join([response_line.encode(), b'\r\n', json.dumps(body).encode()])
        
        return b''.join([response_line.encode(), b'\r\n', b''.join(body)])

    # checking a number is prime or not method
    def checkPrime(self, number):

        if number < 2:
            return False

        for i in range(2, int(math.sqrt(number)) + 1):
            if (number % i) == 0:
                return False
        return True

    # /isPrime endpoint handler
    def isPrime(self, parameters):
            # check there is a "number" parameter
            if "number" not in parameters:
                return self.response(400, {'error': 'Missing <number> parameter'})
            # check "number" parameter is an integer
            elif not parameters["number"][0].isdigit():
                return self.response(400, {'error': 'Please enter an integer!'})
            # check this number is prime and return
            number = int(parameters["number"][0])
            body = {'number': number, 'isPrime': self.checkPrime(number)}
            return self.response(200, body)
    
    # /upload endpoint handler
    def upload(self, filename, file_content):

        with open(filename, 'wb') as file:
            file.write(file_content)
        return self.response(200, {'message': 'File uploaded successfully'})  

    # /rename endpoint handler   
    def rename(self, parameters):
        
        if "oldFileName" not in parameters or "newName" not in parameters:
            return self.response(400, {'message': 'Missing <oldFileName> or/and <newName> parameter!'})
        
        oldFileName = parameters["oldFileName"][0]
        newName = parameters["newName"][0]
        if not os.path.exists(oldFileName):
            return self.response(404, {'message': 'File cannot found!'})
        
        os.rename(oldFileName, newName)
        return self.response(200, {'message': 'File succesfully renamed!'})

    # /remove endpoint handler
    def remove(self, parameters):

        if "fileName" not in parameters:
            return self.response(400, {'message': 'Missing <fileName> parameter'})
        
        fileName = parameters["fileName"][0]
        if os.path.exists(fileName):
            os.remove(fileName)
            return self.response(200, {'message': 'File successfully deleted!'})
        
        else:
            return self.response(200, {'message': 'File cannot found!'})

    # /download endpoint handler
    def download(self, parameters):
        
        if "fileName" not in parameters:
            return self.response(400, {'message': 'Missing <fileName> parameter'})
        
        fileName = parameters["fileName"][0]
        if not os.path.exists(fileName):
            return self.response(404, {'message': 'File cannot found!'})

        datas = []
        with open(fileName, 'rb') as file:
            while True:
                data = file.read(1024)
                if data:
                    datas.append(data)
                else: 
                    break
        file.close
        return self.response(200, datas, True) 

        