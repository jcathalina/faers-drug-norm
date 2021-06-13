"""
convenient functions for the manipulation of FAERS data, e.g. the minification of the data to make it easier to analyse.
"""

import pandas as pd
import numpy as np


def minify_faers_data(full_faers_filepath: str, minified_faers_filepath: str) -> None:
    """
    Minimizes the FAERS data entries by dropping duplicates following the rule where we only
    retain the unique rows containing the highest information quality, i.e. the entries where
    the most columns are filled.
    This is a compromise where we are willing to sometimes lose some rows that may have had objectively
    higher quality information, but we are assuming that rows that have had more columns filled are more
    likely to have been entered more carefully and so that generally we can assume that this is a safer approach.
    """
    df = pd.read_csv(full_faers_filepath, low_memory=False)
    # We only care about the following columns when it comes to info quality as we use these to create our RxNav queries
    sub_df = df[["drugname", "prod_ai", "nda_num", "route", "dose_amt", "dose_unit", "dose_form"]]

    # Some entries contain "UNKNOWN" or "unknown", and should not count towards the info quality score so we remove them
    print("Removing entries with 'unknown' or 'unk', this may take a while...")
    sub_df = sub_df.replace("(?i)(unknown|unk)", np.nan, regex=True)
    print("Done!")

    # Calculate scores [0-7] by missing rows, where 0 means a perfect entry and 7 means the entry is empty
    # We sort them afterwards from best to worst for the dupe removal step
    sub_df_scores = sub_df.shape[1] - sub_df.count(axis=1)
    sub_df["scores"] = sub_df_scores
    sub_df = sub_df.sort_values(by=["scores"])
    sub_df = sub_df.drop_duplicates("drugname",
                                    keep="first")  # Drop all duplicates except the ones with the best scores

    indexes_to_keep = sub_df.index
    df = df.iloc[indexes_to_keep]
    df.to_csv(minified_faers_filepath, index=False)


def minify_legacy_data(full_aers_filepath: str, minified_aers_filepath: str) -> None:
    """
    Minimizes the AERS (legacy) data entries by dropping duplicates following the rule where we only
    retain the unique rows containing the highest information quality, i.e. the entries where
    the most columns are filled.
    This is a compromise where we are willing to sometimes lose some rows that may have had objectively
    higher quality information, but we are assuming that rows that have had more columns filled are more
    likely to have been entered more carefully and so that generally we can assume that this is a safer approach.
    """
    df = pd.read_csv(full_aers_filepath, low_memory=False)
    # We only care about the following columns when it comes to info quality as we use these to create our RxNav queries
    sub_df = df[["DRUGNAME", "NDA_NUM", "ROUTE", "DOSE_VBM"]]

    # Some entries contain "UNKNOWN" or "UNK", and should not count towards the info quality score so we remove them
    print("Removing entries with 'unknown' or 'unk', this may take a while...")
    sub_df = sub_df.replace("(?i)(unknown|unk)", np.nan, regex=True)
    print("Done!")

    # Calculate scores [0-7] by missing rows, where 0 means a perfect entry and 7 means the entry is empty
    # We sort them afterwards from best to worst for the dupe removal step
    sub_df_scores = sub_df.shape[1] - sub_df.count(axis=1)
    sub_df["scores"] = sub_df_scores
    sub_df = sub_df.sort_values(by=["scores"])
    sub_df = sub_df.drop_duplicates("DRUGNAME",
                                    keep="first")  # Drop all duplicates except the ones with the best scores

    indexes_to_keep = sub_df.index
    df = df.iloc[indexes_to_keep]
    df.to_csv(minified_aers_filepath, index=False)
