#!/usr/bin/env python

"""

CognitiveAtlas: part of the brainbehavior python package

BrainBehavior: This module will work with three databases that
combined can make inferences about disorders and behaviors:

SAMPLE USAGE: Please see README included with package


"""

from textblob import Word
from textblob.wordnet import Synset
import pickle
import numpy
import pandas
import json
import re
import os

__author__ = ["Vanessa Sochat (vsochat@stanford.edu)"]
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2015/07/24 $"
__license__ = "Python"

# Cognitive Atlas Functions---------------------------------------------------------

# Behaviors --------------------------------------------------------------------

# This function is used to generate likely behaviors/synsets for any word
class Behavior:

    def __init__(self,trait):
        self.get_trait(trait)
        self.is_a = self.get_synonyms()
        self.specifier = ''

    def get_trait(self,trait):
        self.trait = trait.split("(")[0].strip()
        if len(trait.split("(")) > 1:
            self.specifier = trait.split("(")[1].replace(")","").strip()

    def __str__(self):
        return self.trait

    def __repr__(self):
        return self.trait

    def get_synonyms(self):
        word = Word(self.trait)
        self.definitions = word.definitions
        return word.synsets

    def get_json(self,sim_metric="path"):
        # First make list of all unique synsets
        synsets = get_behavior_synset(self)
        return get_behavior_json(synsets,sim_metric=sim_metric)
        

# Global functions
def make_node(syn,nid,class_name):
    return {"name":syn.name(),
            "nid":nid,
            "class":class_name,
            "definition":syn.definition(),
            "example":"|".join([x for x in syn.examples()]),
            "lexname":syn.lexname(),
            "lemmanames":"|".join([x for x in syn.lemma_names()]),
            "pos":syn.pos(),
            "similartos":"|".join([x.name() for x in syn.similar_tos()]),
            "topicdomains":"|".join([x.name() for x in syn.topic_domains()])}

def get_json(behaviors,sim_metric="path"):
    synsets = get_behaviors_synsets(behaviors)
    return get_behavior_json(synsets,sim_metric)

'''Get path distance for each of syn1 and syn2'''
def get_relation(syn1,syn2,sim_metric):
    from nltk.corpus import wordnet as wn
    if sim_metric == "path":
        # https://stackoverflow.com/questions/20075335/is-wordnet-path-similarity-commutative
        sim_score = min(wn.path_similarity(syn1,syn2), wn.path_similarity(syn2,syn1))
    elif sim_metric == "lch":
        if syn1.pos() == syn2.pos():
            sim_score = syn1.lch_similarity(syn2)
        else:
            sim_score = 0
    elif sim_metric == "wup":
        sim_score = syn1.wup_similarity(syn2)
    if sim_score: return sim_score
    else: return 0 
    

'''Return link json for two nodes'''
def make_link(syn1,syn2,sim,sim_metric):
    nid1 = syn1["nid"]
    nid2 = syn2["nid"]
    return {"source":nid1,"target":nid2,"value":sim,"metric":sim_metric}

# Extract a list of all synsets, lemmas, and "similartos"
def get_term_objects(behaviors):
    synsets = get_behaviors_synsets(behaviors)
    all_terms = []
    for syn,data in synsets.iteritems(): # synsets already contain parents/child etc.
        # We also need to get the lemmas
        lemmas = data["data"].lemmas()
        lemma_synsets = [l.synset() for l in lemmas]
        new_terms = [data["data"]] + data["data"].similar_tos() + lemma_synsets
        all_terms = all_terms + new_terms
    return all_terms

# Extract family from a synset
def get_synset_family(synset):
    lemmas = [l.synset() for l in synset.lemmas()]
    is_as = synset.hypernyms()
    part_of = synset.member_holonyms() 
    family = numpy.unique(synset.similar_tos() + lemmas + part_of + is_as).tolist()
    return numpy.unique(family).tolist()

# Get opposites
def get_synset_opposites(synset):
    lemmas = synset.lemmas()
    opposites = []
    for lemma in lemmas:
        opposites = opposites + [l.synset() for l in lemma.antonyms()]
    return numpy.unique(opposites).tolist()

# Get unique strings to parse text (we can compare Word strings and text blobs)
def get_term_strings(behaviors,word_only=True):
    all_terms = get_term_objects(behaviors)
    # Now we want a string associated with each
    term_strings = []
    for term in all_terms:
        if word_only:
            term_strings.append(term.name().split(".")[0])
        else:
            term_strings.append(term.name())
    term_strings = numpy.unique(term_strings).tolist()
    # Finally, some terms don't have synsets, add them
    for behavior in behaviors:
        if behavior.trait not in term_strings:
            term_strings.append(behavior.trait) 
    return numpy.sort(term_strings).tolist()

