#in the header file we have included all the necessary packages and definitions
from header import *
#pickle is used for the lexicon we constructed
import pickle

#with the following lines of code we parse the reviews and save them in a dataframe
#you have to specify the path that the reviews txt file is located
lexicon = {}
d = {}
reviewsFile = []
with open("/Users/Sofia/Documents/delft/Information_Retrieval/project/ourProject/reviewsTest.txt") as f:
    for line in f:
        reviewsFile.append(eval(line))
DocumentMetricsMatrix=[0,0,0,0]
data = pd.DataFrame(reviewsFile)

#load Domain Specific Lexicon in a new dictionary
with open("DomainSpecificLexicon.txt", "rb") as myFile:
    myNewPulledInDictionary = pickle.load(myFile)

def SafeDivision(x,y):
    if y==0:
        return 0;
    else:
        return x/y;

#Function that removes all special characters from a sentence
def clean_up_list(word_list):
    clean_word_list = []
    #Split each sentence into words 
    word_list = word_list.split()
    for word in word_list:
        #for each word search if there is one of these characters in it
        symbols = "!@#$%^&*()_-|~`';+[]{/\"?>}<:."
        for i in range(0, len(symbols)):
            #if there is replace that symbol with null
            word = word.replace(symbols[i], "")
            #transform all words in lower case 
            word = word.lower()
        if len(word) > 0:
            clean_word_list.append(word)
    return clean_word_list


#Function that assigns a part of speech tag to each word in a sentence with the nltk tagger
def tagger(listOfSent):
    res = []
    #loop to iterate every sentence in the review
    for sent in listOfSent:
        #append a part of speech tag to each word in the sentence
        res.append(nltk.pos_tag(sent))
    return res

#This function again assigns a part of speecg tag to every word in the every sentnenc of the review using the Standford tagger
#Take as input the whole review and return the tag for each word that is contained in the review
def Stanford_pos_tagger (sentence):
    tags= []
    #loop to iterate every sentence in the review
    for sent in sentence:
        #create specific format for the sentence that the tagger needs
        sent = ' '.join(sent)
        tags.append(pos_tagger.tag(word_tokenize(sent)))
    return tags


def remove_Stop_words(review):
    #Replace the characters ! and ? with the character . to avoid mismatch in our dataframes
    test = review.replace("!", ".")
    test = test.replace("?", ".")
    test = test.split('.')
    f = []
    for sent in test:
        words = sent.split(' ')
        afterStopWord = ""
        for i in words:
            if i not in stopwords:
                afterStopWord += i + ' '
        afterStopWord = clean_up_list(afterStopWord)
        if len(afterStopWord) != 0:
            f.append(afterStopWord)
    return f

#this function creates the dependencies between thw words in the review. Input in this function is thw whole review.
def Dependency_parser(sentence):
    depend = []
    #loop to iterate every sentence in the review
    for sent in sentence:
        sent = ' '.join(sent)
        exist=0
        splitted= sent.split(" ")
        #check if in the sentence any of the aspect that we want is mentioned. If not, for this sentence we 
        #dont create the dependencies and we store just an emopty list. This is in order to reduce the run time by not  passing to
        #the parser unnecessary sentences
        for word in splitted:
            for key,val in AspectSynonyms.items():
                if word in val:
                    exist=1
        if exist==1:
            r = dep_parser.raw_parse(sent)
            d = next(r)
            depend.append(list(d.triples()))
        else:
            depend.append({})

    return depend


#this function takes the review and split it into sentences.The result of this function is the input on the Dependency parser above
def test(review):
    test = review.split('.')
    f = []
    for sent in test:
        words = sent.split(' ')
        if len(words) !=1:
            f.append(words)
    return f

#Function that reduces each word in a sentence to its most basic form
def Lemmatizing(listOfSent):
    ps = WordNetLemmatizer()
    res = []
    #loop to iterate every sentence in a review
    for sent in listOfSent:
        eachSent = []
        #loop to iterate every word in a sentence 
        for word in sent:
            #Get the basic form of this word and add it in the result list
            word = ps.lemmatize(word)
            eachSent.append(word)
        res.append(eachSent)
    return res

