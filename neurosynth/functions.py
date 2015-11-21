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
from nibabel import nifti1
import nibabel as nb
import urllib2
import pandas
import pickle
import numpy
import re
import os
import sys

# IMPORTS FOR ALL PLUGINS
from wordfish.corpus import save_sentences
from wordfish.terms import save_terms
from wordfish.terms import save_relations
from wordfish.plugin import generate_job
from wordfish.utils import wordfish_home

home = wordfish_home()

# REQUIRED WORDFISH FUNCTION
def go_fish():

    f,d = download_data()
    features = pandas.read_csv(f,sep="\t")  
    database = pandas.read_csv(d,sep="\t")  
    pmids = database.id.unique().tolist()
    print "NeuroSynth database has %s unique PMIDs" %(len(pmids))

    # Generate brain maps to extract relationships with
    terms = features.columns.tolist()
    terms.pop(0)  #pmid
    
    maps_dir = "%s/terms/neurosynth/maps" %(home)
    if not os.path.exists(maps_dir):
        os.mkdir(maps_dir)

    # jobs to download abstract texts
    generate_job(func="generate_maps",inputs={"terms":terms},category="terms",batch_num=100)
    generate_job(func="extract_text",category="corpus",inputs={"pmids":pmids},batch_num=100)
    generate_job(func="extract_terms",category="terms")
    generate_job(func="extract_relations",inputs={"terms":terms,"maps_dir":maps_dir},category="relations",batch_num=100)

# USER FUNCTIONS
def extract_text(pmids,output_dir):

    email="wordfish@stanford.edu"
    print "Downloading %s pubmed articles!" %(len(pmids))
    try:
        articles = get_articles(pmids,email)
    except urllib2.URLError, e:
        print "URLError: %e, There is a problem with your internet connection." %(e)

    f,d = download_data()
    features = pandas.read_csv(f,sep="\t")  

    # Prepare dictionary with key [pmid] and value [text]
    features.index = features.pmid
    features = features.drop("pmid",axis=1)
    corpus_input = dict()
    for pmid,article in articles.iteritems():
        # Label the article with nonzero values
        try:
            labels = features.columns[features.loc[int(pmid)]!=0].tolist()     
            corpus_input[pmid] = {"text":article.getAbstract(),"labels":labels}
        except:
            pass

    # Save articles to text files in output folder     
    save_sentences(corpus_input,output_dir=output_dir)

def extract_terms(output_dir):
    f,d = download_data()
    features = pandas.read_csv(f,sep="\t")  
    terms = features.columns.tolist()
    terms.pop(0)  #pmid
    save_terms(terms,output_dir)
    

def generate_maps(terms,output_dir):

    f,d = download_data()
    features = pandas.read_csv(f,sep="\t")  
    database = pandas.read_csv(d,sep="\t")  

    output_dir = "%s/maps" %(output_dir)

    print "Deriving pickled maps to extract relationships from..."
    dataset = Dataset(d)
    dataset.add_features(f)
    for t in range(len(terms)):
        term = terms[t]
        print "Generating P(term|activation) for term %s, %s of %s" %(term,t,len(terms))
        ids = dataset.get_ids_by_features(term)
        maps = meta.MetaAnalysis(dataset,ids)
        term_name = term.replace(" ","_")
        pickle.dump(maps.images["pFgA_z"],open("%s/%s_pFgA_z.pkl" %(output_dir,term_name),"wb"))


def extract_relations(terms,maps_dir,output_dir):

    if isinstance(terms,str):
        terms = [terms]

    f,d = download_data()
    features = pandas.read_csv(f,sep="\t")  
    database = pandas.read_csv(d,sep="\t")  
    allterms = features.columns.tolist()
    allterms.pop(0)  #pmid

    dataset = Dataset(d)
    dataset.add_features(f)
    image_matrix = pandas.DataFrame(columns=range(228453))
    for t in range(len(allterms)):
        term = allterms[t]
        term_name = term.replace(" ","_")
        pickled_map = "%s/%s_pFgA_z.pkl" %(maps_dir,term_name)
        if not os.path.exists(pickled_map):
            print "Generating P(term|activation) for term %s" %(term)
            ids = dataset.get_ids_by_features(term)
            maps = meta.MetaAnalysis(dataset,ids)
            pickle.dump(maps.images["pFgA_z"],open(pickled_map,"wb"))
        map_data = pickle.load(open(pickled_map,"rb"))
        image_matrix.loc[term] = map_data

    sims = pandas.DataFrame(columns=image_matrix.index)
    tuples = []
    for t1 in range(len(terms)):
        term1 = terms[t1]
        print "Extracting NeuroSynth relationships for term %s..." %(term1)
        for t2 in range(len(terms)):
            term2 = terms[t2]
            if t1<t2:
                score = pearsonr(image_matrix.loc[term1],image_matrix.loc[term2])[0]
                tuples.append((term1,term2,score))

    save_relations(output_dir=output_dir,relations=tuples)

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

