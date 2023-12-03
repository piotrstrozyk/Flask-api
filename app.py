import re
import os
from flask import Blueprint, Flask, jsonify, request
from neo4j import GraphDatabase
from dotenv import load_dotenv



app = Flask(__name__)
load_dotenv()

uri = os.getenv("URI")
user = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
driver = GraphDatabase.driver(uri, auth=("neo4j", password), database="neo4j")

departments = Blueprint('departments', __name__)
empl = Blueprint('departments', __name__)

#3 ////////////////////////////////////////////////////////////////////////////

def allEmployees(tx, sort: str = '', filter: str = '', filterType: str = ''):
    query = "MATCH (e:Employee) RETURN e"  
    
    if (sort == 'name'):
        query = "MATCH (e:Employee) RETURN e ORDER BY e.name"
    elif (sort == 'surname'):
        query = "MATCH (e:Employee) RETURN e ORDER BY e.surname"
    elif (sort == 'position'):
        query = "MATCH (e:Employee) RETURN e ORDER BY e.position"

    if (filterType == 'name'):
        query = f"MATCH (e:Employee) WHERE e.name CONTAINS '{filter}' RETURN e"
    if (filterType == 'surname'):
        query = f"MATCH (e:Employee) WHERE e.surname CONTAINS '{filter}' RETURN e"
    if (filterType == 'position'):
        query = f"MATCH (e:Employee) WHERE e.position CONTAINS '{filter}' RETURN e"
    results = tx.run(query).data()
    employees = [{'name': result['e']['name'],
               'surname': result['e']['surname']} for result in results]
    return employees


@empl.route('/employees', methods=['GET'])
def allEmployeesRoute():
    args = request.args
    sort = args.get("sort")
    filter = args.get("filter")
    filterType = args.get("filterType")
    with driver.session() as session:
        employees = session.execute_read(
            allEmployees, sort, filter, filterType)
    res = {'employees': employees}
    return jsonify(res)

#///////////////////////////////////////////////////////////////

#4./////////////////////////////////////////////////////////

def addEmployee(tx, name, surname, position, department):
    query = f"MATCH (e:Employee) WHERE e.name='{name}' AND e.surname='{surname}' AND e.position='{position}' RETURN e"
    res = tx.run(query, name=name).data()
    if res:
        return 'This employee already exists'
    else:
        query = f"CREATE ({name}:Employee {{name:'{name}', surname:'{surname}', position:'{position}'}})"
        tx.run(query, name=name, surname=surname, position=position)
        
@empl.route('/employees', methods=['POST'])
def addEmployeeRoute():
    name = request.form['name']
    surname = request.form['surname']
    position = request.form['position']
    department = request.form['department']
    
    with driver.session() as session:
        session.execute_write(addEmployee, name, surname, position, department)

    res = {'status': 'success'}
    return jsonify(res)
        

#5.////////////////////////////////////////////////////

def updateEmployee(tx, name, surname, new_name, new_surname, new_position, new_department):
    query = f"MATCH (m:Employee)-[r]-(d:Department) WHERE m.name='{name}' AND m.surname='{surname}' RETURN m,d,r"
    res = tx.run(query, name=name, surname=surname).data()

    if res:
        query = f"MATCH (m:Employee) WHERE m.name='{name}' AND m.surname='{surname}' SET m.name='{new_name}', m.surname='{new_surname}', m.position='${new_position}'"
        query1 = f"MATCH (m:Employee {{name: '{name}', surname: '{surname}'}})-[r:WORKS_IN]->(d:Department {{name:'{res[0]['d']['name']}'}}) DELETE r"
        query2 = f"""MATCH (a:Employee),(b:Department) WHERE a.name = '{name}' AND a.surname = '{surname}' AND b.name = '{new_department}' CREATE (a)-[r:WORKS_IN]->(b) RETURN type(r)"""
        tx.run(query, name=name, surname=surname, new_name=new_name,
               new_surname=new_surname, new_position=new_position)
        tx.run(query1, name=name, surname=surname)
        tx.run(query2, name=name, surname=surname,
               new_department=new_department)
        return {'name': new_name, 'surname': new_surname, 'position': new_position, 'New department': new_department}    
    else:
        return None

@empl.route('/employees/<string:person>', methods=['PUT'])
def updateEmployeeRoute(person):
    person1 = re.split('(?<=.)(?=[A-Z])', person)
    name = person1[0]
    surname = person1[1]
    new_name = request.form['name']
    new_surname = request.form['surname']
    new_department = request.form['department']
    new_position = request.form['position']

    with driver.session() as session:
        employee = session.execute_write(
            updateEmployee, name, surname, new_name, new_surname, new_department, new_position)

    if not employee:
        response = {'message': f'Employee {person}not found'}
        return jsonify(response), 404
    else:
        response = {'status': 'success'}
        return jsonify(response)
#///////////////////////////////////////////////////////

#6.////////////////////////////////////////////////////

def deleteEmployee(tx, name: str, surname: str):
    query = f"MATCH (m:Employee)-[r]-(d:Department) WHERE m.name='{name}' AND m.surname='{surname}' RETURN m,d,r"
    res = tx.run(query, name=name, surname=surname).data()
    if not res:
        return None
    else:
        query = f"MATCH (m:Employee) WHERE m.name='{name}' AND m.surname='{surname}' DETACH DELETE m"
        tx.run(query, name=name, surname=surname)
        if (len(res) > 1):
            query = f"MATCH (m:Employee)-[r:WORKS_IN]-(d:Department {{name:'{res[0]['d']['name']}'}}) RETURN m"
            results = tx.run(query).data()
            if (len(results) == 0):
                query = f"MATCH (d:Department) WHERE d.name='{res[0]['d']['name']}' DETACH DELETE d"
                tx.run(query, name=name, surname=surname)
            employees = [{'name': res['m']['name'], 'surname': res['m']
                        ['surname'], 'position': res['m']['position']} for res in results]
            query2 = f"""MATCH (a:Employee),(b:Department) WHERE a.name = '{employees[0]['name']}' AND a.surname = '{employees[0]['surname']}' AND b.name = '{res[0]['d']['name']}' CREATE (a)-[r:MANAGES]->(b) RETURN type(r)"""
            tx.run(query2)
        return {'name': name, 'surname': surname}


