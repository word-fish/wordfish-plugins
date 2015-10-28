'''
reddit
plugin for deepdive python to get corpus from reddit
THESE FUNCTIONS ARE NOT WRITTEN / TESTED YET

'''
from deepdive.nlp import get_term_counts, do_stem, get_total_words
from glob import glob
import pandas
import pickle
import praw
import pickle
from glob import glob
import pandas
import sys
import os


# Reddit might have some terms of interest, maybe top boards?
def extract_terms():
    return None

def extract_corpus(boards=None):
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

    r = praw.Reddit(user_agent='deepdive')


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
    result = {"content":content,"disorder":disorder,"score":scores,"uids":ids,"retrieved":now}
    pickle.dump(result,open("analysis/reddit/%s_dict.pkl" %disorder,"wb"))


### 2. COUNT TERMS ##################################################################
term_pickle = "brainbehavior/data/cognitiveatlas/behavioraltraits.pkl"
terms = pickle.load(open(term_pickle,"rb"))
stems = do_stem(terms)

pickles = glob("%s/*_dict.pkl" %outfolder)
for result_file in pickles:
    result = pickle.load(open(result_file,"rb"))
    content = result["content"]
    print "Parsing %s" %result_file
    # We will save counts and total words
    dfcount = pandas.DataFrame(columns=stems)
    totalwords = []
    # We want to keep a count of those with no terms
    noterms = 0
    for t in range(0,len(content)):
        print "%s of %s" %(t,len(content))
        text = ''.join([i if ord(i) < 128 else ' ' for i in content[t]])
        counts = get_term_counts(terms,str(text))
        # Only save if we have at least one!
        if counts["count"].sum() > 0:    
            totalwords.append(get_total_words(text))
            dfcount.loc[t,counts.index] = counts["count"]
    result["dfcount"] = dfcount
    result["words"] = totalwords 
    # Save to output file
    pickle.dump(result,open(result_file.replace("dict","dict_counts"),"wb"))

### 3. COMBINE COUNTS BY FAMILY ##############################################################
# Prepare behavioral terms
pickles = glob("%s/*_dict_counts.pkl" %outfolder)
families = get_expanded_family_dict(unique=True)

# This is NOT a diagonal matrix, base terms are in rows, family members in columns
path_similarities = get_path_similarity_matrix()

for result_file in pickles:
    tmp = pickle.load(open(result_file,"rb"))
    print "Parsing disorder %s" %tmp["disorder"]
    result = tmp["dfcount"]
    # This will be a new matrix with only base terms as column names
    familydf = pandas.DataFrame(index=result.index)
    # Step 2: For each term stem (row), find family based on path similarity
    for stem,data in families.iteritems():
        family = path_similarities[stem][path_similarities[stem] != 0]
        # Create a data frame with just the columns
        column_names = [c for c in family.index if c in result.columns]
        family = family[column_names]
        # if there are no family members
        if family.shape[0] == 0: 
            familydf[stem] = result[stem]
        # Weight each count by the path similarity, and sum
        else:
            subset = result[column_names].copy()
            for col in subset.columns:
                subset[col] *= family[col]
            familydf[stem] = subset.sum(axis=1) + result[stem] 
    # Save family data frame to file
    tmp["familydf"] = familydf
    pickle.dump(tmp,open(result_file.replace("dict_counts","dict_counts_family"),"wb"))    

### 4. CO-OCCURRENCE ##################################################################
    # Now calculate co-occurrence
    terms = familydf.columns.tolist()

    # Result df will be terms by terms
    df = pandas.DataFrame(columns=terms,index=terms)

    for t in range(0,len(terms)):
        print "%s of %s" %(t,len(terms))
        term1 = terms[t]
        subset = familydf.loc[familydf[term1]>0]
        number_with_term1 = subset.shape[0]
        if number_with_term1 != 0:
            for term2 in terms:
                number_with_term2 = subset[term2].loc[subset[term2]>0].shape[0]
                pt2_given_t1 = float(number_with_term2) / number_with_term1
                # [row](probability), [col](given)
                df.loc[term2,term1] = pt2_given_t1    
        else:
            df.loc[:,term1] = 0

    df.to_csv("/home/vanessa/Documents/Dropbox/Code/Python/brain-behavior/analysis/reddit/result/%s_co-occurrence.tsv" %disorder,sep="\t")
