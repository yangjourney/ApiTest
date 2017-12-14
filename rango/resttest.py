# -*- coding:utf-8 -*- 
import operator,os
import pycurl
import json
import logging
from urllib import urlencode
LOGGING_LEVELS = {'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL}

#Map HTTP method names to curl methods
#Kind of obnoxious that it works this way...
HTTP_METHODS = {u'GET' : pycurl.HTTPGET,
    u'PUT' : pycurl.UPLOAD,
    u'POST' : pycurl.POST,
    u'DELETE'  : 'DELETE'}

class Test(object):
    """ Describes a REST test """
    url  = None
    expected_status = [200]  # expected HTTP status code or codes
    body = None #Request body, if any (for POST/PUT methods)
    headers = dict() #HTTP Headers
    method = u'GET'
    group = u'Default'
    name = u'Unnamed'
    validators = None  # Validators for response body, IE regexes, etc
    stop_on_failure = False
    #In this case, config would be used by all tests following config definition, and in the same scope as tests

    def __init__(self):
        self.headers = dict()
        self.expected_status = [200]

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__)

class Validator:
    """ Validation for a dictionary """
    query = None
    expected = None
    operator = "eq"
    passed = None
    actual = None
    query_delimiter = "/"
    export_as = None

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def validate(self, mydict):
        """ Uses the query as an XPath like query to extract a value from the dict and verify result against expectation """

        if self.query is None:
            raise Exception("Validation missing attribute 'query': " + str(self))

        if not isinstance(self.query, str):
            raise Exception("Validation attribute 'query' type is not str: " + type(self.query).__name__)

        if self.operator is None:
            raise Exception("Validation missing attribute 'operator': " + str(self))

        # from http://stackoverflow.com/questions/7320319/xpath-like-query-for-nested-python-dictionaries
        self.actual = mydict

        try:
            logging.debug("Validator: pre query: " + str(self.actual))
            for x in self.query.strip(self.query_delimiter).split(self.query_delimiter):
                logging.debug("Validator: x = " + x)
                try:
                    x = int(x)
                    self.actual = self.actual[x]
                except ValueError:
                    self.actual = self.actual.get(x)
        except:
            logging.debug("Validator: exception applying query")
            pass

        # default to false, if we have a check it has to hit either count or expected checks!
        output = False

        if self.operator == "exists":
            # require actual value
            logging.debug("Validator: exists check")
            output = True if self.actual is not None else False
        elif self.operator == "empty":
            # expect no actual value
            logging.debug("Validator: empty check" )
            output = True if self.actual is None else False
        elif self.actual is None:
            # all tests beyond here require actual to be set
            logging.debug("Validator: actual is None")
            output = False
        elif self.expected is None:
            raise Exception("Validation missing attribute 'expected': " + str(self))
        elif self.operator == "count":
            self.actual = len(self.actual) # for a count, actual is the count of the collection
            logging.debug("Validator: count check")
            output = True if self.actual == self.expected else False
        else:

            # any special case operators here:
            if self.operator == "contains":
                if isinstance(self.actual, dict) or isinstance(self.actual, list):
                    output = True if self.expected in self.actual else False
                else:
                    raise Exception("Attempted to use 'contains' operator on non-collection type: " + type(self.actual).__name__)
            else:
                # operator list: https://docs.python.org/2/library/operator.html
                myoperator = getattr(operator, self.operator)

                output = True if myoperator(self.actual, self.expected) == True else False

        # if export_as is set, export to environ
        if self.export_as is not None and self.actual is not None:
            logging.debug("Validator: export " + self.export_as + " = " + str(self.actual))
            os.environ[self.export_as] = str(self.actual)

        self.passed = output
        
        res = dict()
        res['detail']={"field":self.query,"expected":self.expected,"actual":self.actual}
        res['output']=output
        if output==False:
            res['error']={"field":self.query,"expected":self.expected,"actual":self.actual}
        else:
            res['error']=None
        return res

class TestConfig:
    """ Configuration for a test run """
    timeout = 10  # timeout of tests, in seconds
    print_bodies = False  # Print response bodies in all cases
    retries = 0  # Retries on failures
    test_parallel = False  # Allow parallel execution of tests in a test set, for speed?
    validator_query_delimiter = "/"
    interactive = False

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__)

class TestResponse:
    """ Encapsulates everything about a test response """
    test = None #Test run
    response_code = None
    body = bytearray() #Response body, if tracked
    passed = False
    response_headers = bytearray()
    detail=list()
    error=list()

    def __str__(self):
        return json.dumps(self, default=lambda o: str(o) if isinstance(o, bytearray) else o.__dict__)

    def body_callback(self, buf):
        """ Write response body by pyCurl callback """
        self.body.extend(buf)

    def unicode_body(self):
        return unicode(self.body.decode('UTF-8'))

    def header_callback(self,buf):
        """ Write headers by pyCurl callback """
        self.response_headers.extend(buf) #Optional TODO use chunk or byte-array storage

