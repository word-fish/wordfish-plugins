'''
fma_nif: plugin for the wordfish python package
functions for extracting brain regions and relationships from the FMA NIF ontology

'''
# WRITE YOUR CUSTOM IMPORTS HERE
from wordfish.utils import get_json, has_internet_connectivity

# IMPORTS FOR ALL PLUGINS
from wordfish.corpus import save_sentences
from wordfish.terms import save_terms
from wordfish.terms import save_relationships

# REQUIRED WORDNET PYTHON FUNCTIONS
def extract_text(output_dir):
    print "Text corpus extraction is not defined for the fma-nif plugin."


def extract_terms(output_dir):

    if has_internet_connectivity():    
       terms = get_terms()
       save_terms(terms,output_dir=output_dir)

    else:
       print "Cannot define fma-nif region terms, no internet connectivity."

    
def extract_relationships(output_dir):

    if has_internet_connectivity(): 
       tuples = []
       terms = get_terms()   
       relations = get_nif_json()
       for relation in relations["edges"]:
           tup = (relation["obj"],relation["sub"],relation["pred"])
           tuples.append(tup)

       save_relationships(terms,output_dir=output_dir,relationships=tuples)
    else:
       print "Cannot define fma-nif relationships, no internet connectivity."


def get_terms():
   terms = dict()
   regions = get_nif_json()
   for region in regions["nodes"]:
       prefLabel = region["lbl"]
       unique_id = region["id"]
       terms[unique_id] = region
       terms[unique_id]["name"] = prefLabel
   return terms

def get_nif_json():
    return get_json("http://matrix.neuinfo.org:9000/scigraph/graph/neighbors/NIFGA:birnlex_796?relationshipType=http://www.obofoundry.org/ro/ro.owl%23has_proper_part&direction=OUTGOING&depth=9")
