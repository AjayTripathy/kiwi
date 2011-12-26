import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords

def getSenseSimilarity(worda,wordb):
  wordasynsets = wn.synsets(worda)
  wordbsynsets = wn.synsets(wordb)
  
  synsetnamea = [wn.synset(str(syns.name)) for syns in wordasynsets]
  synsetnameb = [wn.synset(str(syns.name)) for syns in wordbsynsets]

  maxpathsim = 0
  for sseta, ssetb in [(sseta,ssetb) for sseta in synsetnamea for ssetb in synsetnameb]:
    pathsim = sseta.path_similarity(ssetb)
    if pathsim > maxpathsim:
        maxpathsim = pathsim

  return maxpathsim

def getSentenceSimilarity(senta, sentb):
  wordsa = nltk.tokenize.word_tokenize(senta)
  wordsb = nltk.tokenize.word_tokenize(sentb)
  sentsim = 0
  stwords = stopwords.words('english')
  for word in wordsa:
    if word in stwords:
      wordsa.remove(word)
  
  for word in wordsb:
    if word in stwords:
      wordsb.remove(word)

  for worda in wordsa:
    for wordb in wordsb:
      sentsim = sentsim + getSenseSimilarity(worda, wordb)
  try:
    return sentsim / (len(wordsa) + len(wordsb))
  except:
    return 0.0

def getPassageSimilarity(text):
  sentences = nltk.tokenize.sent_tokenize(text)
  sentenceRange = range(len(sentences))
  passageSimilarity = 0
  for i in sentenceRange:
    if (i+1 in sentenceRange):
      passageSimilarity = passageSimilarity + getSentenceSimilarity(sentences[i], sentences[i+1])

  if len(sentences) > 1:
    return float(passageSimilarity) / float(len(sentences) - 1)
  else:
    return 1.0    
