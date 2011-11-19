import sys
import web
from web import form
import nltk
from nltk import *
from nltk.corpus import PlaintextCorpusReader
from nltk.stem import *
import json
import operator


def make_text(string):
	return string

urls = (
	'/', 'hello',
	'/rev', 'revision',
	'/test', 'tester')

app = web.application(urls, globals())
render = web.template.render('templates/')

myform = web.form.Form(web.form.Textarea('content', rows=40, cols=80))

class tester:
	def GET(self):
		contentList = []
		JSON1 = json.dumps({'word' : 'hello', 'properties' : {'stem': 'hello', 'repetition' : False}})
		JSON2 = json.dumps({'word' : 'world', 'properties' : {'stem': 'world', 'repetition' : False}})
		contentList.append(JSON1)
		contentList.append(JSON2)
		
		return render.edit(contentList)

class firstrev:
	def POST(self):
		i =  web.input(text=None)
		text = i.text
		print text
		tokens = WordPunctTokenizer().tokenize(text)
		stemmer = LancasterStemmer()
		wrds = []
		index = 0
		for token in tokens:
			if (token == '"'):
				returnhtml = returnhtml + "\"" +  " " #a hack, fix this on serverside
				makeJson = {}
				makeJson['word'] = "\""
				makeJson['properties'] = {}
				makeJson['properties']['stem'] = stemmer.stem(token)
				makeJson['properties']['repetitions'] = False
				makeJson['specialChar'] = False
				wrds.append(makeJson)
			elif ("""\r\n""" in token):
				makeJson = {}
				makeJson['word'] = "paragraphbreak"
				makeJson['properties'] = {}
				makeJson['properties']['stem'] = stemmer.stem(token)
				makeJson['properties']['repetitions'] = False
				makeJson['specialChar'] = True
				wrds.append(makeJson)
			elif (token == " "):
				makeJson = {}
				makeJson['word'] = "space"
				makeJson['properties'] = {}
				makeJson['properties']['stem'] = stemmer.stem(token)
				makeJson['properties']['repetitions'] = False
				makeJson['specialChar'] = True
				wrds.append(makeJson)
			else:
				#returnhtml = returnhtml + token + " " 
				makeJson = {}
				makeJson['word'] = token
				makeJson['properties'] = {}
				makeJson['properties']['stem'] = stemmer.stem(token)
				makeJson['properties']['repetitions'] = False
				makeJson['specialChar'] = False
				wrds.append(makeJson)
			index = index + 1
		returnJson = json.dumps(wrds)
		return returnJson
class revision:
	def POST(self):
		i = web.input(text=None)
		content = i.text
		tokens = WordPunctSpaceTokenizer().tokenize(content)
		finder = ParseBigramCollocationsAndWords(tokens)
		repetitions = DetectRepetitions(finder, tokens)
		stemmer = LancasterStemmer()
		wrds = []

		sentenceLengths = []
		rJson = {}
		rJson["label"] = ["frequency"]
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
				 
				
			if (token == '"'):
				returnhtml = returnhtml + "\"" +  " " #a hack, fix this on serverside
				makeJson = {}
				makeJson['word'] = "\""
				makeJson['properties'] = {}
				makeJson['properties']['stem'] = stemmer.stem(token)
				makeJson['properties']['repetitions'] = False
				makeJson['specialChar'] = False
				wrds.append(makeJson)
			elif ("""\r\n""" in token):
				makeJson = {}
				makeJson['word'] = "paragraphbreak"
				makeJson['properties'] = {}
				makeJson['properties']['stem'] = stemmer.stem(token)
				makeJson['properties']['repetitions'] = False
				makeJson['specialChar'] = True
				wrds.append(makeJson)
			elif index in repetitions:
				makeJson = {}
				makeJson['word'] = token
				makeJson['properties'] = {}
				makeJson['properties']['stem'] = stemmer.stem(token)
				makeJson['properties']['repetitions'] = True
				makeJson['specialChar'] = False
				wrds.append(makeJson)

			elif (token == " "):
				makeJson = {}
				makeJson['word'] = "space"
				makeJson['properties'] = {}
				makeJson['properties']['stem'] = stemmer.stem(token)
				makeJson['properties']['repetitions'] = False
				makeJson['specialChar'] = True
				wrds.append(makeJson)
			else: 
				#returnhtml = returnhtml + token + " " 
				makeJson = {}
				makeJson['word'] = token
				makeJson['properties'] = {}
				makeJson['properties']['stem'] = stemmer.stem(token)
				makeJson['properties']['repetitions'] = False
				makeJson['specialChar'] = False
				wrds.append(makeJson)

			index = index + 1
		returnJson = json.dumps(wrds)
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
		
		rJson["values"] = values
		statistics = json.dumps({"wordCount" : rJson})
		return render.edit(returnJson, statistics)
	
									
class hello: 
	def GET(self):
		form = myform()
		return render.hello(form)
	
	def POST(self):
		form = myform()
		form.validates()
		content = form['content'].value
		tokens = WordPunctSpaceTokenizer().tokenize(content)
		finder = ParseBigramCollocationsAndWords(tokens)
		repetitions = DetectRepetitions(finder, tokens)
		stemmer = LancasterStemmer()
		wrds = []

		sentenceLengths = []
		rJson = {}
		rJson["label"] = ["frequency"]
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
				 
				
			if (token == '"'):
				returnhtml = returnhtml + "\"" +  " " #a hack, fix this on serverside
				makeJson = {}
				makeJson['word'] = "\""
				makeJson['properties'] = {}
				makeJson['properties']['stem'] = stemmer.stem(token)
				makeJson['properties']['repetitions'] = False
				makeJson['specialChar'] = False
				wrds.append(makeJson)
			elif ("""\r\n""" in token):
				makeJson = {}
				makeJson['word'] = "paragraphbreak"
				makeJson['properties'] = {}
				makeJson['properties']['stem'] = stemmer.stem(token)
				makeJson['properties']['repetitions'] = False
				makeJson['specialChar'] = True
				wrds.append(makeJson)
			elif index in repetitions:
				makeJson = {}
				makeJson['word'] = token
				makeJson['properties'] = {}
				makeJson['properties']['stem'] = stemmer.stem(token)
				makeJson['properties']['repetitions'] = True
				makeJson['specialChar'] = False
				wrds.append(makeJson)

			elif (token == " "):
				makeJson = {}
				makeJson['word'] = "space"
				makeJson['properties'] = {}
				makeJson['properties']['stem'] = stemmer.stem(token)
				makeJson['properties']['repetitions'] = False
				makeJson['specialChar'] = True
				wrds.append(makeJson)
			else: 
				#returnhtml = returnhtml + token + " " 
				makeJson = {}
				makeJson['word'] = token
				makeJson['properties'] = {}
				makeJson['properties']['stem'] = stemmer.stem(token)
				makeJson['properties']['repetitions'] = False
				makeJson['specialChar'] = False
				wrds.append(makeJson)

			index = index + 1
		returnJson = json.dumps(wrds)
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
		
		rJson["values"] = values
		statistics = json.dumps({"wordCount" : rJson})
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
