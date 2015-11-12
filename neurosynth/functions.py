'''
neurosynth: plugin for the deepdive python package
functions for working with neurosynth database

'''

from neurosynth.base.dataset import Dataset
from neurosynth.base.dataset import FeatureTable
from wordfish.plugins.pubmed.functions import get_articles
from neurosynth.analysis import meta
from scipy.stats import pearsonr
from wordfish.vm import download_repo
from wordfish.utils import untar
import nibabel as nb
from nibabel import nifti1
import pandas
import numpy
import urllib2
import re
import os
import sys

# IMPORTS FOR ALL PLUGINS
from wordfish.corpus import save_sentences
from wordfish.terms import save_terms
from wordfish.terms import save_relationships

# REQUIRED WORDFISH PYTHON FUNCTIONS
def extract_text(output_dir,email="wordfish@stanford.edu"):

    f,d = download_data()
    features = pandas.read_csv(f,sep="\t")  
    database = pandas.read_csv(d,sep="\t")  

    pmids = database.id.unique().tolist()
    print "NeuroSynth database has %s unique PMIDs" %(len(pmids))

    # download abstract texts
    print "Downloading pubmed articles (this may take a while)"
    articles = dict()
    try:
        iters = int(numpy.ceil(len(pmids)/5000.0))
        start = 0
        for i in range(iters):
            if i == iters:
                end = len(pmids)
            else:
                end = iters*5000
            arts = get_articles(pmids[start:end],email)
            articles.update(arts)
    except urllib2.URLError, e:
        print "URLError: %e, There is a problem with your internet connection." %(e)

    # Prepare dictionary with key [pmid] and value [text]
    features.index = features.pmid
    features = features.drop("pmid",axis=1)
    corpus_input = dict()
    for pmid,article in articles.iteritems():
        # Label the article with nonzero values
        labels = features.columns[features.loc[pmid]!=0].tolist()     
        corpus_input[pmid] = {"text":article.getAbstract(),"labels":labels}

    # Save articles to text files in output folder     
    save_sentences(corpus_input,output_dir=output_dir)

def extract_terms(output_dir):
    f,d = download_data()
    features = pandas.read_csv(f,sep="\t")  
    terms = features.columns.tolist()
    terms.pop(0)  #pmid
    save_terms(terms,output_dir)
    

def extract_relationships(output_dir):

    f,d = download_data()
    features = pandas.read_csv(f,sep="\t")  
    database = pandas.read_csv(d,sep="\t")  
    terms = features.columns.tolist()
    terms.pop(0)  #pmid

    relationships = []
    print "Extracting NeuroSynth relationships..."
    dataset = Dataset(d)
    dataset.add_features(f)
    image_matrix = pandas.DataFrame(columns=range(228453))
    for t in range(len(terms)):
        term = terms[t]
        print "Parsing term %s, %s of %s" %(term,t,len(terms))
        ids = dataset.get_ids_by_features(term)
        maps = meta.MetaAnalysis(dataset,ids)
        # Let's use reverse inference, unthresholded Z score map
        image_matrix.loc[term] = maps.images["pFgA_z"]

    sims = pandas.DataFrame(columns=image_matrix.index)
    tuples = []
    for t1 in range(image_matrix.index):
        term1 = image_matrix.index[t1]
        for t2 in range(image_matrix.index):
            term2 = image_matrix.index[t2]
            if t1<t2:
                score = pearsonr(image_matrix.loc[term1],image_matrix.loc[term2])[0]
                tuples.append((term1,term2,score))

    save_relationships(terms,output_dir=output_dir,relationships=tuples)


def download_data(destination=None):
    '''download_data
    download neurosynth repo data to a temporary or specified destination
    return path to features and database files
    Parameters
    ==========
    destination: path
        full path to download destination. If none, will use temporary directory
    Returns
    =======
    database,features: paths
        full paths to database and features files  
    '''
    print "Downloading neurosynth database..."

    if destination==None:
        destination = download_repo(repo_url="https://github.com/neurosynth/neurosynth-data")
    else:
        download_repo(repo_url="https://github.com/neurosynth/neurosynth-data",tmpdir=destination)
    untar("%s/current_data.tar.gz" %(destination),destination)
    
    features = "%s/features.txt" %(destination)
    database = "%s/database.txt" %(destination)
    
    return features,database
