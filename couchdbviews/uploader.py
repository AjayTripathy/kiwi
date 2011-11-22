import json
import ast
import sys
import couchdb
import httplib

def main(argv):
  f = open(argv, 'r')
  rawString = f.read()
  dictObj = ast.literal_eval(rawString)
  designDocId = str(dictObj['_id'])
  designDoc = json.dumps(dictObj)
  print designDoc
  server = couchdb.Server()
  for db in server:
    relativePath = "/" + str(db) + "/" + designDocId
    print relativePath 
    connection =  httplib.HTTPConnection('127.0.0.1:5984')
    connection.request('PUT',relativePath , designDoc)
    result = connection.getresponse()
    print result
     

if __name__ == "__main__":
  main(sys.argv[1])