# Function that counts how many times a word appears in a sentence
def create_dictionary(listOfSent):
    word_count = {}
    #loop to iterate each sentence in a review
    for sent in listOfSent:
        #loop to iterate each word in a sentence
        for word in sent:
            if word in word_count:
                word_count[word] += 1
            else:
                word_count[word] = 1
    return word_count

#for each word of each sentence of the review that is received as an input , we assign it with a sentiment.

def sentiment(listOfSent, tagging, count):
    s = []
    counts = 0
    for j, sent in enumerate(listOfSent):
        eachSent = []
        for ind, i in enumerate(sent):
            try:
                swn.senti_synset(i+'.'+tags[tagging[j][ind][1]]+'.'+str(count[i])).pos_score()
                pass
            except:
                sen = t = n =  0
                pass
            else:
				#We use our own Domain Specific Lexicon in this case in order to assign a sentiment
                if (i in myNewPulledInDictionary):
                    sen = myNewPulledInDictionary[i]
                else:
					#in case the word is not present in our dictionary, we use sentiWordNet
                    counts += 1
                    sen = swn.senti_synset(i + '.' + tags[tagging[j][ind][1]] + '.' + str(count[i])).pos_score() - swn.senti_synset(i + '.' + tags[tagging[j][ind][1]] + '.' + str(count[i])).neg_score()
            eachSent.append(sen)
        s.append(eachSent)
    return s

#in this case we asssign a sentiment to each word of each sentence of a review, 
#based on the both the sentiwordnet and the corpus of positive and negative words that we have derived
def newSentiment(listOfSent, tagging, count):
    s=[]
    for j, sent in enumerate(listOfSent):
        eachSent = []
        for ind, word in enumerate(sent):
            sen={}
            try:
                swn.senti_synset(word+'.'+tags[tagging[j][ind][1]]+'.'+str(count[word])).pos_score()
                pass
            except:
                sen[word] =  0.0
                pass
            else:
                sen[word] = swn.senti_synset(word+'.'+tags[tagging[j][ind][1]]+'.'+str(count[word])).pos_score()-swn.senti_synset(word+'.'+tags[tagging[j][ind][1]]+'.'+str(count[word])).neg_score()
            #if the value returned by the sentiWordnet is not the same as in the opinion lexicon we change it's value
            #eventually we will just have positive and negative review, so we assign 0.5 with the corresponding sign of each case
            if sen[word] > 0 and word in neg_lexicon:
                sen[word] = -0.5
            elif sen[word] < 0 and word in pos_lexicon:
                sen[word] = 0.5
            elif sen[word] == 0 and word in neg_lexicon:
                sen[word] = -0.5
            elif sen[word] == 0 and word in pos_lexicon:
                sen[word] = 0.5
            eachSent.append(sen)
        s.append(eachSent)
    return s


#used for document level metrics calculation
def DocumentMetrics(review, tagging, sentiment1, rating):
    counter = 0
    sentiment = 0
    for i, sentence in enumerate(review):
        for index, word in enumerate(tagging[i]):
            if (word[1] in tags) and tags[word[1]] != "n":
                counter += 1;
                if (word[0] in myNewPulledInDictionary):
                    sentiment += myNewPulledInDictionary[word[0]]
                else:
                    sentiment += sentiment1[i][index]
    sentiment = SafeDivision(sentiment,counter)
    res = ""
    if (rating["overall"] > 3):
        if (sentiment > 0):
            # true positive
            DocumentMetricsMatrix[0]+=1
        else:
            # false negative
            DocumentMetricsMatrix[3]+=1
    else:
        if (sentiment > 0):
            # false positive
            DocumentMetricsMatrix[1] += 1
        else:
            # true negative
            DocumentMetricsMatrix[2] += 1