# Return most common element in a list (used for directions "similar" and "opposite"
# "similar" will be return if they are equal
def get_most_common(lst):
    return max(set(lst), key=lst.count)

# Generate a matrix of path similarity scores between all terms, for use in text parsing
def get_path_similarity_matrix(family_index=None,sim_metric="path"):
    from nltk.corpus.reader.wordnet import Lemma, Synset as Syn
    from brainbehavior.nlp import do_stem
    if family_index == None: 
        family_index = get_expanded_family_dict(unique=True)

    families = get_expanded_family_dict(unique=True)
    allstems = get_expanded_behavior_list(sim_metric=sim_metric,synset_names=False)

    # Now fill in matrix! We are only defining similarity stem|member (row --> column)
    df = pandas.DataFrame(index=allstems,columns=allstems)
    for stem, family in families.iteritems():
        # Find unique family stems
        unique_family = numpy.unique(family["family"]).tolist()
        for member in unique_family:
            idx = family["family"].index(member)
            if isinstance(idx,int): idx = [idx]
            direction = get_most_common([family["direction"][x] for x in idx])
            similarity = numpy.mean([family["similarity"][x] for x in idx])
            if direction != "similar":
                similarity = -1*similarity
            # We will be conservative and define similarity == 0 in the case of conflict 
            if not numpy.isnan(df.loc[stem,member]) and df.loc[stem,member] != similarity:
                if similarity == 0:
                    print "Replacing %s with %s for terms %s,%s!" %(df.loc[stem,member],similarity,stem,member)
                    df.loc[stem,member] = similarity
            else:
                df.loc[stem,member] = similarity
            
    # Fill in zeros for values that are still nan
    df[df.isnull()] = 0
    return df


def get_behavior_json(synsets,sim_metric="path"):
    if sim_metric in ["path","lch","wup"]:
        
        # We need to define the similarity (links) between all synsets
        links = []
        for s1 in range(len(synsets.keys())):
            for s2 in range(len(synsets.keys())):
                if s1<s2:
                    syn1 = synsets.keys()[s1]
                    syn2 = synsets.keys()[s2]
                    sim = get_relation(synsets[syn1]["data"],synsets[syn2]["data"],sim_metric=sim_metric)
                    if sim != None:
                        links.append(make_link(synsets[syn1],synsets[syn2],sim,sim_metric))

        # Extract nodes from the synsets
        nodes = []
        for syn in synsets.keys():
            nodes.append(synsets[syn]["node"])
        return {"links":links,"nodes":nodes}

    else:
        print "Error: sim_metric must be one of 'path'\n'lch':semantic relatedness of word senses using the method described by Leacock and Chodorow (1998) or \n'wup': semantic relatedness of word senses using the edge counting method of the of Wu & Palmer (1994)"
 

def get_behaviors_synsets(behaviors):
    synsets = dict()
    all_nids = []
    if not isinstance(behaviors,list):
        behaviors = [behaviors]
    nid = 1
    for behavior in behaviors:
        new_synsets = get_behavior_synset(behavior,nid)
        new_nids = [new_synsets[x]["nid"] for x in new_synsets.keys()]
        all_nids = all_nids + new_nids
        nid = numpy.max(all_nids) + 1
        synsets.update(new_synsets)
    return synsets


def get_behavior_synset(behavior,nid=1):
    synsets = dict()
    for s in range(len(behavior.is_a)):
        syn = behavior.is_a[s]
        node = make_node(syn,nid,behavior.trait)
        # We will only include relationships that are descriptors
        acceptable_pos = ["s","a"]
        synsets[syn.name()] = {"data":syn,"nid":nid,"node":node}
        nid = nid + 1
        # parents and children
        relations = syn.hypernyms() + syn.hyponyms()
        while relations:
            relation = relations.pop()
            if relation.pos() in acceptable_pos:
                node = make_node(relation,nid,behavior.trait)
                synsets[relation.name()] = {"data":relation,"nid":nid,"node":node}
                nid = nid + 1
                new_relations = [new for new in relation.hypernyms() + relation.hyponyms() if new.name() not in synsets.keys()]
                relations = relations + new_relations
    return synsets


def get_input_file():
    diry = os.path.dirname(os.path.realpath(__file__))
    return "%s/brainbehavior/data/cognitiveatlas/cogPheno_791.tsv" %diry

def read_cogpheno(input_file=None):
    if input_file == None:
        input_file = get_input_file()
    return pandas.read_csv(input_file,sep="\t")


# QUALITY CONTROL -----------------------------------------------------------------------------------------------------
# Tell the user for any terms that are not in wordnet (in case we want to change)
def check_cogpheno_terms(input_file=None):
    if input_file == None:
        input_file = get_input_file()
    cogpheno = read_cogpheno(input_file)
    print "Evaluating terms: terms without matches (below) should be re-considered, unless it's a medical term."
    traits = cogpheno.question_behavioral_trait.unique()
    traits.sort()
    traits = traits.tolist()[1:len(traits)]
    traits = [x for x in traits if x not in ["nan","None"]]
    for trait in traits:
        tmp = Behavior(trait)
        if len(tmp.is_a) == 0:
            print tmp.trait


