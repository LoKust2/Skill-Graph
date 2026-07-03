import os
import pandas as pd

# ============================================================
# Configuration
# ============================================================

INPUT_DIR = "input"
MIDDLEMAN_DIR = "middleman"
GRAPH_DIR = "graph"

os.makedirs(MIDDLEMAN_DIR, exist_ok=True)
os.makedirs(GRAPH_DIR, exist_ok=True)

ENTITY_FILE = os.path.join(INPUT_DIR, "entity_alignment_results.csv")
SUBSKILL_FILE = os.path.join(INPUT_DIR, "is_a_subskill_of.csv")
COMPLIMENT_FILE = os.path.join(INPUT_DIR, "compliment_edges.csv")

# ============================================================
# Read input files
# ============================================================

entities = pd.read_csv(ENTITY_FILE)
subskills = pd.read_csv(SUBSKILL_FILE)
compliments = pd.read_csv(COMPLIMENT_FILE)

# ============================================================
# Validate required columns
# ============================================================

entity_required = [
    "esco_uri",
    "esco_preferred_label"
]

subskill_required = [
    "child_uri",
    "child_label",
    "parent_uri",
    "parent_label"
]

compliment_required = [
    "skill1",
    "skill2"
]

for c in entity_required:
    if c not in entities.columns:
        raise Exception(f"Missing column: {c}")

for c in subskill_required:
    if c not in subskills.columns:
        raise Exception(f"Missing column: {c}")

for c in compliment_required:
    if c not in compliments.columns:
        raise Exception(f"Missing column: {c}")

# ============================================================
# Clean data
# ============================================================

entities = entities.drop_duplicates()
subskills = subskills.drop_duplicates()
compliments = compliments.drop_duplicates()

entities = entities.fillna("")
subskills = subskills.fillna("")
compliments = compliments.fillna("")

# ============================================================
# Export Middleman CSVs
# ============================================================

entities.to_csv(
    os.path.join(MIDDLEMAN_DIR, "cleaned_entities.csv"),
    index=False
)

subskills.to_csv(
    os.path.join(MIDDLEMAN_DIR, "cleaned_subskills.csv"),
    index=False
)

compliments.to_csv(
    os.path.join(MIDDLEMAN_DIR, "cleaned_compliments.csv"),
    index=False
)

print("Middleman CSVs exported.")

# ============================================================
# Build Skill Nodes
# ============================================================

entity_nodes = entities[
    ["esco_uri", "esco_preferred_label"]
].rename(columns={
    "esco_uri": "id",
    "esco_preferred_label": "name"
})

child_nodes = subskills[
    ["child_uri", "child_label"]
].rename(columns={
    "child_uri": "id",
    "child_label": "name"
})

parent_nodes = subskills[
    ["parent_uri", "parent_label"]
].rename(columns={
    "parent_uri": "id",
    "parent_label": "name"
})

skill_nodes = pd.concat(
    [
        entity_nodes,
        child_nodes,
        parent_nodes
    ],
    ignore_index=True
)

skill_nodes = skill_nodes.drop_duplicates()

skill_nodes["label"] = "Skill"

# ============================================================
# Handle unknown skills
# ============================================================

if skill_nodes["id"].eq("").any():

    skill_nodes.loc[
        skill_nodes["id"] == "",
        "id"
    ] = "UNCLASSIFIED"

    skill_nodes.loc[
        skill_nodes["name"] == "",
        "name"
    ] = "Unclassified_Skill"

if "UNCLASSIFIED" not in skill_nodes["id"].values:

    skill_nodes.loc[len(skill_nodes)] = [
        "UNCLASSIFIED",
        "Unclassified_Skill",
        "Skill"
    ]

skill_nodes.to_csv(
    os.path.join(GRAPH_DIR, "SkillNodes.csv"),
    index=False
)

print("SkillNodes.csv exported.")

# ============================================================
# Create lookup table
# ============================================================

lookup = dict(
    zip(
        skill_nodes["name"],
        skill_nodes["id"]
    )
)

# ============================================================
# Build IS_A_SUBSKILL_OF edges
# ============================================================

subskill_edges = subskills.rename(columns={
    "child_uri": "START_ID",
    "parent_uri": "END_ID"
})

subskill_edges["TYPE"] = "IS_A_SUBSKILL_OF"

subskill_edges = subskill_edges[
    [
        "START_ID",
        "END_ID",
        "TYPE"
    ]
]

subskill_edges.to_csv(
    os.path.join(GRAPH_DIR, "SubskillEdges.csv"),
    index=False
)

print("SubskillEdges.csv exported.")

# ============================================================
# Build COMPLIMENT edges
# ============================================================

compliments["START_ID"] = compliments["skill1"].map(lookup)
compliments["END_ID"] = compliments["skill2"].map(lookup)

compliments["START_ID"] = compliments["START_ID"].fillna("UNCLASSIFIED")
compliments["END_ID"] = compliments["END_ID"].fillna("UNCLASSIFIED")

compliments["TYPE"] = "COMPLIMENT"

if "count" not in compliments.columns:
    compliments["count"] = 1

compliment_edges = compliments[
    [
        "START_ID",
        "END_ID",
        "TYPE",
        "count"
    ]
]

compliment_edges.to_csv(
    os.path.join(GRAPH_DIR, "ComplimentEdges.csv"),
    index=False
)

print("ComplimentEdges.csv exported.")

print()
print("=======================================")
print("ETL COMPLETE")
print("=======================================")
print("Middleman folder:")
print("  cleaned_entities.csv")
print("  cleaned_subskills.csv")
print("  cleaned_compliments.csv")
print()
print("Graph folder:")
print("  SkillNodes.csv")
print("  SubskillEdges.csv")
print("  ComplimentEdges.csv")