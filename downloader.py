from typing import Dict

import requests
import threading
import os

from tqdm import tqdm


class ThreadedFileDownloader:
    """
    Class to download multiple files from a page at a time given a list of URLs.
    Derived from Stefan Fortuin's code @ https://stefanfortuin.nl/article/making-a-multithreaded-file-downloader-in-python
    """
    def __init__(self, configuration: Dict):
        self.config = configuration
        self.headers = configuration.get("headers")
        self.semaphore = threading.Semaphore(value=configuration.get("downloader").get("max_threads"))
        self.chunk_size = 1024

    def get_file(self, url: str):
        self.semaphore.acquire()

        filename: str = url.split("/")[-1]
        filepath: str = os.path.join(self.config.get("downloader").get("dest_dir"), filename)

        if not os.path.isfile(filepath):
            self.download(url, filepath)

        else:
            print(f"file {filepath} already exists, skipping...")

        self.semaphore.release()

    def download(self, url: str, filepath: str):
        try:
            res = requests.get(url=url, timeout=30, stream=True)
            res.raise_for_status()
            self._write_file(res, filepath, "wb")
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")

    def resume(self):
        pass

    def run(self, url: str):
        thread = threading.Thread(target=self.get_file, args=(url,))
        thread.start()

    def _write_file(self, response: requests.Response, filepath: str, mode: str):
        total_size = int(response.headers.get("content-length", 0))  # FAERS Quarterly files server does not support content-length.
        pbar = tqdm(total=total_size, desc=f"{filepath.split('/')[-1]}", unit="B", unit_scale=True, leave=True)
        print(f"total size: {total_size}")
        with open(file=filepath, mode=mode) as f:
            for chunk in response.iter_content(chunk_size=self.chunk_size):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))

        pbar.close()
        print(f"File has been downloaded to: {filepath}", end='\n')

