'''
cnp: plugin for the wordfish python package
functions for importing questions from CNP database

'''
# WRITE YOUR IMPORTS HERE
import pandas
import os

# IMPORTS FOR ALL PLUGINS
from wordfish.corpus import save_sentences
from wordfish.terms import save_terms
from wordfish.terms import save_relations
from wordfish.plugin import generate_job

# REQUIRED WORDNET FUNCTIONS
def go_fish():    
    generate_job(func="extract_text",category="corpus")

# USER FUNCTION
def extract_text(output_dir):

    corpus_input = {}
    plugin_directory = os.path.abspath(os.path.dirname(__file__))
    questions = pandas.read_csv("%s/cnp_739.tsv" %(plugin_directory),sep="\t")
    for question in questions.iterrows():
        corpus_input[question[1].question_label] = { "text":question[1].question_text }

    # Save articles to text files in output folder     
    save_sentences(corpus_input,output_dir=output_dir)
