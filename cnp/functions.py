'''
[tag]: plugin for the wordfish python package
functions for working [description]

'''
# WRITE YOUR IMPORTS HERE
import pandas
import os

# IMPORTS FOR ALL PLUGINS
from wordfish.corpus import save_sentences
from wordfish.terms import save_terms
from wordfish.terms import save_relationships

# REQUIRED WORDNET PYTHON FUNCTIONS
def extract_text(output_dir):

    corpus_input = {}
    plugin_directory = os.path.abspath(os.path.dirname(__file__))
    questions = pandas.read_csv("%s/cnp_739.tsv" %(plugin_directory),sep="\t")
    for question in questions.iterrows():
        corpus_input[question[1].question_label] = question[1].question_text

    # Save articles to text files in output folder     
    save_sentences(corpus_input,output_dir=output_dir)

def extract_terms(output_dir):

    print "Terminology extraction is not defined for the CNP plugin."

    
def extract_relationships(output_dir):

    print "Relationship extraction is not defined for the CNP plugin."

