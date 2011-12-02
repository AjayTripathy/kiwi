import sys
import web
from web import form
import nltk
from nltk import *
from nltk.corpus import PlaintextCorpusReader
from nltk.stem import *
import json
import operator
import couchdb
import ast
import httplib

urls = (
	'/', 'register',
	'/rev', 'revision',
	'/test', 'tester', 
    '/add',  'testAdd', 
    '/save', 'testSave',
    '/hello', 'hello')

app = web.application(urls, globals())
render = web.template.render('templates/')

myform = web.form.Form(web.form.Textarea('content', rows=10, cols=30))

couch = couchdb.Server()

class register:
    def GET(self):
        return render.register()

class testSave:
  def GET(self):
    i = web.input(userID=None, rawContent=None)
    userID = str(i.userID)
    rawContent = i.rawContent
    parsedContentDict = parseContent(rawContent)
    print parsedContentDict
    saveContent(userID, rawContent, parsedContentDict)


class testAdd:
  def GET(self):
    i = web.input(userID=None)
    userID = str(i.userID)
    addDbForUser(userID)

def addDbForUser(userID):
    db = couch.create(userID)
    #Add all the design documents
    path = "./couchdbviews/views"
    dirList=os.listdir(path)
    for fname in dirList:
       pathToFile = path + "/" + fname
       f = open(pathToFile, 'r')
       rawString = f.read()
       dictObj = ast.literal_eval(rawString)
       designDocId = str(dictObj['_id'])
       designDoc = json.dumps(dictObj)
       print designDoc
       relativePath = "/" + userID + "/" + designDocId
       print relativePath
       connection =  httplib.HTTPConnection('127.0.0.1:5984')
       connection.request('PUT',relativePath , designDoc)
       result = connection.getresponse()
       print result.__dict__

def saveContent(userID, rawContent, parsedContentDict):
    print "saving"
    db = couch[userID]
    parsedContentDict['rawText'] = rawContent
    doc = parsedContentDict
    db.save(doc)

    
def parseContent(content):
    tokens = WordPunctSpaceTokenizer().tokenize(content)
    finder = ParseBigramCollocationsAndWords(tokens)
    repetitions = DetectRepetitions(finder, tokens)
    stemmer = LancasterStemmer()
    wrds = []
    sentenceLengths = []
    stats = {}
    stats["label"] = ["frequency"]
    wordFreq = {}

    currentSentenceLength = 0
    index = 0
    for token in tokens:
        if token in ["!", ".", "?"]:
            sentenceLengths.append(currentSentenceLength)
            currentsentenceLength = 0
        elif token not in [",","-", ":", "'", '"']:
            currentSentenceLength += 1

        if token not in ['the','s','.',';',',',"'",":", "`","(",")", " "]:
            if token not in wordFreq:
                wordFreq[token] = 1
            else:
                wordFreq[token] += 1

        makeJson = {}
        makeJson['properties'] = {}
        makeJson['properties']['stem'] = stemmer.stem(token)
        makeJson['specialChar'] = False
        makeJson['properties']['repetitions'] = False
        if (token == '"'):
            makeJson['word'] = "\""
        elif ("""\r\n""" in token):
            makeJson = {}
            makeJson['word'] = "paragraphbreak"
            makeJson['specialChar'] = True
        elif index in repetitions:
            makeJson['word'] = token
            makeJson['properties']['repetitions'] = True
        elif (token == " "):
            makeJson['word'] = "space"
            makeJson['specialChar'] = True
        else:
            makeJson['word'] = token
        wrds.append(makeJson)
        index = index + 1

    sorted_x = sorted(wordFreq.iteritems(), key=operator.itemgetter(1))
    sorted_x.reverse()
    top5 = []
    max5 = len(sorted_x)
    if max5 >  5:
        max5 = 5
    for i in range(max5):
        top5.append(sorted_x[i])
    values = []
    for top in top5:
        dic = {"label" : top[0] ,"values" : [top[1]]}
        values.append(dic)
    stats["values"] = values
    returnval = json.dumps({"text" : wrds})
    return {"text": wrds , "statistics": stats}



class tester:
    def GET(self):
        contentList = []
        JSON1 = json.dumps({'word' : 'hello', 'properties' : {'stem': 'hello', 'repetition' : False}})
        JSON2 = json.dumps({'word' : 'world', 'properties' : {'stem': 'world', 'repetition' : False}})
        contentList.append(JSON1)
        contentList.append(JSON2)
        return render.edit(contentList)