#Function used for baseline algorithm where we locate sentences that refer to one aspect and find the adjectives in that sentence in order to assign
#sentiment to that aspect
def SingleAspect(review, tagging, sentiment1):
    res=[]
    #loop to iterate every sentence in a review
    for i, sentence in enumerate(review):
        aspectsDetected=[];
        #Assign to each list the words we use to identify the aspect in a review 
        aspectsLocation=AspectSynonyms["location"]
        aspectsService=AspectSynonyms["service"]
        aspectsValue=AspectSynonyms["value"]
        aspectsRoom=AspectSynonyms["rooms"]
        #Loops to check if one or more of these aspects appear in a sentence and if yes add it to list aspectsDetected
        for aspect in aspectsLocation:
            if aspect in ' '.join(sentence):
                aspectsDetected.append("location")
        for aspect in aspectsService:
            if aspect in ' '.join(sentence):
                aspectsDetected.append("service")
        for aspect in aspectsValue:
            if aspect in ' '.join(sentence):
                aspectsDetected.append("value")
        for aspect in aspectsRoom:
            if aspect in ' '.join(sentence):
                aspectsDetected.append("rooms")
        #If there are no references for any aspect do nothing
        if len(aspectsDetected) == 0:
            test = 0
            print("No aspects")
        # If there is one aspect find all adjectives in that sentence and add their sentiment values
        elif len(aspectsDetected) == 1:
            sentiment=0
            for index,word in enumerate(tagging[i]):
                if word[1] == "JJ":
                    if (word[0] in myNewPulledInDictionary):
                        sentiment += myNewPulledInDictionary[word[0]]
                    else:
                        sentiment+=sentiment1[i][index]
            res.append({aspectsDetected[0]: sentiment})
        # Imore than one aspect detected ignore sentence
        else:
            ttt='more than one aspect'
            print("More than one aspects", ' '.join(sentence))
    return res


#this function was used to create our domain specific lexicon.used only once, with 20.000 reviews as input.
#The resulted dictionary is stored for re-use using cpickle library of python.
def LexiconCreate(review, tagging,ratings):

    for i, sentence in enumerate(review):
        aspectsDetected = [];

        aspectsLocation = AspectSynonyms["location"]
        aspectsService = AspectSynonyms["service"]
        aspectsValue = AspectSynonyms["value"]
        aspectsRoom = AspectSynonyms["rooms"]

        for aspect in aspectsLocation:
            if aspect in ' '.join(sentence):
                aspectsDetected.append("location")

        for aspect in aspectsService:
            if aspect in ' '.join(sentence):
                aspectsDetected.append("service")

        for aspect in aspectsValue:
            if aspect in ' '.join(sentence):
                aspectsDetected.append("value")

        for aspect in aspectsRoom:
            if aspect in ' '.join(sentence):
                aspectsDetected.append("rooms")

        if len(aspectsDetected) == 0:
            tt="No aspects"
        elif len(aspectsDetected) == 1:
            sentiment = 0
            for index, word in enumerate(tagging[i]):
                if(word[1] in tags) and tags[word[1]] != "n" and (aspectsDetected[0] in ratings):
                    if(ratings[aspectsDetected[0]]>3):
                        if(word[0] in lexicon):
                            lexicon[word[0]][0]+=1
                        else:
                            lexicon[word[0]]=[0,0]
                            lexicon[word[0]][0] += 1
                    else:
                        if(word[0] in lexicon):
                            lexicon[word[0]][1]+=1
                        else:
                            lexicon[word[0]]=[0,0]
                            lexicon[word[0]][1] += 1
        else:
           tt2="more than one"


#This function merges aspect results from different sentences in the same review to calculate the final polarity for each review.
def FixSingleAspect(polarities):
    result=[]
    ValueLocation = 0
    ValueService = 0
    ValueRooms = 0
    ValuePrice = 0
    # For every pair item in the list of aspects detected in a review from the function SingleAspect
    for i in polarities:
        #For the key of every pair if it corresponds to one of the aspects add their values
        for key in i:
            if 'location' in i:
                ValueLocation=ValueLocation+i[key]
            elif 'rooms' in i:
                ValueRooms=ValueRooms+i[key]
            elif 'service' in i:
                ValueService=ValueService+i[key]
            elif 'value' in i:
                ValuePrice=ValuePrice+i[key]
    # Return a final list with all four aspects and their corresponding sentiment for this review
    result.append({'location': ValueLocation})
    result.append({'rooms': ValueRooms})
    result.append({'service' : ValueService})
    result.append({'value': ValuePrice})
    return result


