from alg.formatter import FaersDataRow
from mapping.rxnav import approx_match

import pandas as pd
import numpy as np

relevant_cols = ["primaryid", "caseid", "drug_seq", "role_cod", "drugname", "val_vbm", "route", "dose_vbm", "nda_num",
                 "dose_amt", "dose_unit", "dose_form", "origin", "prod_ai"]
drug_table: pd.DataFrame = pd.read_csv(filepath_or_buffer="data/FAERS_2012Q4_2021Q1.csv",
                                       nrows=100,
                                       usecols=relevant_cols)
drug_table.update(drug_table.select_dtypes(include=np.number).applymap('{:,g}'.format))  # cast dosage values to int formatting if applicable

for _, row in drug_table.iterrows():
    data = FaersDataRow(data=row)
    print(data)
    res = approx_match(query=data.query)
    print(res)

# TODO: Rewrite this as a separate test with hardcoded data entries.
test_series = drug_table.iloc[9995]

row = FaersDataRow(data=test_series)

print(row.query)
print(row.backup_query)
