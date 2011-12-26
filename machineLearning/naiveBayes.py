import coherenceTable
import nltk
import sentenceComparison

def coherenceFeatures(text):
  table = coherenceTable.coherenceTable(text)
  features = { } 
  densities =  table.getColumnDensities()
  features['avgDensity'] = sum(densities)/len(densities)
  features['semanticSimilarity'] = sentenceComparison.getPassageSimilarity(text) 
  return features  
   
