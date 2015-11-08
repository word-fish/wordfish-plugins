'''
reddit
plugin for wordfish python to get corpus from reddit

'''

from wordfish.utils import has_internet_connectivity
import praw
import os

# REQUIRED FUNCTIONS FOR ALL WORDFISH PLUGINS
from wordfish.corpus import save_sentences
from wordfish.terms import save_terms
from wordfish.terms import save_relationships

# Reddit might have some terms of interest, maybe top boards?
def extract_terms():
    return None

def extract_text(output_dir,boards=None):
    '''extract_corpus
    main function for parsing reddit boards into deepdive input corpus
    Parameters
    ==========
    boards: list
        list of reddit boards to parse
    '''
    if boards == None:
        # let's do some neurological disorders!
        boards = ["depression","anxiety","stress","OCD","panic","phobia","PTSD",
             "EatingDisorders","autism","amnesia","Alzheimers","BipolarReddit",
             "schizophrenia","narcissism","narcolepsy","Drug_Addiction","relationships",
             "gaming","worldnews","politics","movies","science","atheism","Showerthoughts",
             "cringe","rage","niceguys","sex","loseit","raisedbynarcissists","BPD",
             "AvPD","DID","SPD","EOOD","CompulsiveSkinPicking","psychoticreddit","insomnia"]

    if has_internet_connectivity():
        r = praw.Reddit(user_agent='wordfish')

        for board in boards:
            print "Parsing %s" %board
            submissions = r.get_subreddit(disorder).get_hot(limit=1000)
            now = time.localtime()
            content = []
            ids = []
            scores = []
        for sub in submissions:
            try:
                if len(sub.selftext) > 0:
                    if sub.fullname not in ids:
                        content.append(sub.selftext)
                        ids.append(sub.fullname)
                        scores.append(sub.score)
                        if sub.num_comments > 0:
                            comments = sub.comments
                            while len(comments) > 0:
                                for comment in comments:
                                    current = comments.pop(0)
                                    if isinstance(current,praw.objects.MoreComments):
                                        comments = comments + current.comments()
                                    else:               
                                        if len(current.body)>0:     
                                            content.append(current.body)
                                            ids.append(current.fullname)
                                            scores.append(current.score)
            except:
                print "Skipping %s" %sub.fullname

        print "%s has %s entities" %(disorder,len(content))
        # For each result, package into the right format for text parsing
        corpus_input = dict()
        count = 0
        last_disorder = disorder[0]
        for c in range(len(content)):
            current_disorder = disorder[c]
            if last_disorder == current_disorder:
                count = count + 1
            else:
                count = 1
            uid = "%s_%s" %(current_disorder,count)
            corpus_input[uid] = content[c]

        # Save articles to text files in output folder     
        save_sentences(corpus_input,output_dir=output_dir)


def extract_terms(output_dir,extract_relationships=False):
    print "Term extraction is not currently defined for the reddit plugin."
    
def extract_relationships(output_dir):
    print "Relationship extraction is not currently defined for the reddit plugin."
