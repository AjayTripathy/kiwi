import nltk
from nltk import tokenize
from nltk.stem import *

class coherenceTable:

  def __init__(self, inputText):
    self.sentences = nltk.tokenize.sent_tokenize(inputText)
    sentenceIndex = 0
    self.coherenceTable = {}
    self.densityTable = {}
    for sentence in self.sentences:
      text = nltk.word_tokenize(sentence)
      taggedtxt = nltk.pos_tag(text)
      for tup in taggedtxt:
        if ( (tup[1] == 'NN') or (tup[1] == 'PRP') ):
          if (tup[0] in self.coherenceTable):
            if not (self.coherenceTable[-1] == sentenceIndex):
              self.densityTable[tup[0]].append(sentenceIndex)
              diff = sentenceIndex - self.coherenceTable[tup[0]][-1]
              for i in range(diff - 1):
                self.coherenceTable[tup[0]].append('X')
              self.coherenceTable[tup[0]].append(sentenceIndex)
          else:
            self.densityTable = [sentenceIndex]
            self.coherenceTable[tup[0]] = []
            for i in range(sentenceIndex - 1):
              self.coherenceTable[tup[0]].append('X')
            self.coherenceTable[tup[0]].append(sentenceIndex)
        print self.coherenceTable
      sentenceIndex = sentenceIndex + 1
    for word in self.coherenceTable:
      diff = sentenceIndex - self.coherenceTable[tup[0]][-1]
      for i in range(diff - 1):
        self.coherenceTable[tup[0]].append('X')

    
  def getColumnDensity(self, word):
    column = self.densityTable[word]
    density =float(len(column)) / float(len(self.sentences))
    return density
 
  def getColumnDensities():
    densities = []
    for word in self.coherenceTable:
      densities.append(self.getColumnDensity(word))
    return densities
