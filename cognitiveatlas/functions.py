'''
cognitiveatlas
plugin for wordnet python

'''
from cognitiveatlas.api import get_task, get_concept

# IMPORTS FOR ALL PLUGINS
from wordfish.corpus import save_sentences
from wordfish.terms import save_terms
from wordfish.terms import save_relationships

# REQUIRED WORDNET PYTHON FUNCTIONS
def extract_text(output_dir):
    return None


def get_concepts():
    return get_concept().json


def get_terms():
    terms = dict()
    concepts = get_concepts()

    for c in range(len(concepts)):
        concept_id = concepts[c]["id"]
        meta = {"name":concepts[c]["name"],
                "definition":concepts[c]["definition_text"]}
        terms[concept_id] = meta
    return terms

def extract_terms(output_dir,extract_relationships=False):

    terms = get_terms()
    save_terms(terms,output_dir=output_dir)
    
def extract_relationships(output_dir):

    tuples = []
    terms = get_terms()
    concepts = get_concepts()

    for concept in concepts:
        if "relationships" in concept:
            for relation in concept["relationships"]:   
                relationship = "%s,%s" %(relation["direction"],relation["relationship"]) 
                tuples.append[(concept["id"],relation["id"],relationship)]

    save_relationships(terms,output_dir=output_dir,relationships=tuples)
