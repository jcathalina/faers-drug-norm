from typing import Dict, Optional, List

import pandas as pd
import numpy as np

from alg.formatter import FaersDataRow
from mapping.rxnav import approx_match, RxNavResponse


class RxNormMapper:
    def __init__(self):
        self.thresh = 80
        self.nda_dict = self._load_nda_dict()
        self.international_dict = self._load_international_dict()  # TODO: Load dictionary that maps int. drug names to active ingredients

        # Analytics
        self.number_hq_mappings = 0
        self.successful_name_only_calls = 0
        self.successful_default_calls = 0
        self.successful_backup_calls = 0



    def map_to_rxnorm(self, data_row: "FaersDataRow", include_international=True) -> None:
        """
        Optimizes the data found in FAERS drug tables into formats that are convenient for RxNav's approximate matching
        algorithm to increase the odds of confidently mapping drug entries to RXCUIs.
        :param include_international:
        :param data_row:
        """

        tries_exhausted = False

        while not tries_exhausted:  # TODO: Make a list of functions and loop through that to make code shorter.

            response: RxNavResponse = self.try_mapping_nda_num(data=data_row)
            if response.success:
                print(response)
                break

            response = self.try_mapping_only_drug_name(data=data_row)
            if response.success:
                self.successful_name_only_calls += 1
                print(response)
                break

            response = self.try_mapping_default_query(data=data_row)
            if response.success:
                self.successful_default_calls += 1
                print(response)
                break

            response = self.try_mapping_backup_query(data=data_row)
            if response.success:
                self.successful_backup_calls += 1
                print(response)
                break

            if include_international:
                response = self.try_mapping_with_international_data(data=data_row)
                # TODO: The international mapper has to fuzzy match against the EU dict to find the closest match or direct matching?
                if response.success:
                    print(response)
                    break

            print("No high-confidence mapping found... ")
            tries_exhausted = True

        # if we receive a low confidence score
        # if res.candidates[0].score <= self.thresh:


    def try_mapping_nda_num(self, data) -> "RxNavResponse":
        if data.nda_num:  # if an nda_num is present, check it against the dictionary first.
            trade_name: "Optional[str]" = self.nda_dict.get(data.nda_num, None)
            if trade_name is None:
                return RxNavResponse("", [])  # Just return an empty default RxNavResponse to not waste time on this process.
            return approx_match(query=trade_name)

    @staticmethod
    def _load_nda_dict(path: str) -> Dict:
        print("Loading NDA dictionary...")
        nda_df = pd.read_csv(path, header=None)
        return {nda_df["nda_num"]: nda_df["trade_name"]}
