import json
import logging
import time
from datetime import datetime

import jwt
import requests
from requests import HTTPError

#Get_Config
#A convience class to get configuration values that we do not want to show 
#(or upload to github) (key, secret, url) from a json file.It also sets up 
#logging for the helper classes. If logging is not set up, will just print 
#to the console.
#Template format is simple
#{
#   "url":"",
#   "key":"",
#   "secret":""
#}
class Get_Config():

    #Initializes the class by taking the configuration file path
    #as an argument, a typical value would be "./config.json".
    def __init__(self, file_path):
        self.file_path = file_path
        with open(self.file_path) as conf:
            self.data = json.load(conf)

    #Returns url value from the configuration file to a variable
    def get_url(self):
        return self.data["url"]

    #Returns key value from the configuration file to a variable
    def get_key(self):
        return self.data["key"]

    #Returns secret value from the configuration file to a variable
    def get_secret(self):
        return self.data["secret"]

    #Sets logging with default level of DEBUG. 
    def set_logging(self, level=logging.DEBUG):
        self.level = level
        logging.basicConfig(
            filename=f'./logs/Bb_helper_log_{datetime.now()}', filemode="w", level=self.level)

#Auth_Helper
#A class to simplify REST API authentication for the Blackboard API.
class Auth_Helper():

    #Initializes the auth helper by taking the target system url,
    # PI key and secret as arguments.
    def __init__(self, url, key, secret):
        self.url = url
        self.key = key
        self.secret = secret

    #Returns the authentication token for Blackboard Learn.
    def learn_auth(self):
        try:
            self.url_token = "/learn/api/public/v1/oauth2/token"
            self.params = {"grant_type": "client_credentials"}
            self.headers = {
                'Content-Type': "application/x-www-form-urlencoded"}
            r = requests.request("POST", self.url+self.url_token, headers=self.headers,
                                 params=self.params, auth=(self.key, self.secret))
            r.raise_for_status()
            data = json.loads(r.text)
            self.learn_token = data["access_token"]
            logging.info("Learn Authentication successful")
            logging.info("Token expires in: "+str(data["expires_in"]))
            return self.learn_token
        except requests.exceptions.HTTPError as e:
            data = json.loads(r.text)
            logging.error(data["error_description"])

    #Returns the authentication token for Blackboard Collaborate.
    def collab_auth(self):
        self.token_url = '/token'
        self.exp = int(round(time.time() * 1000)) + 270000
        self.claims = {"iss": self.key, "sub": self.key, "exp": self.exp}
        # Encode the JWT assertion with the jWT module, that includes claims and the secret.
        self.assertion = jwt.encode(self.claims, self.secret)
        self.credentials = 'urn:ietf:params:oauth:grant-type:jwt-bearer'
        self.headers = {  # Content type is sent as a header
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        #Grant credentials and assertion are sent as parameters
        self.params = {  
            'grant_type': self.credentials,
            'assertion': self.assertion
        }
        try:
            r = requests.request('POST', self.url+self.token_url, params=self.params,
                                 headers=self.headers, auth=(self.key, self.secret))
            r.raise_for_status()
            data = json.loads(r.text)
            logging.info('Collaborate Authentication successful')
            logging.info("Token expires in: "+str(data["expires_in"]))
            self.collab_token = data['access_token']
            return self.collab_token
        except requests.exceptions.HTTPError as e:
            data = json.loads(r.text)
            logging.error(data["error"])

#Bb_requests
#A class to simplify API calls to Blackboard REST APIs, provides functions 
#for GET, POST, PUT, PATCH and DELETE
class Bb_requests():

    #GET request. It takes a GET endpoint from the API, the authentication
    #token and a list of parameters as arguments.
    def Bb_GET(self, endpoint, token, params):
        self.endpoint = endpoint
        self.token = token
        self.params = params
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': "Application/json"
        }
        try:
            r = requests.request('GET', self.endpoint,
                                 headers=self.headers, params=self.params)
            data = json.loads(r.text)
            r.raise_for_status()
            logging.info("GET Request completed")
            return data
        except requests.exceptions.HTTPError as e:
            data = json.loads(r.text)
            logging.error(data["error_description"])

    #POST request. It takes a POST endpoint from the API, the authentication token,
    #a list of parameters, and a json payload as arguments.
    def Bb_POST(self, endpoint, token, params, payload):
        self.endpoint = endpoint
        self.token = token
        self.params = params
        self.payload = payload
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': "Application/json"
        }
        try:
            r = requests.request('POST', self.endpoint,
                                 headers=self.headers, params=self.params, json=self.payload)
            data = json.loads(r.text)
            r.raise_for_status()
            logging.info("POST Request completed")
            return data
        except requests.exceptions.HTTPError as e:
            data = json.loads(r.text)
            logging.error(data["message"])

    #PATCH request. It takes a PATCH endpoint from the API, the authentication token,
    #a list of parameters, and a json payload as arguments. A PATCH requests allows
    #to update a record partially.
    def Bb_PATCH(self, endpoint, token, params, payload):
        self.endpoint = endpoint
        self.token = token
        self.params = params
        self.payload = payload
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': "Application/json"
        }
        try:
            r = requests.request('PATCH', self.endpoint,
                                 headers=self.headers, params=self.params, json=self.payload)
            data = json.loads(r.text)
            r.raise_for_status()
            logging.info("PATCH Request completed")
            return data
        except requests.exceptions.HTTPError as e:
            data = json.loads(r.text)
            logging.error(data["message"])

    #PUT request. It takes a PUT endpoint from the API, the authentication token, 
    #a list of parameters, and a json payload as arguments. A PUT request is meant
    #to update a record entirely.
    def Bb_PUT(self, endpoint, token, params, payload):
        self.endpoint = endpoint
        self.token = token
        self.params = params
        self.payload = payload
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': "Application/json"
        }
        try:
            r = requests.request('PUT', self.endpoint,
                                 headers=self.headers, params=self.params, json=self.payload)
            data = json.loads(r.text)
            r.raise_for_status()
            logging.info("PUT Request completed")
            return data
        except requests.exceptions.HTTPError as e:
            data = json.loads(r.text)
            logging.error(data["message"])

    #DELETE request. It takes a DELETE endpoint from the API, the authentication token
    #and a list of parameters as arguments.
    def Bb_DELETE(self, endpoint, token, params):
        self.endpoint = endpoint
        self.token = token
        self.params = params
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': "Application/json"
        }
        try:
            r = requests.request(
                'DELETE', self.endpoint, headers=self.headers, params=self.params)
            data = json.loads(r.text)
            r.raise_for_status()
            logging.info("DELETE Request completed")
            return data
        except requests.exceptions.HTTPError as e:
            data = json.loads(r.text)
            logging.error(data["message"])

    
class Bb_Utils():

    #Prints the response from any of the above methods in a prettified format to the console.
    def pretty_printer(self, data):
        self.data = data
        print(json.dumps(self.data, indent=4, sort_keys=True))
        logging.info("Results printed to the console.")

    # Checks if a given Learn course exists in the server
    def check_course_id(self, course_id):
        try:
            self.endpoint_courses = "/learn/api/public/v3/courses"
            self.headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': "Application/json"
            }
            self.params = {
                "externalId": course_id,
                "fields": "id"
            }
            r = requests.request(
                'GET', self.url+self.endpoint_courses, headers=self.headers, params=self.params)
            r.raise_for_status()
            data = json.loads(r.text)
            if data["results"]:
                logging.info('The course has been found in the server.')
                return True
            else:
                logging.warning(
                    'The course could not be found, pelase check that the provided course id is the external id')
                return False
        except requests.exceptions.HTTPError as e:
            data = json.loads(r.text)
            logging.error(data["message"])