import coherenceTable
import nltk
import sentenceComparison

def coherenceFeatures(text):
  table = coherenceTable.coherenceTable(text)
  features = { } 
  densities =  table.getColumnDensities()
  features['avgDensity'] = round( (sum(densities)/len(densities)) * 10 )
  features['semanticSimilarity'] = round(sentenceComparison.getPassageSimilarity(text) * 10) 
  return features  
   