def lowercase_keys(input_dict):
    """ Take input and if a dictionary, return version with keys all lowercase """
    if not isinstance(input_dict,dict):
        return input_dict

    safe = dict()
    for key,value in input_dict.items():
        safe[str(key).lower()] = value
    return safe

def choose_handler(headers):
    content_type = '';
    if headers is not None:
        content_type=headers.get(u'Content-Type')
    return content_type

def configure_curl(mytest, test_config = TestConfig()):
    """ Create and mostly configure a curl object for test """

    if not isinstance(mytest, Test):
        raise Exception('Need to input a Test type object')
    if not isinstance(test_config, TestConfig):
        raise Exception('Need to input a TestConfig type object for the testconfig')

    curl = pycurl.Curl()
    # curl.setopt(pycurl.VERBOSE, 1)  # Debugging convenience
    curl.setopt(curl.URL, str(mytest.url))
    curl.setopt(curl.TIMEOUT, test_config.timeout)


    #TODO use CURLOPT_READDATA http://pycurl.sourceforge.net/doc/files.html and lazy-read files if possible

    # Set read function for post/put bodies
 
    if mytest.method == u'POST' or mytest.method == u'PUT':
        if mytest.body is not None:
            content_type = choose_handler(mytest.headers)
            if content_type==u'application/json':
                #json post
                curl.setopt(curl.POSTFIELDS,  json.dumps(eval(mytest.body)))
            elif content_type==u'application/x-www-form-urlencoded':
                #form post
                curl.setopt(curl.POSTFIELDS,  urlencode(eval(mytest.body)))

    if mytest.method == u'POST':
        curl.setopt(HTTP_METHODS[u'POST'], 1)
    elif mytest.method == u'PUT':
        curl.setopt(HTTP_METHODS[u'PUT'], 1)
    elif mytest.method == u'DELETE':
        curl.setopt(curl.CUSTOMREQUEST,'DELETE')

    headers = list()
    if mytest.headers: #Convert headers dictionary to list of header entries, tested and working
        for headername, headervalue in mytest.headers.items():
            headers.append(str(headername) + ': ' +str(headervalue))
    headers.append("Expect:")  # Fix for expecting 100-continue from server, which not all servers will send!
    headers.append("Connection: close")
    curl.setopt(curl.HTTPHEADER, headers)

    curl.setopt(pycurl.VERBOSE,1)
    curl.setopt(pycurl.FOLLOWLOCATION, 1)
    curl.setopt(pycurl.MAXREDIRS, 5)
    curl.setopt(pycurl.CONNECTTIMEOUT, 60)
    return curl

def run_test(mytest, test_config = TestConfig()):
    """ Put together test pieces: configure & run actual test, return results """

    curl = configure_curl(mytest, test_config)

    result = TestResponse()

    # reset the body, it holds values from previous runs otherwise
    result.body = bytearray()
    curl.setopt(pycurl.WRITEFUNCTION, result.body_callback)
    curl.setopt(pycurl.HEADERFUNCTION, result.header_callback) #Gets headers

    try:
        curl.perform() #Run the actual call
    except Exception as e:
        print (e)  #TODO figure out how to handle failures where no output is generated IE connection refused

    result.test = mytest
    response_code = curl.getinfo(pycurl.RESPONSE_CODE)
    result.response_code = response_code
    result.passed = response_code in mytest.expected_status
    logging.debug("Initial Test Result, based on expected response code: "+str(result.passed))

    #print str(test_config.print_bodies) + ',' + str(not result.passed) + ' , ' + str(test_config.print_bodies or not result.passed)

    #Print response body if override is set to print all *OR* if test failed (to capture maybe a stack trace)
    if test_config.print_bodies:
        if test_config.interactive:
            print ("RESPONSE:")

    result.detail = list()
    result.error = list()
    # execute validator on body
    if result.passed == True:
        if mytest.validators is not None and isinstance(mytest.validators, list):
            logging.debug("executing this many validators: " + str(len(mytest.validators)))
            myjson = json.loads(str(result.body))
            for validator in mytest.validators:
                # pass delimiter from config to validator
                validator.query_delimiter = test_config.validator_query_delimiter
                # execute validation
                res = validator.validate(myjson)

                result.detail.append(res['detail'])
                if res['error'] is not None:
                    result.error.append(res['error'])
                mypassed = res['output']
                if mypassed == False:
                    result.passed = False
                    # do NOT break, collect all validation data!
                if test_config.interactive:
                    # expected isn't really required, so accomidate with prepending space if it is set, else make it empty (for formatting)
                    myexpected = " " + str(validator.expected) if validator.expected is not None else ""
                    print ("VALIDATOR: " + validator.query + " " + validator.operator + myexpected + " = " + str(validator.passed))
        else:
            logging.debug("no validators found")

    logging.debug(result)

    curl.close()
    return result