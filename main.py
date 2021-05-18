from typing import List, Any

from setup import setup_faers, category_table_to_csv, get_ascii_files_of_category

from mapper.drug_name_mapper import DrugNameMapper
from utils import list_chunker

from mapper.regex_patterns import *

import concurrent.futures

compiled_drug_name_regexes: List[re.Pattern] = [
        rm_tablets,
        rm_capsules,
        rm_abbr_units,
        rm_units,
        rm_hcl
    ]

compiled_active_ingredient_regexes: List[re.Pattern] = []

WORKERS = 4

if __name__ == '__main__':

    mapper = DrugNameMapper(regex_objects_for_drug_name=compiled_drug_name_regexes,
                            regex_objects_for_active_ingredient=compiled_active_ingredient_regexes,
                            nda_filepath="data/dictionaries/nda_dict.csv")

    all_drug_info = mapper.get_drug_info(path_to_drug_table="data/processed/validated_drugname_list.csv")

    chunk_len = len(all_drug_info) // WORKERS

    print(chunk_len)

    c = list(list_chunker(lst=all_drug_info, chunk_length=chunk_len))

    print(len(c))

    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as e:
        for result in e.map(mapper.run, c):
            pass