@empl.route('/employees/<string:person>', methods=['DELETE'])
def deleteEmployeeRoute(person):
    person1 = re.split('(?<=.)(?=[A-Z])', person)
    name = person1[0]
    surname = person1[1]
    with driver.session() as session:
        employee = session.execute_write(deleteEmployee, name, surname)

    if not employee:
        response = {'message': 'Employee not found'}
        return jsonify(response), 404
    else:
        res = {'status': 'success'}
        return jsonify(res)

#///////////////////////////////////////////////////////

#7.//////////////////////////////////////////////////////

def getEmployeeSubordinates(tx, name: str, surname: str):
    query = f"""MATCH (p:Employee), (p1:Employee {{name:'{name}', surname:'{surname}'}})-[r]-(d)
               WHERE NOT (p)-[:MANAGES]-(:Department)
               AND (p)-[:WORKS_IN]-(:Department {{name:d.name}})
               RETURN p"""
    results = tx.run(query).data()
    employees = [{'name': result['p']['name'],
               'surname': result['p']['surname']} for result in results[:len(results)//2]]
    return employees


@empl.route('/employees/<person>/subordinates', methods=['GET'])
def getEmployeeSubordinatesRoute(person):
    person1 = re.split('(?<=.)(?=[A-Z])', person)
    name = person1[0]
    surname = person1[1]
    with driver.session() as session:
        employees = session.read_transaction(
            get_employee_subordinates, name, surname)
    res = {'employees': employees}
    return jsonify(res)


#///////////////////////////////////////////////////////

#8.//////////////////////////////////////////////////////

def getDepartmentsFromEmployees(tx, name: str, surname: str):
    query = f"""MATCH 
               (m:Employee {{name:'{name}', surname:'{surname}'}})-[r:WORKS_IN]-(d:Department), 
               (m1:Employee)-[r1:MANAGES]-(d1:Department {{name:d.name}}),
               (m2:Employee)-[r2:WORKS_IN]-(d2:Department {{name:d.name}}) 
               RETURN d.name AS name, m1.name AS Manager, count(m2) AS Number_of_Employees"""
    result = tx.run(query).data()
    departments = [{'Name': result[0]['name'], 'Manager': result[0]
                    ['Manager'], 'Number of employees':result[0]['Number_of_Employees']+1}]
    return departments


@empl.route('/employees/<string:person>/department', methods=['GET'])
def get_departments_route_from_employee(person):
    person1 = re.split('(?<=.)(?=[A-Z])', person)
    name = person1[0]
    surname = person1[1]
    with driver.session() as session:
        departments = session.read_transaction(
            getDepartmentsFromEmployees, name, surname)
    res = {'department': departments}
    return jsonify(res)


#////////////////////////////////////////////////////////

#9.//////////////////////////////////////////////////////

def getDepartments(tx, sort: str = '', sortType: str = '', filter: str = '', filterType: str = ''):
    query = "MATCH (m:Department) RETURN m"
    if (sortType == 'asc'):
        if (sort == 'name'):
            query = "MATCH (m:Department) RETURN m ORDER BY m.name"
        if (sort == 'numberOfEmployees'):
            query = f"""MATCH 
               (m:Employee)-[r:WORKS_IN]-(d:Department)
               RETURN d.name ORDER BY count(m)"""
    if (sortType == 'desc'):
        if (sort == 'name'):
            query = "MATCH (m:Department) RETURN m ORDER BY m.name DESC"
        if (sort == 'numberOfEmployees'):
            query = f"""MATCH 
               (m:Employee)-[r:WORKS_IN]-(d:Department)
               RETURN d.name ORDER BY count(m) DESC"""
    if (filterType == 'name'):
        query = f"MATCH (m:Department) WHERE m.name CONTAINS '{filtr}' RETURN m"
    if (filterType == 'numberOfEmployees'):
        query = f"""MATCH 
               (m:Employee)-[r:WORKS_IN]-(d:Department)
               WHERE count(m) = '{filter}'               
               RETURN d.name"""
    results = tx.run(query).data()
    departments = [{'name': result['m']['name']} for result in results]
    return departments


@departments.route('/departments', methods=['GET'])
def get_departments_route():
    with driver.session() as session:
        departments = session.read_transaction(getDepartments)
    res = {'departments': departments}
    return jsonify(res)

#//////////////////////////////////////////////////////////

#10.//////////////////////////////////////////////////////////

def getDepartmentsEmployees(tx, name: str):
    query = f"MATCH (m:Employee)-[r:WORKS_IN]-(d:Department {{name:'{name}'}}) RETURN m"
    results = tx.run(query).data()
    employees = [{'name': result['m']['name'], 'surname': result['m']
                ['surname'], 'position': result['m']['position']} for result in results]
    return employees


@departments.route('/departments/<string:name>/employees', methods=['GET'])
def getDepartmentRouteFromDepartment(name: str):
    with driver.session() as session:
        employees = session.execute_read(getDepartmentsEmployees, name)
    res = {'employees': employees}
    return jsonify(res)

#//////////////////////////////////////////////////////////
app.register_blueprint(empl)


@app.route('/')
def test():
    return "all good"
    
if __name__ == '__main__':
    app.run()