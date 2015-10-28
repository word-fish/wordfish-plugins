'''

pubmed: 
part of the deepdive python package: parsing of term data structures into formats for deepdive
this set of functions is for parsing pubmed data

'''

import os
import re
import sys
import nltk
import json
import pandas
import urllib
import string
import urllib2
import numpy as np
from Bio import Entrez
from deepdive.nlp import do_stem

# Pubmed
class Pubmed:
    '''Pubmed: 
       class for storing a pubmed object with email credential,
       and optionally a pubmed central lookup table. 
    '''
    def __init__(self,pmc=True):
        if pmc:
            self.get_pmc_lookup()

    def get_pmc_lookup(self):
        print "Downloading latest version of pubmed central ftp lookup..."
        self.ftp = pandas.read_csv("ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/file_list.txt",skiprows=1,sep="\t",header=None)
        self.ftp.columns = ["URL","JOURNAL","PMCID","PMID"]

    def get_pubmed_central_ids(self):
        return list(self.ftp["PMCID"])

def get_ftp():
    '''get_ftp
    download ftp object from pubmed
    '''
    return pmc = Pubmed(email=email).ftp


# Download pubmed without relying on pubmed object
def download_pubmed(pmids,download_folder,ftp=None):
    """download_pubmed
    Download full text of articles with pubmed ids pmids to folder
        pmids: 
            list of pubmed ids to download
        download_folder: 
            destination folder
        ftp: 
            pandas data frame of pubmed ftp. If not provided,
            will be obtained and read programatically. If this function is
            being run in a cluster environment, it is recommended to save
            this ftp object, and read in from file for the function.
    """

    # If no ftp object is provided, retrieve it
    if ftp == None:
        ftp = get_ftp()

    if isinstance(pmids,str):
        pmids = [pmids]
    
    subset = pandas.DataFrame(columns=ftp.columns)
    for p in pmids:
        row = ftp.loc[ftp.index[ftp.PMCID == p]]
        subset = subset.append(row)
    
    # Now for each, assemble the URL
    for row in subset.iterrows():
        url = "ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/%s" % (row[1]["URL"])
        download_place = "%s/" %(download_folder)
        basename = os.path.basename(row[1]["URL"])
        if not os.path.isfile("%s/%s" %(download_folder,basename)):
            print "Downloading %s" % (url)       
            os.system("wget \"%s\" -P %s" % (url,download_place))


def check_download(pmid,download_folder,ftp=None):
    """check_download
    check if file downloaded
    """
    if ftp == None:
        ftp = get_ftp()

    article = ftp.loc[ftp.index[ftp.PMCID == pmid]]
    article = os.path.basename(article["URL"].tolist()[0])
    article = "%s/%s" %(download_folder,article)
    return os.path.exists(article)


def get_articles(ids,email):
    """get_single_article
    Read and return single article (or search term) pubmed

    id1
    """
    if isinstance(ids,str):
        ids = [ids]

    Entrez.email = email

    pmids = []
    for id1 in ids:
        handle = Entrez.esearch(db='pubmed',term=id1,retmax=1)
        record = Entrez.read(handle)
        # If we have a match
        if "IdList" in record:
            if record["Count"] != "0":
                pmids.append(record["IdList"][0])

    if len(pmids) > 0:
        # Retrieve them all!
        print "Retrieving %s papers..." % (len(pmids))
        handle = Entrez.efetch(db='pubmed', id=pmids,retmode='xml')
        records = Entrez.read(handle)
        articles = dict()
        for record in records:
             articles[str(record["MedlineCitation"]["PMID"])] = Article(record)
        return articles
    else:
        print "No articles found."


def search_abstract(article,terms,stem=False):
    '''search_article
    Search article for one or more terms of interest - no processing of expression. return 1 if found, 0 if not

    article: Article 
        an Article object
    terms: str/list
        a list of terms to be compiled with re
    stem: boolean
        if True, stem article words first
    '''
    text = [article.getAbstract()] + article.getMesh() + article.getKeywords()
    text = text[0].lower()

    # Perform stemming of terms    
    if stem:
        words = do_stem(terms,return_unique=True)

    term = "|".join([x.strip(" ").lower() for x in words])
    expression = re.compile(term)
    # Search abstract for terms, return 1 if found
    found = expression.search(text)
    if found:
        return 1
    return 0
    



def search_articles(searchterm,email):
    '''search_articles
    Return list of articles based on search term
    Parameters
    ==========
    searchterm: str
       a search term to search for
    Returns
    =======
    articles: Article objects
        a list of articles that match search term
    '''
    print "Getting pubmed articles for search term %s" %(searchterm)

    Entrez.email = email
    handle = Entrez.esearch(db='pubmed',term=searchterm,retmax=5000)
    record = Entrez.read(handle)

    # If there are papers
    if "IdList" in record:
        if record["Count"] != "0":
            # Fetch the papers
            ids = record['IdList']
            handle = Entrez.efetch(db='pubmed', id=ids,retmode='xml',retmax=5000)
            return Entrez.read(handle)

    # If there are no papers
    else:
        print "No papers found for searchterm %s!" %(searchterm)


# ARTICLE ------------------------------------------------------------------------------
class Article:
    '''An articles object holds a pubmed article'''
    def __init__(self,record):
        self.parseRecord(record)

    def parseRecord(self,record):
        if "MedlineCitation" in record:
            self.authors = record["MedlineCitation"]["Article"]["AuthorList"]
        if "MeshHeadingList" in record:
            self.mesh = record["MedlineCitation"]["MeshHeadingList"]
        else:
            self.mesh = []
        self.keywords = record["MedlineCitation"]["KeywordList"]
        self.medline = record["MedlineCitation"]["MedlineJournalInfo"]
        self.journal = record["MedlineCitation"]["Article"]["Journal"]
        self.title = record["MedlineCitation"]["Article"]["ArticleTitle"]
        self.year = record["MedlineCitation"]["Article"]["ArticleTitle"]
        if "Abstract" in record["MedlineCitation"]["Article"]:
            self.abstract = record["MedlineCitation"]["Article"]["Abstract"]
        else:
            self.abstract = ""
        self.ids = record["PubmedData"]["ArticleIdList"]

    """get Abstract text"""
    def getAbstract(self):
        if "AbstractText" in self.abstract:
            return self.abstract["AbstractText"][0]
        else:
            return ""

    """get mesh terms"""
    def getMesh(self):
        return [ str(x["DescriptorName"]).lower() for x in self.mesh]

    """get keywords"""
    def getKeywords(self):
        return self.keywords
