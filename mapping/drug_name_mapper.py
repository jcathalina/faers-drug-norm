from typing import List
from collections import defaultdict
from random import randint
from tqdm import tqdm

from .drug_info import DrugInfo
from .rxnav import approx_match, RxNavResponse
import pandas as pd

import re

MATCH_THRESHOLD = 90


# TODO: I should probably update this class to NOT mutate instances of DrugInfo (except mapping)
# TODO: Only read data from them and manipulate from there
class DrugNameMapper:
    def __init__(self, regex_objects_for_drug_name: List[re.Pattern],
                 regex_objects_for_active_ingredient: List[re.Pattern],
                 nda_filepath: str,
                 match_type: str = "approx") -> None:
        self.regex_objects_dn = regex_objects_for_drug_name
        self.regex_objects_ai = regex_objects_for_active_ingredient  # TODO: Active Ingredient regex patterns from Banda et al. 2016
        self.nda_table = self._generate_nda_table(path_to_nda_dict=nda_filepath)  # HashMap<nda_num, name>
        self.hash_table = defaultdict(int)  # HashMap<drug_name, rxcui>
        self.match_type = match_type

    def _hash_exists(self, drug_name: str) -> bool:
        return drug_name in self.hash_table  # check if we already processed this entry before

    def check_hash(self, info: DrugInfo) -> DrugInfo:
        if self._hash_exists(info.drug_name):
            info.mapping = self.hash_table[info.drug_name]
        return info

    def clean_drug_name(self, info: DrugInfo) -> DrugInfo:
        clean_name = info.drug_name
        for match in self.regex_objects_dn:
            clean_name = re.sub(pattern=match, repl='', string=clean_name)
        info.drug_name = clean_name.strip()

        # start unoptimized part
        # TODO: Not sure if the hash check is necessary here as the outer loop starts with one
        info = self.check_hash(info)
        if info.mapping is not None:
            return info  # return early with mapping if hash is found
        possible_rxcui: int = self.rxnav_lookup(info.drug_name)
        if possible_rxcui:
            info.mapping = possible_rxcui
            self.hash_table[info.drug_name] = possible_rxcui
        return info
        # end unoptimized part

    def clean_active_ingredient(self, info: DrugInfo) -> DrugInfo:
        # active ingredient field can be empty, handle this edge case
        clean_name: str = info.active_ingredient
        if not isinstance(clean_name, str):
            return info

        for match in self.regex_objects_ai:
            clean_name = re.sub(pattern=match, repl='', string=clean_name)
        clean_name = clean_name.strip()

        # sometimes the active ingredient can be mapped to an rxcui rather than the drug name entry
        possible_rxcui: int = self.rxnav_lookup(clean_name)
        if possible_rxcui:
            info.mapping = possible_rxcui
            self.hash_table[info.drug_name] = possible_rxcui

        return info

    def lookup_nda_number(self, info: DrugInfo) -> DrugInfo:
        nda = info.nda_number
        if nda not in self.nda_table or nda != type(int):
            return info  # if the nda number is invalid, return early

        found_name: str = self.nda_table[nda]
        possible_rxcui: int = self.rxnav_lookup(found_name)
        if possible_rxcui:
            info.mapping = possible_rxcui
        return info


    @staticmethod
    def rxnav_lookup(drug_name: str) -> int:
        possible_match: RxNavResponse = approx_match(drug_name)
        match_score: int = possible_match.candidates[0].score

        if match_score >= MATCH_THRESHOLD:
            rxcui: int = possible_match.candidates[0].rxcui
            return rxcui

    @staticmethod
    # FIXME: Figure out best way to just test if endpoint is available
    def _rxnav_is_running() -> bool:
        import urllib.request

        test_url = "http://localhost:4000//REST/approximateTerm.json?term=CARBOPLATIN&maxEntries=1"
        return urllib.request.urlopen(test_url).getcode() == 200

    @staticmethod
    def _generate_nda_table(path_to_nda_dict: str):
        df_nda: pd.DataFrame = pd.read_csv(filepath_or_buffer=path_to_nda_dict,
                                           usecols=["nda_num", "trade_name"])

        nda_table: dict = df_nda.set_index("nda_num").to_dict()["trade_name"]
        return nda_table

    @staticmethod
    def get_drug_info(path_to_drug_table: str):
        all_drug_info: List[DrugInfo] = []
        df_drug: pd.DataFrame = pd.read_csv(filepath_or_buffer=path_to_drug_table,
                                            low_memory=False,
                                            usecols=["primaryid", "caseid", "drug_seq",
                                                     "drugname", "prod_ai", "nda_num"])
        df_drug["nda_num"] = df_drug["nda_num"].astype("Int32",
                                                       errors='ignore')  # Use nullable ints or else we get floats and nans
        for info in df_drug.itertuples(name="FaersData"):
            prod_ai = info.prod_ai
            drugname = info.drugname

            if isinstance(prod_ai, str):  # TODO: use isinstance more instead of type()!!
                prod_ai = prod_ai.replace(',', '')

            if isinstance(drugname, str):
                drugname = drugname.replace(',', '')

            di = DrugInfo(primaryid=info.primaryid,
                          caseid=info.caseid,
                          drug_seq=info.drug_seq,
                          drug_name=drugname,
                          active_ingredient=prod_ai,
                          nda_number=info.nda_num)
            all_drug_info.append(di)
        return all_drug_info

    def run(self, drug_info_chunk: List[DrugInfo]):

        # Before anything, make sure rxnav is running locally with a simple test
        # assert mapping.rxnav_is_running(), "Please make sure you have a local rxnav instance running." \
        #                                   "For assistance on how to do this, consult the README"


        with open(file=f"output/mapping_test_{randint(0, 1_000)}.csv", mode="w", encoding="utf-8") as f:
            for info in tqdm(drug_info_chunk, leave=True, position=0):
                # First check if we have already encountered this entry (Step 0)
                x = self.check_hash(info)

                # After every step, check if mapping has been found
                # If so, write to file and skip to next entry
                if x.mapping is not None:
                    f.write(f"{x.__str__()}\n")
                    continue

                # Step 1: Clean drug name with Banda et al.'s regex method
                x = self.clean_drug_name(x)

                if x.mapping is not None:
                    f.write(f"{x.__str__()}\n")
                    continue

                # Step 2: Clean active ingredient with Banda et al.'s regex method
                # See if active ingredient contains the necessary information
                x = self.clean_active_ingredient(x)

                if x.mapping is not None:
                    f.write(f"{x.__str__()}\n")
                    continue

                # Step 3: If the previous steps yield nothing, check if there is an NDA number
                # If so, look it up in our dictionary and map the found name
                # If all else fails... TODO: Implement methods to deal with these edge cases
                x = self.lookup_nda_number(x)
                f.write(f"{x.__str__()}\n")
