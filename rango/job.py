import pymysql as mdb
from rango.models import Project,Module,Report,Api,Case,DbConfigure
import json
from util import CustomEncoder
from rango.resttest import Test,TestConfig,Validator
import util
import resttest
import reportlab.lib.fonts
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import inch 
def test(case,user):
#If exist non empty check sql query statements, it will execute them
    project = case.api.module.project
    dbconfigure = DbConfigure.objects.get(project=project)
    dbresult = ""
    if case.check_sql != "":
        dbresult = run_sql(case.check_sql,dbconfigure.address,dbconfigure.username,dbconfigure.password,dbconfigure.dbname)

    url = case.api.url
    method = case.api.method
    headers = case.api.headers
    body = case.body
    if body != "":
        body = body.replace("\r\n"," ")
    base_url = case.api.module.project.domain
    expected_status = case.expected_status
    if case.expected == '':
        expected = None
    else:
        print (util.read(json.loads(case.expected),''))
        expected = util.read(json.loads(case.expected),'')
    testset = case.api.module.name
    print_bodies = True
    
    test = Test()
    if method!="POST" and method!="PUT":
        test.url = base_url+url+body
    else:
        test.url = base_url+url
    test.method = method
    test.expected_status = [expected_status]
    
    #convert headers JSON into list
    if headers.strip()!='':
        test.headers = json.loads(headers)
    test.body = body

    #convert expected information into validator content
    if expected is not None:
        if isinstance(expected, list): 
            for var in expected:
                if isinstance(var,dict):
                    for (d,x) in var.items():
                        validator = Validator()
                        if not isinstance(d, str):
                            d = d.encode('utf-8')

                        d = d.replace('[','.')
                        d = d.replace(']','')
                        d = d.replace('.','/')

                        validator.query = d
                        validator.expected = x
                        validator.operator = validator.operator
                        if test.validators is None:
                            test.validators = list()
                        test.validators.append(validator)
    
    config = TestConfig()
    config.testset = testset
    config.print_bodies = print_bodies
    result = resttest.run_test(test, test_config = config)

    #Update or generate new report for the case
    reports = Report.objects.filter(case=case)
    if len(reports)==0:
        report = Report(content=result.body,case=case,created_user= user,status=result.passed)
        report.detail = json.dumps(result.detail, ensure_ascii=False)
        report.error = json.dumps(result.error, ensure_ascii=False)
        report.dbresult = dbresult
        report.save()
    else:
        report = reports[0]
        report.detail = json.dumps(result.detail,ensure_ascii=False)
        report.error = json.dumps(result.error, ensure_ascii=False)
        report.content = result.body
        report.created_user = user
        report.dbresult = dbresult
        report.status = result.passed
        report.save()    

#execute sql script file
def run_sql_file(filename, address,username,password):
    try:
        connection = mdb.connect(address, username, password)
        file = open(filename, 'r')
        sql = s = " ".join(file.readlines())
        cursor = connection.cursor()
        cursor.execute(sql)
        cursor.close()
        connection.commit()
        connection.close()
    except:
        print ("errors ignored")

#execute sql query statements
def run_sql(sql,address,username,password,dbname):
    result = ""
    try:
        connection = mdb.connect(address, username, password,dbname)
        cursor = connection.cursor(mdb.cursors.DictCursor)
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()      
        connection.commit()
        connection.close()
    except mdb.Error as e:
        result=e
    if isinstance(result,tuple):
        try:
            result = json.dumps(result,cls=CustomEncoder)
        except:
            print ("")
    return result

#how to invoke?
#canvas = Canvas('/home/report.pdf')
#export_report_pdf(canvas, "test for REPORTLAB!",reports)
#canvas.showPage() 
#canvas.save()
def export_report_pdf(canvas, headtext,reports):
    canvas.setFont("Helvetica-Bold", 11.5)  
    canvas.drawString(1*inch, 10.5*inch, headtext)  
    canvas.line(1*inch, 10*inch, 7.5*inch, 10*inch)
    