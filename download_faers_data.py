from utils.downloader import ThreadedFileDownloader
import os

if __name__ == "__main__":

    configuration = {
        "max_threads": 2,
        "dest_dir": "data"
    }

    files_to_download = {
        "FAERS_2012Q4_2021Q1.csv": "https://ndownloader.figshare.com/files/28345767",
        "AERS_2004Q1_2012Q3.csv": "https://ndownloader.figshare.com/files/28345770"
    }

    for filename, url in files_to_download.items():
        downloader = ThreadedFileDownloader(configuration)
        downloader.run(url)

    # One more loop for the proper renaming of the files. TODO: Probably should just name them according to the key in the downloader.
    dest_dir = configuration.get("dest_dir")
    for filename, url in files_to_download.items():
        os.rename(src=os.path.join(dest_dir, url.split("/")[-1]), dst=os.path.join(dest_dir, filename))
