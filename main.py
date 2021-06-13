# TODO: Recreate the banda set using the legacy data + FAERS up until 2015 Q3 (check if this is correct)
# TODO: Write benchmark scripts for performance between tweaks + vs. Banda
# TODO: Write out analysis methods that will be implemented during mapping, e.g. how many times do we match EU names
# TODO: Output some sicc images
from tqdm import tqdm

from alg.formatter import FaersDataRow
from alg.mapping import RxNormMapper, load_faers_data

mapper_configuration = {
    "nda_path": "C:/_msc/faers-drug-norm/data/dictionaries/nda_dict.csv",
    "int_path": "C:/_msc/faers-drug-norm/data/dictionaries/eu_brand_names_list.csv",
}

faers_configuration = {
    "faers_path": "C:/_msc/faers-drug-norm/data/FAERS_MIN_2012Q4_2021Q1.csv",
    "aers_path": "C:/_msc/faers-drug-norm/data/AERS_MIN_2004Q1_2012Q3.csv",
    "dev_path": "C:/_msc/faers-drug-norm/data/FAERS_DEV_SET.csv",
    "full_path": "C:/_msc/faers-drug-norm/data/FAERS_MIN_FULL_UNTIL_2021Q1.csv",
    "n_rows": None
}


def exp_1_no_clean_no_int():
    faers_configuration["n_rows"] = 10_000
    mapper = RxNormMapper(config=mapper_configuration)
    faers_data = load_faers_data(config=faers_configuration, file_to_use="dev")

    for _, row in tqdm(faers_data.iterrows(), total=len(faers_data)):
        data = FaersDataRow(data=row)
        mapper.map_to_rxnorm(data_row=data, include_international=False)

    df = mapper.to_dataframe()
    df.to_csv("exp_1_no_clean_no_int_10k.csv", index=False)


def exp_2_no_clean_yes_int():
    faers_configuration["n_rows"] = 10_000
    mapper = RxNormMapper(config=mapper_configuration)
    faers_data = load_faers_data(config=faers_configuration, file_to_use="dev")

    for _, row in tqdm(faers_data.iterrows(), total=len(faers_data)):
        data = FaersDataRow(data=row)
        mapper.map_to_rxnorm(data_row=data, include_international=True)

    df = mapper.to_dataframe()
    df.to_csv("exp_2_no_clean_yes_int_10k.csv", index=False)


def exp_3_no_clean_no_int_fulldev():
    mapper = RxNormMapper(config=mapper_configuration)
    faers_data = load_faers_data(config=faers_configuration, file_to_use="dev")

    for _, row in tqdm(faers_data.iterrows(), total=len(faers_data)):
        data = FaersDataRow(data=row)
        mapper.map_to_rxnorm(data_row=data, include_international=False)

    df = mapper.to_dataframe()
    df.to_csv("results/exp_3_no_clean_no_int_fulldev.csv", index=False)


if __name__ == "__main__":
    exp_3_no_clean_no_int_fulldev()
