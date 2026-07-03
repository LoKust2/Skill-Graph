CREATE CONSTRAINT skill_id IF NOT EXISTS
FOR (s:Skill)
REQUIRE s.id IS UNIQUE;

CREATE INDEX skill_name IF NOT EXISTS
FOR (s:Skill)
ON (s.name);