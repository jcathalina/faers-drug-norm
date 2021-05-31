from common.downloader import ThreadedFileDownloader
from common.scraper import Scraper

import toml

configuration = toml.load("config.toml")

scraper = Scraper(configuration=configuration)
downloader = ThreadedFileDownloader(configuration=configuration)

faers_links = scraper.run(include_legacy_files=True)

# Example for filtering out all new format FAERS files
# Note: If you are worried about overwriting your already existing files,
# the downloader does a check in the destination folder and skips if it already exists.
only_legacy = filter(lambda x: "faers" not in x, faers_links)
legacy_links = list(only_legacy)

for link in legacy_links:
    downloader.run(link)
