'''
[tag]: plugin for the wordfish python package
functions for working [description]

'''
# WRITE YOUR IMPORTS HERE


# IMPORTS FOR ALL PLUGINS
from wordfish.corpus import save_sentences
from wordfish.terms import save_terms
from wordfish.terms import save_relationships

# REQUIRED WORDNET PYTHON FUNCTIONS
def extract_text(output_dir):

    # You can provide a dictionary if your items have ids
    corpus_input = {
                    "unique_id_1","bla bla bla 1",
                    "unique_id_1","bla bla bla 2"
                    }

    # Or a list if not
    corput_input = ["bla bla bla 1","bla bla bla 2"]

    # Save articles to text files in output folder     
    save_sentences(corpus_input,output_dir=output_dir)


def extract_terms(output_dir,extract_relationships=False):

    # You can provide a dictionary if your terms have meta data
    # the key should be some unique ID for your term, and use numbers
    # if you do not have any. The "name" variable in the meta data should
    # correspoind to the term name
    terms = {"term_unique_id1":{"meta1":"meta_value1",
                                "meta2":"meta_value2",
                                "name":"term1"}}
    # Or a list if not
    terms = ["term1"]

    save_terms(terms,output_dir=output_dir)
    
def extract_relationships(output_dir):

    # You should provide a list of tuples, with the
    # first and second items for each tuple corresponding
    # to term ids you specified in extract_terms
    tuples = [(source1,target1,value)]

    # Value can be a string or int
    # The terms variable is equivalent to the one needed for extract_terms
    save_relationships(terms,output_dir=output_dir,relationships=tuples)

