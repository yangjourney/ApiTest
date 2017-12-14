import json
from datetime import date, datetime
def read(obj,key):
    collect = list()
    for k in obj:
        v = obj[k]
        if isinstance(v,dict):
            collect.extend(read(v,k))
        elif isinstance(v,list):
            if key=='':
                collect.extend(readList(v,k))
            else:
                if isinstance(readList(v,key+"."+k),list):
                    collect.extend(readList(v,key+"."+k))
                else:
                    collect.append(readList(v,key+"."+k))
        else:
            if key=='':
                collect.append({k:v})
            else:
                collect.append({str(key)+"."+k:v})
    return collect
    
def readList(obj,key):
    collect = list()
    res = None
    for index,item in enumerate(obj):
        if isinstance(item,dict):
            for k in item:
                v = item[k]
                if isinstance(v,dict):
                    collect.extend(read(v,key+"["+str(index)+"]"+"."+k))
                elif isinstance(v,list):
                    if isinstance(readList(v,key+"["+str(index)+"]"+"."+k),list):
                        collect.extend(readList(v,key+"["+str(index)+"]"+"."+k))
                    else:
                        collect.append(readList(v,key+"["+str(index)+"]"+"."+k))
                else:
                    collect.append({key+"["+str(index)+"]"+"."+k:v})
        else:
            res = {str(key):obj}
    if res is None:
        return collect
    else:
        return res

#custom encoder for datetime format data while converting object into json string
class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)