# TODO: Make a devset with random samples from the FAERS dataset, ~10% samples should be good
# TODO: Recreate the banda set using the legacy data + FAERS up until 2015 Q3 (check if this is correct)
# TODO: Write benchmark scripts for performance between tweaks + vs. Banda
# TODO: Write out analysis methods that will be implemented during mapping, e.g. how many times do we match EU names
# TODO: Output some sicc images
# TODO: Add a directly runnable python script that downloads the aggregated data from figshare
from tqdm import tqdm

from alg.formatter import FaersDataRow
from alg.mapping import RxNormMapper, load_faers_data

import logging
logging.basicConfig(filename='faers_dev.log', level=logging.INFO)


if __name__ == "__main__":

    mapper_configuration = {
        "nda_path": "C:/_msc/faers-drug-norm/data/dictionaries/nda_dict.csv",
        "int_path": "C:/_msc/faers-drug-norm/data/dictionaries/eu_brand_names_list.csv",
    }

    faers_configuration = {
        "faers_path": "C:/_msc/faers-drug-norm/data/FAERS_MIN_2012Q4_2021Q1.csv",
        "aers_path": "C:/_msc/faers-drug-norm/data/AERS_MIN_2004Q1_2012Q3.csv",
        "dev_path": "C:/_msc/faers-drug-norm/data/FAERS_DEV_SET.csv",
        "full_path": "C:/_msc/faers-drug-norm/data/FAERS_MIN_FULL_UNTIL_2021Q1.csv",
        "n_rows": 1000
    }

    mapper = RxNormMapper(config=mapper_configuration)
    faers_data = load_faers_data(config=faers_configuration, file_to_use="dev")

    for _, row in tqdm(faers_data.iterrows(), total=len(faers_data)):
        data = FaersDataRow(data=row)
        mapper.map_to_rxnorm(data_row=data)


    print("DONE! HERE ARE THE STATS!!")

    logging.info(f"UNMAPPABLES: {mapper.unmappable}")
    logging.info(f"DRUG NAME ONLY: {mapper.successful_name_only_calls}")
    logging.info(f"DEFAULT QUERY: {mapper.successful_default_calls}")
    logging.info(f"BACKUP QUERY: {mapper.successful_backup_calls}")
