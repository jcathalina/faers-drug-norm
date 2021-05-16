from typing import List

import toml

from downloader import ThreadedFileDownloader
from scraper import Scraper
from file_manager import FileManager
from tqdm import tqdm

import pandas as pd
import glob
import os


if __name__ == '__main__':

    do_setup = False

    if do_setup:
        # TODO: Extract downloader and file manager to their own scripts, main should only run main loop.
        config = toml.load("config.toml")
        downloader = ThreadedFileDownloader(configuration=config)
        scraper = Scraper(configuration=config)
        file_manager = FileManager()

        urls = scraper.run()

        for url in urls:
            downloader.run(url)

        # TODO: Globally load configuration in one spot that can be accessed from all files. this config getting is ugly.
        data_dir = config.get("downloader").get("dest_dir")
        file_manager.extract_faers(data_dir)
        file_manager.clean_up("data/extracted/ascii")

        def contains(filepath: str, *substrings: str) -> bool:
            for substring in substrings:
                if substring in filepath:
                    return True
            return False

        # TODO: This can probably be done way nicer, us re.compile to use regex to filter only drug files in glob
        path = "data/extracted/ascii"
        all_files = glob.glob(path + "/*.txt")
        drug_files: List[str] = []
        for file in all_files:
            if contains(file, "drug", "DRUG"):
                drug_files.append(file)
        del all_files

        li = []
        for file in tqdm(drug_files):
            df: pd.DataFrame = pd.read_csv(file, sep="$", index_col=None, header=0, low_memory=False)
            try:
                df["origin"] = file.split("/")[-1].split("\\")[-1]  # Bypass weird windows backslash, not necessary for other OS's
            except Exception as e:
                df["origin"] = file.split("/")[-1]
            li.append(df)
        drug_df: pd.DataFrame = pd.concat(li, axis=0, ignore_index=True)

        drug_df.to_csv("data/processed/drug_table.csv")

    df: pd.DataFrame = pd.read_csv("data/processed/drug_table.csv", low_memory=False)
    print(len(df))  # 40_584_418 entries from 2012 Q4 --- 2021 Q1
