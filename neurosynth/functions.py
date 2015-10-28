'''
neurosynth: plugin for the deepdive python package
functions for working with neurosynth database

'''

from neurosynth.base.dataset import Dataset
from neurosynth.base.dataset import FeatureTable
from neurosynth.base import mask
from neurosynth.base import imageutils
from neurosynth.analysis import meta
from neurosynth.analysis import decode
from deepdive.vm import download_repo
import nibabel as nb
from nibabel import nifti1
import pandas
import re
import os
import sys

# REQUIRED DEEPDIVE PYTHON FUNCTIONS
def extract_text(email="deepdive@stanford.edu"):

    features,database = download_data()
    df = pandas.read_csv(database,sep="\t")
    pmids = df.id.unique().tolist()
    print "NeuroSynth database has %s unique PMIDs" %(len(pmids))

# download abstract text
email = "vsochat@stanford.edu"
pm = Pubmed(email,pmc=False)
articles1 = pm.get_many_articles(pmids[:10000])
articles2 = pm.get_many_articles(pmids[10000:])
articles = articles1.copy()
articles.update(articles2)

if not os.path.exists("articles.pkl"):
    pickle.dump(articles,open("articles.pkl","wb"))


def extract_terms():


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
    if destination==None:
        destination = download_repo(repo_url="https://github.com/neurosynth/neurosynth-data")
    else:
        download_repo(repo_url="https://github.com/neurosynth/neurosynth-data",destination=destination)
    os.system("tar -xzvf %s/current_data.tar.gz" %(destination))
    
    features = "%s/features.txt" %(destination)
    database = "%s/database.txt" %(destination)

    if read==True:
        features = pandas.read_csv(features,sep="\t")  
        database = pandas.read_csv(database,sep="\t")  
    
    return features,database


# NeuroSynth Functions--------------------------------------------------------------
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
