import toml

from downloader import ThreadedFileDownloader
from scraper import Scraper

if __name__ == '__main__':
    config = toml.load("config.toml")
    downloader = ThreadedFileDownloader(configuration=config)
    scraper = Scraper(configuration=config)

    urls = scraper.run()

    for url in urls:
        downloader.run(url)


