'''
reddit
plugin for wordfish python to get corpus from reddit

'''

from wordfish.utils import has_internet_connectivity
import time
import praw
import os


# REQUIRED FUNCTIONS FOR ALL WORDFISH PLUGINS
from wordfish.corpus import save_sentences
from wordfish.terms import save_terms
from wordfish.terms import save_relationships
from wordfish.plugin import generate_job

# REQUIRED WORDFISH FUNCTION
def go_fish(boards=None):

    if boards == None:
        # let's do some neurological disorders!
        boards = ["depression","anxiety","stress","OCD","panic","phobia","PTSD",
             "EatingDisorders","autism","amnesia","Alzheimers","BipolarReddit",
             "schizophrenia","narcissism","narcolepsy","Drug_Addiction","relationships",
             "gaming","worldnews","politics","movies","science","atheism","Showerthoughts",
             "cringe","rage","niceguys","sex","loseit","raisedbynarcissists","BPD",
             "AvPD","DID","SPD","EOOD","CompulsiveSkinPicking","psychoticreddit","insomnia"]
    
    generate_job(func="extract_text",category="corpus",inputs={"boards":boards})


# USER FUNCTIONS
def extract_text(boards,output_dir):
    '''extract_text
    main function for parsing reddit boards into deepdive input corpus
    Parameters
    ==========
    boards: list
        list of reddit boards to parse
    '''
    if isinstance(boards,str): boards = [boards]
    if has_internet_connectivity():
        r = praw.Reddit(user_agent='wordfish')

        for board in boards:
            corpus_input = dict()
            print "Parsing %s" %board
            submissions = r.get_subreddit(board).get_hot(limit=1000)
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
            print "%s has %s entities" %(board,len(content))
            # For each result, package into the right format for text parsing
            for c in range(len(content)):
                uid = "%s_%s" %(board,c)
                corpus_input[uid] = {"text":content[c],"labels":[board]}

            # Save articles to text files in output folder     
            save_sentences(corpus_input,output_dir=output_dir,prefix=board)
