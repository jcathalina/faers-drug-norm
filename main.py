# TODO: Make a devset with random samples from the FAERS dataset, ~10% samples should be good
# TODO: Recreate the banda set using the legacy data + FAERS up until 2015 Q3 (check if this is correct)
# TODO: Write benchmark scripts for performance between tweaks + vs. Banda
# TODO: Write out analysis methods that will be implemented during mapping, e.g. how many times do we match EU names
# TODO: Output some sicc images
# TODO: Add a directly runnable python script that downloads the aggregated data from figshare

faers_configuration = {
    "faers_path": "C:/_msc/faers-drug-norm/data/FAERS_MIN_2012Q4_2021Q1.csv",
    "aers_path": "C:/_msc/faers-drug-norm/data/AERS_MIN_2004Q1_2012Q3.csv",
    "dev_path": "C:/_msc/faers-drug-norm/data/FAERS_DEV_SET.csv",
    "full_path": "C:/_msc/faers-drug-norm/data/FAERS_MIN_FULL_UNTIL_2021Q1.csv",
    "n_rows": None
}
