#!/usr/bin/python

import sys
import web
from web import form
import nltk
from nltk import *
from nltk.corpus import PlaintextCorpusReader
from nltk.stem import *
from nltk.corpus import cmudict
from re import match
import json
import operator
import couchdb
import ast
import httplib

urls = (
    '/', 'register',
    '/start', 'hello',
    '/rev', 'revision',
    '/save', 'save',
    '/register', 'register',
    '/login', 'login',
    '/verify', 'verify',
    '/getAllDocs', 'getDocs',
    '/load' , 'load',
    '/render', 'renderPage'
    )



app = web.application(urls, globals())
render = web.template.render('templates/')

myform = web.form.Form(web.form.Textarea('content', rows=10, cols=30))

couch = couchdb.Server()
cmu = cmudict.dict()

store = web.session.DiskStore('sessions')
session = web.session.Session(app, store, initializer= {'loggedin' : 'false'})

##Here is the Users database. It holds usernames along with (hashed) passwords.
##Knowing whether or not they're logged in is done through cookies and isAuth.

usersDB = None
if ('users' not in couch):
    usersDB = couch.create('users')
else:
    usersDB = couch['users']



#returns True if you are authorized and False if you are not. I swear, this is secure. :<
#It is, it's not as though you can access isAuth client-side
def isAuth(user, token):
    if user not in usersDB:
        print "user wasn't actually in database"
        return False
    else:
        if (token == usersDB[user]['hashedPassword']):
            print "token matched"
            return True
        else:
            print "token failed"
            return False

class verify:
    def POST(self):
        i = web.input()
        username = str(i.username).lower()
        token = str(i.token)
        if (isAuth(username, token)):
            return "verified"
        else:
            return "not verified"

class save:
    def POST(self):
      i = web.input()
      userID = str(i.username).lower()
      password = str(i.password)
      title = str(i.title)
      rawText = str(i.text)
      if ( isAuth(userID, password) ):
        saveContent(userID, title, rawText, parseContent(rawText))
        return 'success'
      else:
        return 'failure'

class load:
   def POST(self):
     i = web.input()
     userID = str(i.username).lower()
     password = str(i.password)
     title = str(i.title)
     if ( isAuth(userID, password) ):
       content = loadContent(userID, title)
       return json.dumps(content)
     else:
       return 'failure'

class getDocs:
   def POST(self):
     i = web.input()
     userID = str(i.username).lower()
     password = str(i.password)
     if (isAuth(userID, password)):
       titles = docNames(userID)
       return json.dumps(titles)
     else:
       return 'failure'

class register:
    def GET(self):
        return render.register(usersDB)

    def POST(self):
        print web.input()
        i = web.input()
        userID = str(i.username).lower()
        password = str(i.password)

        if userID in usersDB:
            return 'already exists'
        else:
            usersDB[userID] = {'name' : userID, 'hashedPassword' : password}
            addDbForUser(userID)
            return 'woo yeah'
        return 'wat'

class login:
    def POST(self):
        print web.input()
        i = web.input()
        userID = str(i.username).lower()
        password = str(i.password)

        if userID in usersDB:
            if usersDB[userID]['hashedPassword'] == password:
                return 'great'
            else:
                return 'no match'
        else:
            print "username not in DB"
            return 'no match'

        return 'watlol'

class renderPage:
  def POST(self):
    i = web.input()
    form = myform()
    form.validates()
    returnDict = str(i.parsedText)
    print "ok"
    returnDict = json.loads(returnDict)
    returnJson = json.dumps(returnDict['text'])
    statistics = json.dumps(returnDict['statistics'])
    return render.edit(returnJson, statistics)

class testAdd:
  def GET(self):
    i = web.input(userID=None)
    userID = str(i.userID)
    addDbForUser(userID)

def addDbForUser(userID):
    userID = "user_" + userID
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

def saveContent(userID, title, rawContent, parsedContentDict):
    print "saving"
    userID = "user_" + userID
    db = couch[userID]
    doc = { }
    doc['rawText'] = rawContent
    doc['parsedContent'] = parsedContentDict
    db[title] = doc

def loadContent(userID, title):
   userID = "user_" + userID
   db = couch[userID]
   doc = db[title]
   return doc

def docNames(userID):
   userID = 'user_' + userID
   db = couch[userID]
   docs = []
   for title in db:
     if not (title[:8] == '_design/' ):
       docs.append( {'title' : title} )
   return docs

def parseContent(content):
    tokens = WordPunctSpaceTokenizer().tokenize(content)
    finder = ParseBigramCollocationsAndWords(tokens)
    repetitions = DetectRepetitions(finder, tokens)
    stemmer = LancasterStemmer()
    wrds = []
    stats = {}
    sentenceLengths = []
    topWords = {}
    topWords["label"] = ["frequency"]
    wordFreq = {}
    totalSyllables = 0
    totalWords = 0

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

        if token not in ['.',';',',',"'",":", "`","(",")", " "]:
          totalSyllables = totalSyllables + syllableCount(token)
          totalWords = totalWords + 1

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

    gradeLevel = FleshKincaid(totalWords, len(sentenceLengths), totalSyllables)
    print gradeLevel
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
    topWords["values"] = values
    returnval = json.dumps({"text" : wrds})
    stats['topWords'] = topWords
    stats['gradeLevel'] = {'gradeLevel' : gradeLevel}
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

def FleshKincaid(totalWords, totalSentences, totalSyllables):
  if ( (not (totalWords == 0)) and (not (totalSentences == 0)) ):
    return int(0.39 * (totalWords / totalSentences) + 11.8 * (totalSyllables / totalWords) - 15.59)
  else:
    return 0

def syllableCount(word):
  reduced = reduce(word)
  if (not len(reduced)) or (not reduced in cmu):
    return manual_syllable_count(reduced)
  return len([x for x in list(''.join(list(cmu[reduced])[-1])) if match(r'\d', x)])

def manual_syllable_count(word):
  count = 0
  prev = None
  vowels = ['a', 'e', 'i', 'o', 'u']
  for letter in word:
    if ((prev not in vowels) and (letter in vowels)):
      count = count + 1
    prev = letter
  return count

def reduce(word):
  return ''.join([x for x in word.lower() if match(r'\w', x)])



if __name__ == "__main__":
#	main(sys.argv[1])
	app.run()
