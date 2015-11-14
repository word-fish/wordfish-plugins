'''
cattell: plugin for the wordfish python package
functions for converting Cattell's 282 traits into terms for wordfish python

'''
# WRITE YOUR IMPORTS HERE
from wordfish.utils import has_internet_connectivity, get_json

# IMPORTS FOR ALL PLUGINS
from wordfish.corpus import save_sentences
from wordfish.terms import save_terms
from wordfish.terms import save_relationships
from wordfish.plugin import generate_job

# REQUIRED WORDFISH FUNCTION
def go_fish():    
    generate_job(func="extract_terms",category="terms")
    generate_job(func="extract_relationships",category="terms")


# USER FUNCTIONS
def get_cattell():
    url = "https://raw.githubusercontent.com/vsoch/traits/master/data/json/cattell_personality_282.json"
    return get_json(url)

def get_terms(cattell):
    terms = dict()
    for term in cattell:
        unique_id = term["id"]
        name = term["trait"]
        if term["subtype_level1"] != None:
            name = term["subtype_level1"]
        if term["subtype_level2"] != None:
            name = term["subtype_level2"]
        terms[unique_id] = term
        terms[unique_id]["name"] = name
    return terms

def extract_terms(output_dir):

    cattell = get_cattell()
    terms = get_terms(cattell)
    save_terms(terms,output_dir=output_dir)

    
def extract_relationships(output_dir):

    cattell = get_cattell()
    terms = get_terms(cattell)
    tuples = []
    for term in cattell:
        unique_id = term["id"]
        opposite = (unique_id,term["opposite_id"],"opposite_of")
        tuples.append(opposite) 

    save_relationships(terms,output_dir=output_dir,relationships=tuples)

