import spacy
import json

from spacy.language import Language, Doc
from spacy.matcher import PhraseMatcher
from typing import *


@spacy.registry.misc("abbreviations.dict.rxnorm")
def create_rxnorm_abbreviations_dict() -> Dict[str, str]:
    with open(file="../data/dictionaries/abbreviations.json", mode="r", encoding="utf-8") as f:
        abbreviations: Dict[str, str] = json.load(f)
    return abbreviations


@Language.factory("abbreviations", default_config={"abbreviations": {"@misc": "abbreviations.dict.rxnorm"},
                                                   "case_sensitive": False})
def create_abbreviation_component(nlp: Language, name: str, abbreviations: Dict[str, str], case_sensitive: bool):
    return AbbreviationComponent(nlp=nlp, abbreviations=abbreviations, case_sensitive=case_sensitive)


class AbbreviationComponent:
    def __init__(self, nlp: Language, abbreviations: Dict[str, str], case_sensitive: bool):
        matcher_attr = "TEXT" if case_sensitive else "LOWER"
        self.matcher = PhraseMatcher(nlp.vocab, attr=matcher_attr)
        self.matcher.add("ABBREVIATIONS", [nlp.make_doc(abb) for abb in abbreviations])
        self.abbreviations = abbreviations
        self.case_sensitive = case_sensitive

        if not Doc.has_extension("abbreviations"):
            Doc.set_extension("abbreviations", default=[])

    def __call__(self, doc: Doc) -> Doc:

        for _, start, end in self.matcher(doc):
            span = doc[start:end]
            abbreviation = self.abbreviations.get(span.text if self.case_sensitive else span.text.lower())
            doc._.abbreviations.append((span, abbreviation))

        return doc


spacy.prefer_gpu()
# nlp = spacy.load("en_core_web_sm")
nlp = spacy.blank("en")
nlp.add_pipe("abbreviations", config={"case_sensitive": False})

# doc = nlp("acet 200 mg tablet")
# print(doc._.abbreviations)

import pandas as pd

# a = pd.read_csv("../data/processed/drug_table_clean.csv", usecols=["drugname", "prod_ai"], nrows=10000, dtype="object")
# a = a["drugname"].to_list()
a = ["INJ MG HCL something tablet"]

for x in a:
    doc = nlp(x)
    # print(f"Doc: {doc}, Abbr: {doc._.abbreviations}")
    print(doc)