#used to compute the metrics matrices (true positives,true negatives etc) for each aspect
def ComputeMetrics(labels,AspectPolarities):
    MetricsLocation = [0,0,0,0]
    MetricsService = [0,0,0,0]
    MetricsValue = [0,0,0,0]
    MetricsRoom=[0,0,0,0]
    for key in labels.keys():
        for item in AspectPolarities:
            if(key in item.keys()):
                if(key=="location"):
                    if(item[key]>0 and labels[key]>3):
                        MetricsLocation[0]+=1
                    elif(item[key]>0 and labels[key]<=3):
                        #False Positive
                        MetricsLocation[1]+=1
                    elif(item[key]<0 and labels[key]<=3):
                        #TrueNegative
                        MetricsLocation[2] += 1
                    elif(item[key]<0 and labels[key]>3):
                        # FalseNegative
                        MetricsLocation[3] += 1
                elif(key=="service"):
                    if(item[key]>0 and labels[key]>3):
                        MetricsService[0]+=1
                    elif(item[key]>0 and labels[key]<=3):
                        #False Positive
                        MetricsService[1]+=1
                    elif(item[key]<0 and labels[key]<=3):
                        #TrueNegative
                        MetricsService[2] += 1
                    elif(item[key]<0 and labels[key]>3):
                        # FalseNegative
                        MetricsService[3] += 1
                elif(key=="rooms"):
                    if(item[key]>0 and labels[key]>3):
                        MetricsRoom[0]+=1
                    elif(item[key]>0 and labels[key]<=3):
                        #False Positive
                        MetricsRoom[1]+=1
                    elif(item[key]<0 and labels[key]<=3):
                        #TrueNegative
                        MetricsRoom[2] += 1
                    elif(item[key]<0 and labels[key]>3):
                        # FalseNegative
                        MetricsRoom[3] += 1
                elif(key=="value"):
                    if(item[key]>0 and labels[key]>3):
                        MetricsValue[0]+=1
                    elif(item[key]>0 and labels[key]<=3):
                        #False Positive
                        MetricsValue[1]+=1
                    elif(item[key]<0 and labels[key]<=3):
                        #TrueNegative
                        MetricsValue[2] += 1
                    elif(item[key]<0 and labels[key]>3):
                        # FalseNegative
                        MetricsValue[3] += 1
    return [MetricsLocation,MetricsRoom,MetricsService,MetricsValue]

#this function is actually our final implementation. It takes as input the review in the dependency format and the sentiment of each word
#in the review. As a result it produce the polarity of all aspects in every review.
def sentimentDependency(review,sentiment,text):
    #we specifiy which rules we will consider from the dependencies.
    rules = ['amod', 'nsubj', 'dep', 'dobj', 'neg', 'nmod', 'nsubjpass']
    #we specify the negation rules from dependencies
    neg_rules = ['conj','neg']
    result = []
    list = []
    num_of_sentence = 0
    flag = ('not' in text or 'no' in text)
    neg = None
    #for every sentence in the review
    for sentence in review:
        #for each rule in the sentence
        for dependent in sentence:
            #iteration in aspect list in order to find if any of the words which mentioned belongs to the aspect list.
            #Since in each rule, a pair of words exist, we have to check if any of these two words belong in the aspect list
            for key, value in AspectSynonyms.items():
                #We check if the right part (word) of the rule exist in aspect list
                if dependent[0][0].lower() in value:
                    #we check if the rule belong to list list with the rules that we want
                    if dependent[1] in rules:
                        #We check if this rule is a negation rule because this rule need a different handle.
                        if flag:
                            neg = negation(dependent, sentence, sentiment[num_of_sentence])
                            list.append({key: neg})
                        if neg == None:
                            #iteration on the sentiment list of each word to match words with their sentiments
                            for newsent in sentiment[num_of_sentence]:
                                for key_sent, val_sent in newsent.items():
                                    #specific check for the aspect 'value' since it need a special handle
                                    if key == 'value':
                                        if dependent[0][0] == key_sent:
                                            list.append({key: val_sent})
                                    elif dependent[2][0] == key_sent:
                                        list.append({key: val_sent})
                    #the case of neither, nor is different from the not
                    if dependent[1] in neg_rules:
                        flag = ('neither' in text or 'nor' in text)
                        if flag:
                            neg = negation(dependent, sentence, sentiment[num_of_sentence])
                            list.append({key: neg})
                #The same procedure as previous, but now checking the left part(word) of the rule
                elif dependent[2][0].lower() in value:
                    if dependent[1] in rules:
                        if flag:
                            neg = negation(dependent, sentence, sentiment[num_of_sentence])
                            list.append({key: neg})
                        if neg == None:
                            for newsent in sentiment[num_of_sentence]:
                                for key_sent, val_sent in newsent.items():
                                    if key == 'value':
                                        if dependent[2][0] == key_sent:
                                            list.append({key: val_sent})
                                    elif dependent[0][0] == key_sent:
                                        list.append({key: val_sent})
                    if dependent[1] in neg_rules:
                        flag = ('neither' in text or 'nor' in text)
                        if flag:
                            neg = negation(dependent, sentence, sentiment[num_of_sentence])
                            list.append({key: neg})
        num_of_sentence += 1
    final = []
    for it in list:
        for k, v in it.items():
            if v is not None:
                final.append({k: v})
    #we conduct a summation of the aspect in all sentences of the review in order to generate the total polarity of every aspect inside the review
    ValueLocation = 0
    ValueService = 0
    ValueRooms = 0
    ValuePrice = 0
    for i in final:
        for key in i:
            if 'location' in i:
                #print("Found Location")
                ValueLocation = ValueLocation + i[key]
            elif 'rooms' in i:
                #print("Found Rooms")
                ValueRooms = ValueRooms + i[key]
            elif 'service' in i:
                #print("Found service")
                ValueService = ValueService + i[key]
            elif 'value' in i:
                #print("Found value")
                ValuePrice = ValuePrice + i[key]
    result.append({'location': ValueLocation})
    result.append({'rooms': ValueRooms})
    result.append({'service': ValueService})
    result.append({'value': ValuePrice})
    return result

