import pandas as pd
import nltk
import re
import pickle
from nltk.corpus import stopwords
from nltk.corpus import sentiwordnet as swn
from nltk import pos_tag, word_tokenize
from nltk.stem import PorterStemmer
from nltk.parse import stanford
import os
import operator
from nltk.stem import WordNetLemmatizer
from nltk.tag.stanford import StanfordPOSTagger # pos tagger stanford
from nltk.parse.stanford import StanfordDependencyParser  #depedency parser

os.environ['STANFORD_MODELS'] = '/Users/Sofia/Documents/delft/Information_Retrieval/project/ourProject/jars/stanford-parser-3.9.1-models.jar'
os.environ['STANFORD_PARSER'] = '/Users/Sofia/Documents/delft/Information_Retrieval/project/ourProject/jars/stanford-parser.jar'

######## Standford tagger  ########################
model = '/Users/Sofia/Documents/delft/Information_Retrieval/project/ourProject/jars/english-bidirectional-distsim.tagger'
jar ='/Users/Sofia/Documents/delft/Information_Retrieval/project/ourProject/jars/stanford-postagger.jar'
pos_tagger = StanfordPOSTagger(model, jar, encoding='utf8')

########## stanford depedency parser ############
dep_parser=StanfordDependencyParser(model_path="/Users/Sofia/Documents/delft/Information_Retrieval/project/ourProject/jars/englishPCFG.ser.gz")


stopwords = stopwords.words('english')
#we have created a correspondance between the POS Tagger tags and the simples
#than the lexicon needs
tags = {
    "CC": "n",
    "JJ": "a",
    "JJR": "a",
    "JJS": "a",
    "MD": "v",
    "NN": "n",
    "NNP": "n",
    "NNPS": "n",
    "NNS": "n",
    "VB": "v",
    "VBD": "v",
    "VBG": "v",
    "VBN": "v",
    "VBP": "v",
    "VBZ": "v",
    "WRB": "r",
    "RB": "r",
    "RBR": "r",
    "RBS": "r",
}

#the file opinionLexicon has the function opinion_lexicon
#which loads the two files negative and positive words that will be needed in the code
from opinionLexicon import opinion_lexicon
pos_lexicon, neg_lexicon = opinion_lexicon()

#The aspect List contains as keys the aspects we want to search the reviews for
#and as values the most important synonyms we found
AspectSynonyms={
    "location": ['location', 'distance', 'city', 'center', 'station', 'local', 'km', 'placement', 'locating', 'position', 'positioning', 'emplacement', 'localization', 'localisation', 'locating', 'fix', 'location', 'm','located'],
    "service": ['service', 'lobby', 'reception', 'maid', 'staff', 'waiter', 'disservice', 'divine_service', 'Service', 'help', 'table_service', 'servicing', 'serve', 'serving'],
    "value": ['price', 'expensive', 'cheap', 'affordable', 'cost', '$', 'dollars', 'value', 'economic_value', 'note_value', 'prize', 'esteem', 'disesteem','prize', 'prise', 'measure', 'evaluate', 'valuate', 'assess', 'appraise', 'value', 'rate'],
    "rooms": ['room', 'bathroom', 'view', 'suite', 'bed', 'fridge', 'safe', 'sofa', 'rooms', 'beds'],
}


#the following code was used once in a smaller list than the above to find synonyms and antonyms
#with the help of wordnet
# for item in AspectSynonyms:
#     for syn in wordnet.synsets(item):
#         for l in syn.lemmas():
#             AspectSynonyms[item].append(l.name())
#             if l.antonyms():
#                 AspectSynonyms[item].append(l.antonyms()[0].name())