"""
Pipeline that takes in a row of faers data from a database and transforms it into an entry
that is optimized for RxNav's normalization algorithm.
"""
from dataclasses import dataclass
from typing import Optional, Dict

import pandas as pd
from fuzzywuzzy import process


@dataclass
class Identifier:
    """Class that contains information to link back to the original FAERS DB"""
    primary_id: str
    case_id: str
    drug_seq: str


class FaersDataRow:  # TODO: Think of a better name for this
    """Class for creating and handling a RxNav query along with its metadata to link it back to the original FAERS DB"""
    def __init__(self, data: pd.Series):
        self.drug_name_entry: str = data["drugname"]
        self.query: str = self._create_query(data=data)
        self.identifier = Identifier(primary_id=data["primaryid"], case_id=data["caseid"], drug_seq=data["drug_seq"])
        self.nda_num: "Optional[str]" = data["nda_num"]
        self.role_code: str = data["role_cod"]
        self.backup_query: "Optional[str]" = self._create_backup_query(data=data)
        # self.int_mapped_query: "Optional[str]" = self.get_int_mapped_active_ingredient()


    @staticmethod
    def _create_query(data: pd.Series) -> str:
        """
        :param data: a row extracted from a pandas dataframe containing FAERS data
        :return: a query that's optimized (given the available info) for RxNav's approximate matching algorithm
        """
        components = ["drugname", "route", "dose_amt", "dose_unit", "dose_form"]  # Note: (rarely) drugname can be null!
        query = " ".join([str(data[c]) for c in components])
        return query.replace("nan", "").rstrip()  # remove all nans from string and strip trailing whitespace.


    @staticmethod
    def _create_backup_query(data: pd.Series) -> "Optional[str]":
        """
        This method is only a fallback as active ingredient is often missing from FAERS data entries.
        However, sometimes more information is contained in these columns that can be helpful for the mapping
        of these cases.
        :param data: a row extracted from a pandas dataframe containing FAERS data
        :return: a query that uses the active ingredient instead of the drugname
                 for RxNav's approximate matching algorithm.
        """
        # No need to continue with this method if there's no prod_ai
        if data["prod_ai"] == "nan":
            return
        components = ["prod_ai", "route", "dose_amt", "dose_unit", "dose_form"]
        query = " ".join([str(data[c]) for c in components])
        return query.replace("nan", "").rstrip()  # remove all nans from string and strip trailing whitespace.


    @staticmethod
    def get_int_mapped_query(data: pd.Series, international_dict: "Dict[str, str]", fuzzy_search=True) -> "Optional[str]":
        """
        :return:
        """
        drug_name = data["drug_name"]
        components = ["route", "dose_amt", "dose_unit", "dose_form"]

        if fuzzy_search:
            choices = [*international_dict]  # unpack dict keys to list for fuzzy matching
            match = process.extractOne(drug_name, choices=choices, score_cutoff=90)
            if match is None:
                return
            active_ingredient = international_dict.get(match)
            return f"{active_ingredient} {' '.join([str(data[c]) for c in components])}"

        direct_match = international_dict.get(drug_name, None)
        return f"{direct_match} {' '.join([str(data[c]) for c in components])}"


    def get_int_mapped_active_ingredient(self, international_dict: "Dict[str, str]", fuzzy_search=True) -> "Optional[str]":
        # TODO: This can be a helper method for int mapped query to refactor code
        """
        :param international_dict:
        :param fuzzy_search:
        :return:
        """
        drug_name = self.drug_name_entry
        if fuzzy_search:
            choices = [*international_dict]  # unpack dict keys to list for fuzzy matching
            match = process.extractOne(drug_name, choices=choices, score_cutoff=90)
            if match is None:
                return
            active_ingredient = international_dict.get(match)
            return active_ingredient
        return international_dict.get(drug_name, None)
