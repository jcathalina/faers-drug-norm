from typing import Dict, Optional, List
from enum import Enum

import pandas as pd
import numpy as np

from alg.formatter import FaersDataRow
from alg.rxnav import approx_match, RxNavResponse


class RxNormMapper:
    def __init__(self, config: "Dict[str, str]"):
        self.thresh = 80
        self.nda_dict = self._load_nda_dict(path=config["nda_path"])
        self.international_dict = self._load_international_dict(
            path=config["int_path"])  # TODO: Load dictionary that maps int. drug names to active ingredients

        # Analytics
        self.number_hq_mappings = 0
        self.successful_name_only_calls = 0
        self.successful_default_calls = 0
        self.successful_backup_calls = 0
        self.unmappable: "List[FaersDataRow]" = []  # TODO: Maybe I should just yield an unmappable and log it instead of keeping the list in mem

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
            self.unmappable.append(data_row)
            tries_exhausted = True

    def try_mapping_nda_num(self, data: "FaersDataRow") -> "RxNavResponse":
        if data.nda_num:  # if an nda_num is present, check it against the dictionary first.
            trade_name: "Optional[str]" = self.nda_dict.get(data.nda_num, None)
            if trade_name is None:
                return RxNavResponse("",
                                     [])  # Just return an empty default RxNavResponse to not waste time on this process.
            return approx_match(query=trade_name)

    def try_mapping_only_drug_name(self, data: "FaersDataRow") -> "RxNavResponse":
        return approx_match(query=data.drug_name_entry)

    def try_mapping_default_query(self, data: "FaersDataRow") -> "RxNavResponse":
        return approx_match(query=data.query)

    def try_mapping_backup_query(self, data: "FaersDataRow") -> "RxNavResponse":
        return approx_match(query=data.backup_query)

    def try_mapping_with_international_data(self, data: "FaersDataRow") -> "RxNavResponse":
        raise NotImplementedError

    @staticmethod
    def _load_nda_dict(path: str) -> "Dict[str, str]":
        print("Loading NDA dictionary...")
        nda_df: "pd.DataFrame" = pd.read_csv(path)

        return {d["nda_num"]: d["trade_name"] for d in nda_df.to_dict(orient="records")}

    @staticmethod
    def _load_international_dict(path: str) -> "Dict[str, str]":
        print("Loading international dictionary...")
        int_df: pd.DataFrame = pd.read_csv(path)

        return {d["drug_name"]: d["prod_ai"] for d in int_df.to_dict(orient="records")}





def load_faers_data(config: "Dict[str, str]", file_to_use: str) -> "pd.DataFrame":
    """
    :param config:
    :param file_to_use: "dev", "faers", "aers", "full"
    :return:
    """
    relevant_cols = ["primaryid", "caseid", "drug_seq", "role_cod", "drugname", "val_vbm", "route", "dose_vbm",
                     "nda_num",
                     "dose_amt", "dose_unit", "dose_form", "origin", "prod_ai"]

    if file_to_use == "dev":
        filepath = config["dev_path"]
    elif file_to_use == "faers":
        filepath = config["faers_path"]
    elif file_to_use == "aers":
        filepath = config["aers_path"]
    elif file_to_use == "full":
        filepath = config["full_path"]
    else:
        raise KeyError(f"the option {file_to_use} does not exist, please choose from dev, faers, aers, full")

    f_data: pd.DataFrame = pd.read_csv(filepath_or_buffer=filepath,
                                       nrows=config["n_rows"],
                                       usecols=relevant_cols)
    f_data.update(f_data.select_dtypes(include=np.number).applymap(
        '{:,g}'.format))  # cast dosage values to int formatting if applicable

    return f_data


if __name__ == "__main__":

    mapper_configuration = {
        "nda_path": "C:/_msc/faers-drug-norm/data/dictionaries/nda_dict.csv",
        "int_path": "C:/_msc/faers-drug-norm/data/dictionaries/eu_brand_names_list.csv",
    }

    faers_data = load_faers_data()
    mapper = RxNormMapper(config=mapper_configuration)

    for _, row in faers_data.iterrows():
        data = FaersDataRow(data=row)
        print(data)
        res = approx_match(query=data.query)
        print(res)
