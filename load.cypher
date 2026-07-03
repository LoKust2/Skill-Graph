LOAD CSV WITH HEADERS
FROM 'file:///SkillNodes.csv' AS row
MERGE (s:Skill {id: row.id})
ON CREATE SET s.name = row.name
ON MATCH SET s.name = row.name;

LOAD CSV WITH HEADERS
FROM 'file:///SubskillEdges.csv' AS row
MATCH (a:Skill {id: row.START_ID})
MATCH (b:Skill {id: row.END_ID})
MERGE (a)-[:IS_A_SUBSKILL_OF]->(b);

LOAD CSV WITH HEADERS
FROM 'file:///ComplimentEdges.csv' AS row
MATCH (a:Skill {id: row.START_ID})
MATCH (b:Skill {id: row.END_ID})
MERGE (a)-[r:COMPLIMENT]->(b)
SET r.weight = toInteger(row.count);