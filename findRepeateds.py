import sys
import nltk
from nltk import *
from nltk.corpus import PlaintextCorpusReader
from nltk.stem import *

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
			w1 = window[0].lower()
			try:
				window = window[:list(window).index(w1, 1)] 
			except ValueError:
				pass
			if index == 0:
				if not w1 in ['the','s','.',';',',',"'",":", "`","(",")", "`"]:
					cls.PhrasesIndexes[w1] = [0] 
					cls.StemmedPhrasesIndexes[stemmer.stem(w1)] = [0]
			wfd.inc(w1)
			for w2 in set(window[1:]):
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
						
if __name__ == "__main__":
	main(sys.argv[1])