#The negation function handles the most common forms of negation: not, neither, nor, no
#in case on of these is located we take into consideration two pairs of words from the dependency parser
#in order to specify which word this negation concerns
def negation(dependency, sentence, newsent):
    neg_list = ['not', 'neither', 'nor', 'no']
    for dep in sentence:
        item = ''
        if (dep[0][0] in neg_list and (dep[2][0] == dependency[0][0] or dep[2][0] == dependency[2][0])):
            item = dep[2][0]
        elif (dep[2][0] in neg_list and (dep[0][0] == dependency[0][0] or dep[0][0] == dependency[2][0])):
            item = dep[0][0]
        for s in newsent:
            for key_sent,val_sent in s.items():
                if item == key_sent:
                    #when the negation is found we reverse the value of the sentiment
                    #from positive to negative and vice versa
                    return -val_sent

#this column is needed for the dependency parser
data['test'] = data.apply(lambda row: test(row['text']), axis=1)
data['pr_text'] = data.apply(lambda row: remove_Stop_words(row['text']), axis=1)
data['WordCount'] = data.apply(lambda row: create_dictionary(row['pr_text']), axis=1)
#UNCOMMENT the following line to use Standford tagger instead of nltk tagger used now
#data['PosTagger'] = data.apply(lambda row: Stanford_pos_tagger(row['pr_text']), axis=1)
data['PosTagger'] = data.apply(lambda row: tagger(row['pr_text']), axis=1)
# Here we create the dependencies between words
data['Dependency'] = data.apply(lambda  row: Dependency_parser(row['test']),axis=1)
data['pr_text'] = data.apply(lambda row: Lemmatizing(row['pr_text']), axis=1)
data['sentiment'] = data.apply(lambda row: sentiment(row['pr_text'], row['PosTagger'], row['WordCount']), axis=1)
data['newSentiment'] = data.apply(lambda row: newSentiment(row['pr_text'], row['PosTagger'], row['WordCount']), axis=1)
data['DocumentMetrics'] = data.apply(lambda row: DocumentMetrics(row['pr_text'],row['PosTagger'], row['sentiment'],row['ratings']),axis=1)
#UNCOMMENT the following 2 lines in order to run our BASELINE functionality
#data['AspectPolarity'] = data.apply(lambda row: SingleAspect(row['pr_text'],row['PosTagger'], row['sentiment']),axis=1)
#data['AspectPolarity']=data.apply(lambda row: FixSingleAspect(row['AspectPolarity']),axis=1)

#Here we generate the results of our final implementation
data['DepSentiment'] = data.apply(lambda row: sentimentDependency(row['Dependency'],row['newSentiment'], row['text']),axis=1)


