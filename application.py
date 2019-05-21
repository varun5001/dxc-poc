#!/usr/bin/python3
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
import sqlalchemy
import sqlite3
from joblib import dump, load

db_connect = create_engine('sqlite:///chinook.db')
app = Flask(__name__)
api = Api(app)


class Employees(Resource):
    def get(self):
        print('In get.....')
        conn = db_connect.connect() # connect to database
        query = conn.execute("select * from employees") # This line performs query and returns json result
        return {'employees': [i[0] for i in query.cursor.fetchall()]} # Fetches first column that is Employee ID
    
    def post(self):
        conn = db_connect.connect()
        print(request.json)
        LastName = request.json['LastName']
        FirstName = request.json['FirstName']
        Title = request.json['Title']
        ReportsTo = request.json['ReportsTo']
        BirthDate = request.json['BirthDate']
        HireDate = request.json['HireDate']
        Address = request.json['Address']
        City = request.json['City']
        State = request.json['State']
        Country = request.json['Country']
        PostalCode = request.json['PostalCode']
        Phone = request.json['Phone']
        Fax = request.json['Fax']
        Email = request.json['Email']
        query = conn.execute("insert into employees values(null,'{0}','{1}','{2}','{3}', \
                             '{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}', \
                             '{13}')".format(LastName,FirstName,Title,
                             ReportsTo, BirthDate, HireDate, Address,
                             City, State, Country, PostalCode, Phone, Fax,
                             Email))
        return {'status':'success'}

    
class Tracks(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute("select trackid, name, composer, unitprice from tracks;")
        result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
        return jsonify(result)

    
class Employees_Name(Resource):
    def get(self, employee_id):
        conn = db_connect.connect()
        query = conn.execute("select * from employees where EmployeeId =%d "  %int(employee_id))
        result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
        return jsonify(result)

@app.route('/post_test', methods=['POST'])
def post_test():
    
        try:
            status = 'Failed'
            #conn = db_connect.connect()
            print(request.json)
            LastName = request.json['LastName']
            FirstName = request.json['FirstName']
            Title = request.json['Title']
            ReportsTo = request.json['ReportsTo']
            BirthDate = request.json['BirthDate']
            HireDate = request.json['HireDate']
            Address = request.json['Address']
            City = request.json['City']
            State = request.json['State']
            Country = request.json['Country']
            PostalCode = request.json['PostalCode']
            Phone = request.json['Phone']
            Fax = request.json['Fax']
            Email = request.json['Email']
            
            '''
            query = conn.execute("insert into employees values(null,'{0}','{1}','{2}','{3}', \
                                '{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}', \
                                '{13}')".format(LastName,FirstName,Title,
                                ReportsTo, BirthDate, HireDate, Address,
                                City, State, Country, PostalCode, Phone, Fax,
                                Email))
            '''
            status = 'success'
        except sqlalchemy.exc.OperationalError:
            print('db locked')
            status = 'Failed because db locked'
        except sqlite3.ProgrammingError:
            print('sqlite programming error')
        except exception as e:
            print(e)
        
        return "{'status':"+status+"'}"
@app.route('/get_test', methods=['GET'])
def get_test():
    print('In get.....')
    conn = db_connect.connect() # connect to database
    #query = conn.execute("select * from employees") # This line performs query and returns json result
    #return {'employees': [i[0] for i in query.cursor.fetchall()]} # Fetches first column that is Employee ID
    return 'Hello'

@app.route('/get_topics', methods=['GET'])
def get_topics():
    tweet = request.args.get('tweet')
    vectorizer = load('tf_vectorizer.joblib') 
    model = load('nmf.joblib')
    #text = "My friend suffering from #lungcancer #lcsm need support from you all. We are also planning to setup #lungcancerawareness meetings in our neighbourhood"
    text = tweet
    nmf_topics = model.transform(vectorizer.transform([text]))[0]
    topic_idx = 0
    json_res = {}
    nmf_map = {'Topic 0':'Lung Cancer',
          'Topic 1':'Breast Cancer and Women',
          'Topic 2':'Diabetes and heart realted',
          'Topic 3':'Early Stage Lung Cancer',
          'Topic 4':'Epilepsy and Seizures',
          'Topic 5':'Heart Stroke'}
    for topic in nmf_map:
        print(topic+' '+nmf_map[topic]+' '+str(nmf_topics[topic_idx]))
        json_res[nmf_map[topic]] = nmf_topics[topic_idx]
        topic_idx+=1
    return str(json_res)

api.add_resource(Employees, '/employees') # Route_1
api.add_resource(Tracks, '/tracks') # Route_2
api.add_resource(Employees_Name, '/employees/<employee_id>') # Route_3



if __name__ == '__main__':
     app.run()
