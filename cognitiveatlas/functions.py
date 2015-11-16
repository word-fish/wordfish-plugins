'''
cognitiveatlas
plugin for wordnet python

'''
from cognitiveatlas.api import get_task, get_concept

# IMPORTS FOR ALL PLUGINS
from wordfish.corpus import save_sentences
from wordfish.terms import save_terms
from wordfish.terms import save_relations
from wordfish.plugin import generate_job

# REQUIRED WORDFISH FUNCTION
def go_fish():    
    generate_job(func="extract_terms",category="terms")
    generate_job(func="extract_relations",category="terms")


# USER FUNCTIONS
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

def extract_terms(output_dir):

    terms = get_terms()
    save_terms(terms,output_dir=output_dir)
    
def extract_relations(output_dir):

    tuples = []
    terms = get_terms()
    concepts = get_concepts()

    for concept in concepts:
        if "relationships" in concept:
            for relation in concept["relationships"]:   
                relationship = "%s,%s" %(relation["direction"],relation["relationship"])
                tup = (concept["id"],relation["id"],relationship) 
                tuples.append(tup)

    save_relations(terms,output_dir=output_dir,relationships=tuples)