class revision:
    def POST(self):
        i = web.input(text=None)
        content = i.text
        returnDict = parseContent(content)
        returnJson = json.dumps(returnDict)
        return returnJson

class hello:
    def GET(self):
        form = myform()
        return render.hello(form)

    def POST(self):
        form = myform()
        form.validates()
        content = form['content'].value
        returnDict = parseContent(content)
        returnJson = json.dumps(returnDict['text'])
        statistics = json.dumps(returnDict['statistics'])
        return render.edit(returnJson, statistics)




class WordPunctSpaceTokenizer(RegexpTokenizer):
    def __init__(self):
        RegexpTokenizer.__init__(self, r'\s+|\w+|[^\w\s]+',  discard_empty=False)

class ParseBigramCollocationsAndWords(BigramCollocationFinder):
    def __init__(cls, words, window_size=2):
        cls.PhrasesIndexes = {}
        cls.StemmedPhrasesIndexes = {}
        cls.breadth = 0
        wfd = FreqDist()
        bfd = FreqDist()
        stemmer = LancasterStemmer()
        if window_size < 2:
            raise ValueError, "Specify window_size at least 2"
        index = 0
        for window in nltk.util.ingrams(words, window_size, pad_right=True):
            w1 = window[0].lower()
            '''
            try:
                    window = window[:list(window).index(w1, 1)]
            except ValueError:
                    continue
            '''
            if index == 0:
                if not w1 in ['the','s','.',';',',',"'",":", "`","(",")", "`", '"', " " ]:
                    cls.PhrasesIndexes[w1] = [0]
                    cls.StemmedPhrasesIndexes[stemmer.stem(w1)] = [0]
            wfd.inc(w1)
            try:
                w2 = window[1]
            except ValueError:
                break
            if w2 is not None:
                w2 = w2.lower()
                if not cls.PhrasesIndexes.has_key(w2):
                    cls.PhrasesIndexes[w2] = [index + 1]
                else:
                    cls.PhrasesIndexes[w2].append(index + 1)

                stemmedw2 = stemmer.stem(w2)
                if not stemmedw2 in ['the','s','.',';',',',"'",":", "`","(",")", "`", '"', " "]:
                    if not cls.StemmedPhrasesIndexes.has_key(stemmedw2):
                        cls.StemmedPhrasesIndexes[stemmedw2] = [index + 1]
                    else:
                        cls.StemmedPhrasesIndexes[stemmedw2].append(index + 1)

                if not cls.PhrasesIndexes.has_key(w1 + " " + w2):
                    cls.PhrasesIndexes[w1 + " " + w2] = [index]
                    #cls.StemmedPhrasesIndexes[w1 + " " + w2] = [index]
                else:
                    cls.PhrasesIndexes[w1 + " " + w2].append(index)
                    #cls.StemmedPhrasesIndexes[w1 + " " + w2].append(index)
                bfd.inc((w1,w2))

            index = index + 1

        cls.breadth = len(cls.StemmedPhrasesIndexes)
        BigramCollocationFinder.__init__(cls, wfd, bfd)






def DetectRepetitions(finder, tokens):
	repetitions = []
	indexesofrepetitions = []
	for phrase in finder.StemmedPhrasesIndexes:
            if not phrase in ['the','s','.',';',',',"'",":", "`","(",")"] :
                phraseindexes = finder.StemmedPhrasesIndexes[phrase]
                if len(phraseindexes) > 1:
                    i = 1
                    while i < len(phraseindexes):
                        diff = phraseindexes[i] - phraseindexes[i - 1]
                        if diff < 250:
                            repetitions = repetitions +  [tokens[phraseindexes[i-1]] + " " +  tokens[phraseindexes[i]]]
                            if not phraseindexes[i-1] in indexesofrepetitions:
                                indexesofrepetitions = indexesofrepetitions + [phraseindexes[i - 1]]
                            if not phraseindexes[i] in indexesofrepetitions:
                                indexesofrepetitions = indexesofrepetitions + [phraseindexes[i]]
                        i = i + 1
	return indexesofrepetitions
if __name__ == "__main__":
#	main(sys.argv[1])
	app.run()
