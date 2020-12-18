# bandcamp_name_your_price_dl

Automate process of downloading name your price albums from bandcamp with Selenium.

## Installation

```sh
pip install bandcamp-name-your-price-dl
```

Also you need to install browser drivers. Refer to [selenium installation guide](https://selenium-python.readthedocs.io/installation.html#drivers).

## Usage

```text
usage: bandcamp_name_your_price_dl [-h] [--encoding {mp3,mp3v0,flac,aac,ogg,alac,wav,aiff}] [--skip-nyp-check] [--wait-time seconds] [--preparing-wait-time seconds]
                                   [--driver {phantomjs,chromium,chrome,edge,firefox,opera,safari,webkit}] [--show-browser-window] [--print-url] [--email EMAIL] [--country-abbrev COUNTRY_ABBREV]
                                   [--postal-code POSTAL_CODE]
                                   album_url [download_dir]

Automate process of downloading name your price albums from bandcamp.

positional arguments:
  album_url             url of desired bandcamp album
  download_dir          directory to download album to

optional arguments:
  -h, --help            show this help message and exit
  --encoding {mp3,mp3v0,flac,aac,ogg,alac,wav,aiff}, -e {mp3,mp3v0,flac,aac,ogg,alac,wav,aiff}
                        desired encoding
  --skip-nyp-check      don't check if album is name your price before downloading
  --wait-time seconds   period to wait for pages loading
  --preparing-wait-time seconds
                        period to wait for bandcamp preparing download
  --driver {phantomjs,chromium,chrome,edge,firefox,opera,safari,webkit}
                        desired webdriver (default is chromium)
  --show-browser-window
                        show browser window (is hidden by default)
  --print-url, --p      print url to stdout instead of downloading
  --email EMAIL         your email address (is used if bandcamp asks for email)
  --country-abbrev COUNTRY_ABBREV, --country COUNTRY_ABBREV
                        country abbreviation used if bandcamp asks for email
  --postal-code POSTAL_CODE, --postcode POSTAL_CODE, --zip-code POSTAL_CODE
                        postal code used if bandcamp asks for email
```
