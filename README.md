# bandcamp_name_your_price_dl

Automate process of downloading name your price albums from [bandcamp](bandcamp.com) with Selenium.

## Installation

```sh
pip install bandcamp_name_your_price_dl
```

Also you need to install a selenium browser driver. Refer to [selenium installation guide](https://selenium-python.readthedocs.io/installation.html#drivers).

## Usage

```text
usage: bandcamp_name_your_price_dl [-h] [--download-dir DOWNLOAD_DIR] [--encoding {mp3,mp3v0,flac,aac,ogg,alac,wav,aiff}]
                                   [--skip-nyp-check] [--wait-time SECONDS] [--preparing-wait-time SECONDS]
                                   [--driver {chromium,chrome,edge,firefox,gecko,opera,phantomjs,safari,webkit}]
                                   [--show-browser-window] [--print-url] [--dont-skip-if-file-exists] [--ignore-cache] [--email EMAIL]
                                   [--country-abbrev COUNTRY_ABBREV] [--postal-code POSTAL_CODE]
                                   ALBUM_URL [DOWNLOAD_DIR]

Automate process of downloading name your price albums from bandcamp.

positional arguments:
  ALBUM_URL             url of desired bandcamp album
  DOWNLOAD_DIR          directory to download album to

optional arguments:
  -h, --help            show this help message and exit
  --download-dir DOWNLOAD_DIR, -d DOWNLOAD_DIR
                        directory to download album to
  --encoding {mp3,mp3v0,flac,aac,ogg,alac,wav,aiff}, -e {mp3,mp3v0,flac,aac,ogg,alac,wav,aiff}, --format {mp3,mp3v0,flac,aac,ogg,alac,wav,aiff}, -f {mp3,mp3v0,flac,aac,ogg,alac,wav,aiff}
                        desired encoding
  --skip-nyp-check, --skip-name-your-price-check
                        don't check if album is name your price before trying to download
  --wait-time SECONDS   period to wait for pages loading (in seconds) (default is 10)
  --preparing-wait-time SECONDS
                        period to wait for bandcamp preparing download (in seconds) (default is 60)
  --driver {chromium,chrome,edge,firefox,gecko,opera,phantomjs,safari,webkit}, --webdriver {chromium,chrome,edge,firefox,gecko,opera,phantomjs,safari,webkit}
                        desired webdriver (default is chromium)
  --show-browser-window
                        show browser window (is hidden by default)
  --print-url, -p       print url to stdout instead of downloading
  --dont-skip-if-file-exists
                        don't skip downloading if desired file already exists in current directory or was already downloaded
  --ignore-cache        don't load cache and don't write anything to it
  --email EMAIL         your email address (is used if bandcamp asks for email)
  --country-abbrev COUNTRY_ABBREV, --country COUNTRY_ABBREV
                        country abbreviation used if bandcamp asks for email
  --postal-code POSTAL_CODE, --postcode POSTAL_CODE, --zip-code POSTAL_CODE
                        postal code used if bandcamp asks for email
```

## Usage example

### Download discography of an artist

To list albums of an artist you may use [bandcamp_list_albums](https://github.com/Layerex/bandcamp_list_albums).

[bandcamp-dl](https://github.com/iheanyi/bandcamp-dl) may be used to download not name your price albums.

```bash
for album in $(bandcamp_list_albums "$BANDCAMP_PAGE_URL" --print-urls)
do
    bandcamp_name_your_price_dl "$album" || bandcamp-dl "$album"
done
```

You may also want to specify email, country and postcode in case bandcamp asks for those and download directory.
