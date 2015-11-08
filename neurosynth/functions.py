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

# REQUIRED DEEPDIVE PYTHON FUNCTIONS
def extract_text(email="deepdive@stanford.edu",output_dir):

    features,database = download_data()
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


def extract_terms(output_file,extract_relationships=False):
    features,database = download_data()
    terms = features.columns.tolist()
    if extract_relationships == True:
        #TODO: write meta analysis idea here with maps
    else:
        relationships=None
    save_terms(terms,output_dir=output_dir,relationships=relationships)


def download_data(destination=None,read=True):
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

    if read==True:
        features = pandas.read_csv(features,sep="\t")  
        database = pandas.read_csv(database,sep="\t")  
    
    return features,database




# NeuroSynth Functions--------------------------------------------------------------
# Not sure if I need these, might refactor
class NeuroSynth:

    def __init__(self,repo_path):
        """Initialize Neurosynth Database"""
        print "Initializing Neurosynth database..."
        self.db = Dataset('%s/database.txt' %(repo_path))
        self.db.add_features('%s/features.txt' %(repo_path))
        self.ids = self.getIDs()

    def getFeatures(self):
        """Return features in neurosynth database"""
        return self.db.get_feature_names()

    def getIDs(self):
        """Extract pubmed IDs or dois from Neurosynth Database"""
        # Get all IDs in neuroSynth
        return self.db.image_table.ids

    def getAuthor(self,db,id):   
        """Extract author names for a given pmid or doi"""
        article = self.db.get_mappables(id)
        meta = article[0].__dict__
        tmp = meta['data']['authors']
        tmp = tmp.split(",")
        authors = [ x.strip("^ ") for x in tmp]
        return authors

    def getAuthors(self,db):
        """Extract all author names in database"""
        articles = db.mappables
        uniqueAuthors = []
            for a in articles:
                meta = a.__dict__
                tmp = meta['data']['authors']
                tmp = tmp.split(",")
                authors = [ x.strip("^ ") for x in tmp]
                for a in authors:
                    uniqueAuthors.append(a)
                    uniqueAuthors = list(np.unique(uniqueAuthors))
        return uniqueAuthors

    def getPaperMeta(self,db,pmid):
        """Extract activation points and all meta information for a particular pmid"""
        articles = db.mappables
        m = []
        for a in articles:
            tmp = a.__dict__
            if tmp['data']['id'] == str(pmid):
                journal = tmp['data']['journal']
                title = tmp['data']['title']
                year = tmp['data']['year']
                doi = tmp['data']['doi']
                auth = tmp['data']['authors']
                peaks = tmp['data']['peaks']
                pmid = tmp['data']['id']
                tmp = (journal,title,year,doi,pmid,auth,peaks)
                m.append(tmp)
        return m
