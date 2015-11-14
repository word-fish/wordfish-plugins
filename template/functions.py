'''
[tag]: plugin for the wordfish python package
functions for working [description]

'''
# WRITE YOUR IMPORTS HERE


# IMPORTS FOR ALL PLUGINS
from wordfish.corpus import save_sentences
from wordfish.terms import save_terms
from wordfish.terms import save_relationships
from wordfish.plugin import generate_job

# REQUIRED WORDFISH FUNCTION
def go_fish():

    # jobs to download abstract texts
    generate_job(func="extract_text",category="corpus",inputs={"uids",uids},batch_num=100)
    generate_job(func="extract_terms",category="terms")
    generate_job(func="extract_relationships",category="terms")


# USER FUNCTIONS
def extract_text(uids,output_dir):

    # This function will be called by a job, and must call save_sentences
    # ** ALL USER FUNCTIONS MUST HAVE output_dir as an input

    # You can provide a dictionary if your items have ids
    corpus_input = {
                     "uid1":{"text":"One fish, two fish."},
                     "uid2":{"text":"Nerd fish, wordfish."},
                    }

    # If you have labels (to be used for classification
    corpus_input = {
                     "uid1":{"text":"One fish, two fish.","labels":["counting","poem"]},
                     "uid2":{"text":"Nerd fish, wordfish.","labels":["poem"]},
                    }

    # Or just give raw text in a list
    corpus_input =   ["This is text from article 1 with no id.",
                      "This is text from article 2 with no id."]


    # Save articles to individual text files in output folder     
    save_sentences(corpus_input,output_dir=output_dir)

def extract_terms(output_dir):

    # You can provide a dictionary if your terms have meta data
    # the key should be some unique ID for your term, and use numbers
    # if you do not have any. The "name" variable in the meta data should
    # correspoind to the term name
    terms = {"term_unique_id1":{"meta1":"meta_value1",
                                "meta2":"meta_value2",
                                "name":"term1"}}
    # Or a list if not
    terms = ["term1"]

    save_terms(terms,output_dir=home)


def extract_relationships(output_dir):

    # You should provide a list of tuples, with the
    # first and second items for each tuple corresponding
    # to term ids you specified in extract_terms
    tuples = [(source1,target1,value)]

    # Value can be a string or int
    # The terms variable is equivalent to the one needed for extract_terms
    save_relationships(terms,output_dir=output_dir,relationships=tuples)
