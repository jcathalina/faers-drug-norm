from typing import Dict, Optional, Tuple

import pandas as pd
import numpy as np

from alg.formatter import FaersDataRow
from mapping.rxnav import approx_match, RxNavResponse


class RxNormMapper:
    def __init__(self):
        self.thresh = 80
        self.nda_dict = self._load_nda_dict()


    def map_to_rxnorm(self, data_row: "FaersDataRow"):
        """
        Optimizes the data found in FAERS drug tables into formats that are convenient for RxNav's approximate matching
        algorithm to increase the odds of confidently mapping drug entries to RXCUIs.
        :param data_row:
        """

        tries_exhausted = False
        confidence_score = -np.inf

        while confidence_score <= self.thresh and not tries_exhausted:

            response: "RxNavResponse" = self.try_mapping_nda_num(data=data_row)
            if response.success:
                print(response)
                break





        # if we receive a low confidence score
        # if res.candidates[0].score <= self.thresh:


    def try_mapping_nda_num(self, data) -> "RxNavResponse":
        if data.nda_num:  # if an nda_num is present, check it against the dictionary first.
            nda_mapping: "Optional[str]" = self.nda_dict.get(data.nda_num, None)
            if nda_mapping is None:
                pass
            return approx_match(query=nda_mapping)

    @staticmethod
    def _load_nda_dict(path: str) -> Dict:
        nda_df = pd.read_csv(path, header=None)
        return {nda_df["nda_num"]: nda_df["trade_name"]}
