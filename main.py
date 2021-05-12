import toml

from downloader import ThreadedFileDownloader

if __name__ == '__main__':
    config = toml.load("config.toml")
    downloader = ThreadedFileDownloader(configuration=config)
    urls = ["https://fis.fda.gov/content/Exports/faers_ascii_2012q4.zip"]

    # downloader.get_file(urls[0])
    for url in urls:
        downloader.run_downloader(url)


