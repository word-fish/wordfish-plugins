'''
neurosynth: plugin for the deepdive python package
functions for working with neurosynth database

'''

from neurosynth.base.dataset import Dataset
from neurosynth.base.dataset import FeatureTable
from wordfish.plugins.pubmed.functions import Pubmed
from neurosynth.base import mask
from neurosynth.base import imageutils
from neurosynth.analysis import meta
from neurosynth.analysis import decode
from wordfish.vm import download_repo
from wordfish.utils import untar
import nibabel as nb
from nibabel import nifti1
import pandas
import re
import os
import sys

# IMPORTS FOR ALL PLUGINS
from wordfish.corpus import save_sentences
from wordfish.terms import save_terms
from wordfish.terms import save_relationships

# REQUIRED WORDFISH PYTHON FUNCTIONS
def extract_text(output_dir,email="deepdive@stanford.edu"):

    f,d = download_data()
    features = pandas.read_csv(f,sep="\t")  
    database = pandas.read_csv(d,sep="\t")  

    pmids = database.id.unique().tolist()
    print "NeuroSynth database has %s unique PMIDs" %(len(pmids))

    # download abstract texts
    print "Downloading pubmed articles (this may take a while)"
    articles = []
    try:
        iters = numpy.ceil(len(pmids)/5000.0)
        start = 0
        for i in range(iters):
            if i == iters:
                end = len(pmids)
            else:
                end = iters*5000
            arts = get_articles(pmids[start:end])
            articles.update(arts)
    except URLError:
        print "URLError: There is a problem with your internet connection."
        sys.exit(32)

    # Prepare dictionary with key [pmid] and value [text]
    corpus_input = dict()
    for pmid,article in articles.iteritems():
        corpus_input[pmid] = article.getAbstract()

    # Save articles to text files in output folder     
    save_sentences(corpus_input,output_dir=output_dir)


def extract_terms(output_dir):
    features,database = download_data()
    terms = features.columns.tolist()
    terms.pop(0)  #pmid
    save_terms(terms,output_dir=output_dir)
    
def extract_relationships(output_dir):

    features,database = download_data()

    relationships = []
    print "Extracting NeuroSynth relationships..."
    dataset = Dataset(database)
    dataset.add_features(features)
    image_matrix = pandas.DataFrame(columns=range(228453))
    for t in range(len(terms)):
        term = terms[t]
        print "Parsing term %s, %s of %s" %(term,t,len(terms))
        ids = dataset.get_ids_by_features(term)
        maps = meta.MetaAnalysis(dataset,ids)
        # Let's use reverse inference, unthresholded Z score map
        image_matrix.loc[term] = maps.images["pFgA_z"]
    sims = image_matrix.corr(method="pearson")
    tuples = []
    ids = sims.index
    # This isn't tested yet
    for s1 in range(len(ids)):
        sim1 = ids[s1]
        for s2 in range(len(ids)):
            sim2 = ids[s2]
            if s2>s1:
                tuples.append((sim1,sim2,sims.loc[sim1,sim2]))
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
