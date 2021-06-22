import scispacy
import spacy
import en_core_sci_scibert

from spacy import displacy
from scispacy.abbreviation import AbbreviationDetector
from scispacy.umls_linking import UmlsEntityLinker

nlp = spacy.load("en_core_sci_scibert")

text = "XYREM (SOLUTION OXYBATE) ORAL SOLUTION, 500MG/ML"

doc = nlp(text)
print(list(doc.sents))
print(doc.ents)

#  Hard cleaning rules:
#  \/([0-9]*)\/ --> Regex for removing stuff like DRUGNAME   /000123213/, occurs a lot!
#  long entries > 50 chars
#  too much data between parentheses
#  noisy punct
#  drug mentioned multiple times
#  generic non-descript names