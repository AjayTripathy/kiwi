import sys
import web
from web import form
import nltk
from nltk import *
from nltk.corpus import PlaintextCorpusReader
from nltk.stem import *

def make_text(string):
	return string


urls = (
	'/', 'hello')

app = web.application(urls, globals())
render = web.template.render('templates/')

myform = web.form.Form(
                web.form.Textarea('content', rows=50, cols=80),
                )


class firstrev:
	def POST(self, text):
		tokens = WordPunctTokenizer().tokenize(text)
		

class hello: 
	def GET(self):
		form = myform()
		return render.hello(form)
	
	def POST(self):
		form = myform()
		form.validates()
		content = form['content'].value
		tokens = WordPunctTokenizer().tokenize(content)
		finder = ParseBigramCollocationsAndWords(tokens)
		repetitions = DetectRepetitions(finder, tokens)
		stemmer = LancasterStemmer()
		#return make_text(content)
		#return repetitions
		returnhtml = """<head>
<title>Your writing is improving!</title>
<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.2.6/jquery.min.js"></script>
<script type="text/javascript" src="/static/jquery.editable-1.3.3.min.js"></script>
<script type="text/javascript">
$(document).ready(function() {

$("span").css({'font-weight':'bold'});

var enter = function()
                {
			var classname = this.className
			$("." + classname).css({color:'red'});
                }

var leave = function()
		{
			var classname = this.className
			$("." + classname).css({color:'black'});
		}



$("span").hover(enter, leave)

$("span").editable()

});


</script>

</head>
<body>
<h1>Bolded Possible Repetitions</h1>
<p>"""
		index = 0
		for token in tokens:
			if index in repetitions:
				print "rep here %d" %(index)
				stemmedtoken = stemmer.stem(token)
				returnhtml = returnhtml +("""<span id="repetition" class="%s"> %s </span>""" %(stemmedtoken , token))
			else: 
				returnhtml = returnhtml + token + " " 
			index = index + 1
		
		return returnhtml + """</p>
</body>
</html>"""



class ParseBigramCollocationsAndWords(BigramCollocationFinder):
	def __init__(cls, words, window_size=2):
		cls.PhrasesIndexes = {}
		cls.StemmedPhrasesIndexes = {}
		wfd = FreqDist()
		bfd = FreqDist()
		stemmer = LancasterStemmer()
		if window_size < 2:
			raise ValueError, "Specify window_size at least 2"
		index = 0
		for window in nltk.util.ingrams(words, window_size, pad_right=True):
			print window
			w1 = window[0].lower()
			'''
			try:
				window = window[:list(window).index(w1, 1)]
			except ValueError:
				continue	
			'''
			if index == 0:
				if not w1 in ['the','s','.',';',',',"'",":", "`","(",")", "`"]:
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
				if not stemmedw2 in ['the','s','.',';',',',"'",":", "`","(",")", "`"]:
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
		BigramCollocationFinder.__init__(cls, wfd, bfd)			






def DetectRepetitions(finder, tokens):
	repetitions = []
	indexesofrepetitions = []
	print len(finder.StemmedPhrasesIndexes)
	for phrase in finder.StemmedPhrasesIndexes:
                if  not phrase in ['the','s','.',';',',',"'",":", "`","(",")"] :
                        phraseindexes = finder.StemmedPhrasesIndexes[phrase]
                        if len(phraseindexes) > 1:
                                i = 1
                                while i < len(phraseindexes):
                                        diff = phraseindexes[i] - phraseindexes[i - 1]
                                        if diff < 100:
                                                repetitions = repetitions +  [tokens[phraseindexes[i-1]] + " " +  tokens[phraseindexes[i]]]
						if not phraseindexes[i-1] in indexesofrepetitions:
							indexesofrepetitions = indexesofrepetitions + [phraseindexes[i - 1]]
						if not phraseindexes[i] in indexesofrepetitions:
							indexesofrepetitions = indexesofrepetitions + [phraseindexes[i]]
                                        i = i + 1
	print repetitions
	return indexesofrepetitions			
'''
def main(argv):
	corpus_root = './'
	wordlists = PlaintextCorpusReader(corpus_root, '.*')
	text = Text(wordlists.words(argv))
	finder = ParseBigramCollocationsAndWords(text.tokens)
	bigram_measures = BigramAssocMeasures() 
	collocations = finder.nbest(bigram_measures.likelihood_ratio, 20)
	colloc_strings = [w1+' '+w2 for w1, w2 in collocations]
	print colloc_strings
	stemmer = LancasterStemmer()
	repetitions = detectrepetitions(finder, text)
	print repetitions

	for phrase in finder.StemmedPhrasesIndexes:
		if  not phrase in ['the','s','.',';',',',"'",":", "`","(",")"] : 
			phraseindexes = finder.StemmedPhrasesIndexes[phrase]
			if len(phraseindexes) > 1:
				i = 1
				while i < len(phraseindexes):
					diff = phraseindexes[i] - phraseindexes[i - 1]
					if diff < 100:
						print text.tokens[phraseindexes[i-1]] + " " +  text.tokens[phraseindexes[i]] + "\n"
					i = i + 1	
'''						
if __name__ == "__main__":
#	main(sys.argv[1])
	app.run()
