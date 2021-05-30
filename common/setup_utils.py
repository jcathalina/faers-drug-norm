from typing import List

import toml

from downloader import ThreadedFileDownloader
from scraper import Scraper
from file_manager import FileManager
from tqdm import tqdm

import pandas as pd
import glob
import os

from sqlalchemy import create_engine
from sql.sql_utils import psql_insert_copy


def contains(filepath: str, *substrings: str) -> bool:
    for substring in substrings:
        if substring in filepath:
            return True
    return False


def setup_faers(load_to_psql: bool = False):
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
    file_manager.clean_up(
        "data/extracted/ascii")  # TODO: Maybe remove all files except for drug files, bypasses filtering.


    # TODO: This can probably be done way nicer, us re.compile to use regex to filter only drug files in glob
    path = "../data/extracted/ascii"
    all_files = glob.glob(path + "/*.txt")
    drug_files: List[str] = []
    for file in all_files:
        if contains(file, "drug", "DRUG"):
            drug_files.append(file)
    del all_files

    li = []
    for file in tqdm(drug_files):
        df: pd.DataFrame = pd.read_csv(file, sep="$", index_col=None, header=0, low_memory=False)
        # TODO: move this try except block to its own function to cleanup code.
        try:
            df["origin"] = file.split("/")[-1].split("\\")[
                -1]  # Bypass weird windows backslash, not necessary for other OS's
        except Exception as e:
            df["origin"] = file.split("/")[-1]
        li.append(df)
    drug_df: pd.DataFrame = pd.concat(li, axis=0, ignore_index=True)

    if not os.path.exists("../data/processed"):
        try:
            os.mkdir("../data/processed")
        except PermissionError as e:
            print(f"Not enough permissions to create file. Caused by: {e}")
    drug_df.to_csv("../data/processed/drug_table.csv", index=False)

    if load_to_psql:
        # print(len(df))  # 40_584_418 entries from 2012 Q4 --- 2021 Q1
        engine = create_engine(
            'postgresql://postgres:x25072014@localhost:5432/fdn')  # TODO: Get this from the config.toml
        drug_df.to_sql('drug_table', engine, method=psql_insert_copy, chunksize=250000)


def read_and_load_to_psql(filepath: str, psql_username: str, psql_password: str, db_name: str, table_name: str,
                          psql_port: str = 5432):
    df: pd.DataFrame = pd.read_csv(filepath, low_memory=False)
    engine = create_engine(
        f'postgresql://{psql_username}:{psql_password}@localhost:{psql_port}/{db_name}')  # TODO: Get this from the config.toml
    df.to_sql(f'{table_name}', engine, method=psql_insert_copy, chunksize=250000)


def get_ascii_files_of_category(category: str = "drug", ascii_files_path: str = "data/extracted/ascii") -> List[str]:
    all_ascii_files = glob.glob(ascii_files_path + "/*.txt")
    category_files: List[str] = []
    for ascii_file in all_ascii_files:
        if contains(ascii_file, category.upper(), category.lower()):
            category_files.append(ascii_file)
    return category_files


def category_table_to_csv(category_files: List[str]):
    df_list: List[pd.DataFrame] = []

    for file in tqdm(category_files):
        df: pd.DataFrame = pd.read_csv(file, sep="$", index_col=None, header=0, low_memory=False)
        # TODO: move this try except block to its own function to cleanup code.
        try:
            df["origin"] = file.split("/")[-1].split("\\")[-1]  # Bypass weird windows backslash, not necessary for other OS's
        except Exception:
            df["origin"] = file.split("/")[-1]
        df_list.append(df)
    cat_df: pd.DataFrame = pd.concat(df_list, axis=0, ignore_index=True)

    if not os.path.exists("../data/processed"):
        try:
            os.mkdir("../data/processed")
        except PermissionError as permission_error:
            print(f"Not enough permissions to create file. Caused by: {permission_error}")
    cat_df.to_csv("../data/processed/drug_table.csv", index=False)
