from nltk.tokenize import RegexpTokenizer
tokenizer = RegexpTokenizer(r'\w+')

#with this function we parse each word of the files and mark it either as pos or as neg
#the final data structure of that lexicon is dictionary, thus two dictionaries are returned
def opinion_lexicon():

	file = open("positive-words.txt")
	raw = file.read()

	file2 = open("negative-words.txt")
	raw2 = file2.read()

	#we use the tokenizer to split the txt in words
	pos_tokens = tokenizer.tokenize(raw)
	neg_tokens = tokenizer.tokenize(raw2)

	pos = [(x, 'pos') for x in pos_tokens]
	neg = [(x, 'neg') for x in neg_tokens]

	pos_lexicon = dict(pos)
	neg_lexicon = dict(neg)
	return pos_lexicon, neg_lexicon