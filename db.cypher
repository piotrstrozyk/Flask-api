CREATE (Sabrina:Employee {name:"Sabrina", surname: "Avila", position:"Regional Functionality Associate"})
CREATE (Caitlyn:Employee {name:"Caitlyn", surname: "Dotson", position:"Regional Functionality Associater"})
CREATE (Mahir:Employee {name:"Mahir", surname: "Bullock", position:"Regional Functionality Associater"})
CREATE (Rajan:Employee {name:"Rajan", surname: "Jacobs", position:"Regional Functionality Associater"})
CREATE (Deborah:Employee {name:"Deborah", surname: "Walls", position:"Dynamic Program Agent"})
CREATE (Priya:Employee {name:"Priyah", surname: "Larson", position:"Dynamic Program Agent"})
CREATE (Zaki:Employee {name:"Zaki", surname: "Warren", position:"Central Intranet Representative"})
CREATE (Nettie:Employee {name:"Nettie", surname: "Mueler", position:"Central Intranet Representative"})
CREATE (Leroy:Employee {name:"Leroy", surname: "Jenkins", position:"Central Intranet Representative"})
CREATE (Aidan:Employee {name:"Aidan", surname: "Mills", position:"Central Intranet Representative"})
CREATE (Roger:Employee {name:"Roger", surname: "Huber", position:"Interactive Tactics Producer"})
CREATE (Safia:Employee {name:"Safia", surname: "Colon", position:"Investor Interactions Officer"})

CREATE (IT:Department {name:"IT"})
CREATE (BD:Department {name:"Business Development"})
CREATE (HR:Department {name:"HR"})
CREATE (L:Department {name:"Legal"})

MATCH
  (a:Employee),
  (b:Department)
WHERE a.name = 'Sabrina' AND b.name = 'Business Development'
CREATE (a)-[r:WORKS_IN]->(b)
RETURN type(r)

MATCH
  (a:Employee),
  (b:Department)
WHERE a.name = 'Caitlyn' AND b.name = 'Business Development'
CREATE (a)-[r:WORKS_IN]->(b)<-[:MANAGES]-(a)
RETURN type(r)

MATCH
  (a:Employee),
  (b:Department)
WHERE a.name = 'Mahir' AND b.name = 'Business Development'
CREATE (a)-[r:WORKS_IN]->(b)
RETURN type(r)

MATCH
  (a:Employee),
  (b:Department)
WHERE a.name = 'Rajan' AND b.name = 'Business Development'
CREATE (a)-[r:WORKS_IN]->(b)<-[:MANAGES]-(a)
RETURN type(r)

MATCH
  (a:Employee),
  (b:Department)
WHERE a.name = 'Deborah' AND b.name = 'HR'
CREATE (a)-[r:WORKS_IN]->(b)
RETURN type(r)

MATCH
  (a:Employee),
  (b:Department)
WHERE a.name = 'Priyah' AND b.name = 'HR'
CREATE (a)-[r:WORKS_IN]->(b)<-[:MANAGES]-(a)
RETURN type(r)

MATCH
  (a:Employee),
  (b:Department)
WHERE a.name = 'Zaki' AND b.name = 'IT'
CREATE (a)-[r:WORKS_IN]->(b)<-[:MANAGES]-(a)
RETURN type(r)

MATCH
  (a:Employee),
  (b:Department)
WHERE a.name = 'Nettie' AND b.name = 'IT'
CREATE (a)-[r:WORKS_IN]->(b)
RETURN type(r)

MATCH
  (a:Employee),
  (b:Department)
WHERE a.name = 'Leroy' AND b.name = 'IT'
CREATE (a)-[r:WORKS_IN]->(b)<-[:MANAGES]-(a)
RETURN type(r)

MATCH
  (a:Employee),
  (b:Department)
WHERE a.name = 'Aidan' AND b.name = 'IT'
CREATE (a)-[r:WORKS_IN]->(b)
RETURN type(r)

MATCH
  (a:Employee),
  (b:Department)
WHERE a.name = 'Roger' AND b.name = 'Legal'
CREATE (a)-[r:WORKS_IN]->(b)
RETURN type(r)

MATCH
  (a:Employee),
  (b:Department),
  (c:Department)
WHERE a.name = 'Aidan' AND b.name = 'Legal' AND c.name = 'IT'
CREATE (a)-[r:WORKS_IN]->(b)<-[:MANAGES]-(a)-[:SUPERVISES]->(c)
RETURN type(r)