FinalMetrics = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
tempMetrics = []
for index,row in data.iterrows():
    tempMetrics = ComputeMetrics(row['ratings'], row['DepSentiment'])
	#UNCOMMENT following line in case we want to run our basline approach.data["AspectPolarity"] column has to be present too.
	#tempMetrics = ComputeMetrics(row['ratings'], row['AspectPolarity'])
    i = 0
    for item in tempMetrics:
        #Final Metrics=[tp,fp,tn,fn]
        FinalMetrics[i][0]+=item[0]
        FinalMetrics[i][1]+=item[1]
        FinalMetrics[i][2]+=item[2]
        FinalMetrics[i][3]+=item[3]
        i+=1
j = 0

#with the help of LexiconCreate() function,from above, we can use this function to create our own domain specific lexicon
def DomainSpecificLexiconCreation():
    for index, row in data.iterrows():
        LexiconCreate(row['pr_text'], row['PosTagger'], row['ratings'])
    PosCount = 0
    NegCount = 0
    for lexword in list(lexicon):
		#we remove all words that appear only once in the whole dataset to eliminate irrelevant cases that appear by chance.
        if (lexicon[lexword][0] + lexicon[lexword][1] < 2):
            # del lexicon[lexword]
            lexicon.pop(lexword)
        else:
            PosCount += lexicon[lexword][0]
            NegCount += lexicon[lexword][1]
    DomainSpecificSentiment = {}
    for lexword in lexicon:
		#calculating positive and negative frequencies of the words
        freqPos = SafeDivision(lexicon[lexword][0], PosCount)
        freqNeg = SafeDivision(lexicon[lexword][1], NegCount)
		#computing their sentiment
        PD = SafeDivision(freqPos - freqNeg, freqPos + freqNeg)
        if PD > 0:
            sent = PD ** 2
        else:
            sent = -PD ** 2
        DomainSpecificSentiment[lexword] = sent
		#save the created lexicon, so we can re-use it without creating it every time
        with open("DomainSpecificLexicon.txt", "wb") as myFile:
             pickle.dump(DomainSpecificSentiment, myFile)


#UNCOMMENT to re-create domain-specific lexicon.
#DomainSpecificLexiconCreation()


#Compute FInal Metrics for each aspect after COMPUTEMETRICS function is done
j=0
for item in FinalMetrics:
   if(j==0):
       accuracyLocation=SafeDivision(item[0]+item[2],sum(item))
       precisionLocation=SafeDivision(item[0],(item[0]+item[2]))
       recallLocation=SafeDivision(item[0],(item[0]+item[3]))
       FscoreLocation=2*SafeDivision((precisionLocation*recallLocation),(precisionLocation+recallLocation))
   elif(j==1):
       accuracyRooms = SafeDivision(item[0] + item[2], sum(item))
       precisionRooms = SafeDivision(item[0], (item[0] + item[2]))
       recallRooms = SafeDivision(item[0], (item[0] + item[3]))
       FscoreRooms=2*SafeDivision((precisionRooms*recallRooms),(precisionRooms+recallRooms))
   elif(j==2):
       accuracyService = SafeDivision(item[0] + item[2], sum(item))
       precisionService = SafeDivision(item[0], (item[0] + item[2]))
       recallService = SafeDivision(item[0], (item[0] + item[3]))
       FscoreService=2*SafeDivision((precisionService*recallService),(precisionService+recallService))
   elif(j==3):
       accuracyValue = SafeDivision(item[0] + item[2], sum(item))
       precisionValue = SafeDivision(item[0], (item[0] + item[2]))
       recallValue = SafeDivision(item[0], (item[0] + item[3]))
       FscoreValue=2*SafeDivision((precisionValue*recallValue),(precisionValue+recallValue))
   j+=1


#Document Level metrics final calculation
accuracyDocument=SafeDivision(DocumentMetricsMatrix[0]+DocumentMetricsMatrix[2],sum(DocumentMetricsMatrix))
precisionDocument=SafeDivision(DocumentMetricsMatrix[0],(DocumentMetricsMatrix[0]+DocumentMetricsMatrix[2]))
recallDocument=SafeDivision(DocumentMetricsMatrix[0],(DocumentMetricsMatrix[0]+DocumentMetricsMatrix[3]))
FscoreDocument=2*SafeDivision((precisionDocument*recallDocument),(precisionDocument+recallDocument))