# LOADING/SAVING -----------------------------------------------------------------------------------------------------
# Core are just the terms defined in cogatpheno
def get_core_behaviors(input_file=None):
    if input_file == None:
        input_file = get_input_file()
    cogpheno = read_cogpheno(input_file)
    # Reduce down to synsets
    traits = cogpheno.question_behavioral_trait_synset.dropna().unique()
    traits = traits[traits != "None"]
    # Undefined (None) are typically clinical symptoms
    clinical = cogpheno.question_behavioral_trait[cogpheno.question_behavioral_trait_synset=="None"].dropna().unique()
    behaviors = clinical.tolist() + traits.tolist()
    behaviors.sort()
    return behaviors


def get_expanded_behavior_list(sim_metric="path",synset_names=False):
    families = get_families(sim_metric=sim_metric,synset_names=synset_names)
    family_index = get_family_index(families)
    allstems = []
    for stem, indices in family_index.iteritems():
        allstems.append(stem)
        for idx in indices:
            allstems = allstems + do_stem(families[idx]["family"])
    return numpy.unique(allstems).tolist() 


def get_families(sim_metric,synset_names=False):
    from nltk.corpus import wordnet as wn
    from brainbehavior.nlp import do_stem
    behaviors = get_core_behaviors()
    families = []
    for behavior in behaviors:
        if re.search("[.]",behavior):
            tmp = dict()
            syn = wn.synset(behavior)
            similar = get_synset_family(syn)
            opposite = get_synset_opposites(syn)
            directions = ["similar"] * len(similar) + ["opposite"] * len(opposite)
            family = similar + opposite
            tmp["similarity"] = [get_relation(syn,fam,sim_metric) for fam in family]
            if synset_names:            
                family = [f.name() for f in family]
            else:
                family = [f.name().split(".")[0] for f in family]
            tmp["base"] = syn
            tmp["family"] = family
            tmp["direction"] = directions
        else:
            tmp["base"] = behavior
        families.append(tmp)
    return families

def get_family_index(families):
    from brainbehavior.nlp import do_stem
    stems = []
    for f in range(0,len(families)):
        family = families[f]
        if isinstance(family["base"],str): 
            stems.append(do_stem(family["base"])[0])
        else: 
            stems.append(do_stem([family["base"].name().split(".")[0]])[0])
    stems = numpy.unique(stems).tolist()        
    family_index = dict((s, []) for s in stems)
    for f in range(0,len(families)):
        family = families[f]
        if isinstance(family["base"],str):
            stem = do_stem(family["base"])[0] 
            holder = family_index[stem]
            holder.append(f)
            family_index[stem] = holder 
        else: 
            stem = do_stem([family["base"].name().split(".")[0]])[0]
            holder = family_index[stem]
            holder.append(f)
            family_index[stem] = holder 
    return family_index

def get_expanded_family_dict(sim_metric="path",synset_names=False,unique=True):
    from brainbehavior.nlp import do_stem
    families = get_families(sim_metric=sim_metric,synset_names=synset_names)
    if unique==True:
        # Finding an identical stem means that we would need to tell the word apart based
        # on context (eg, sensitive as a noun vs. an adjective. Since this method cannot
        # do that (the stems are both "sensit"), we have to simply merge the families
        family_index = get_family_index(families)
        # Combine families, and save list of all stems (including family)
        combined_families = dict()
        for stem, indices in family_index.iteritems():
            direction = []
            family = []
            similarity = []
            for idx in indices:
                direction = direction + families[idx]["direction"]
                family = family + do_stem(families[idx]["family"])
                similarity = similarity + families[idx]["similarity"]
            combined_families[stem] = {"base":stem,
                                   "family":family,
                                   "direction":direction,
                                   "similarity":similarity} 
        return combined_families
    else:
        return families                 

def behaviors_to_pickle(output_file=None,behavior_set="expanded"):
    if output_file == None:
        diry = os.path.dirname(os.path.abspath(__file__))
        output_file = "%s/brainbehavior/data/cognitiveatlas/behavioraltraits.pkl" %diry
    if behavior_set == "expanded":
        behaviors = get_expanded_behavior_list()
    else:
        behaviors = get_core_behaviors()
    pickle.dump(behaviors,open(output_file,"wb"))

# Expanded include synonyms, similartos
def load_behaviors(input_pickle="brainbehavior/data/cognitiveatlas/behavioraltraits.pkl"):
    return pickle.load(open(input_pickle,"rb"))
