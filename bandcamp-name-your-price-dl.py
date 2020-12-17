#!/usr/bin/env python3

import argparse
import os
import re
import shutil
import sys

import requests
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def main():
    parser = argparse.ArgumentParser(
        prog="bandcamp-name-your-price-dl",
        description="Automate process of downloading name your price albums from bandcamp",
    )
    parser.add_argument(
        "album_url",
        metavar="album_url",
        type=str,
        help="url of desired bandcamp album",
    )
    parser.add_argument(
        "download_dir",
        metavar="download_dir",
        type=str,
        nargs="?",
        help="directory to download archive with album to",
    )
    parser.add_argument(
        "--encoding",
        "-e",
        type=str,
        choices=("mp3", "mp3v0", "flac", "aac", "ogg", "alac", "wav", "aiff"),
        help="desired encoding",
    )
    parser.add_argument(
        "--skip-nyp-check",
        action="store_false",
        help="don't check if album is name your price before downloading",
    )
    parser.add_argument(
        "--wait-time",
        metavar="seconds",
        type=int,
        default=10,
        help="period to wait for pages loading",
    )
    parser.add_argument(
        "--preparing-wait-time",
        metavar="seconds",
        type=int,
        default=60,
        help="period to wait for bandcamp preparing download",
    )
    parser.add_argument(
        "--driver",
        choices=(
            "chromium",
            "chrome",
            "edge",
            "firefox",
            "opera",
            "safari",
            "webkit",
        ),
        help="desired webdriver (default is chromium)",
    )
    parser.add_argument(
        "--print-url",
        "--p",
        action="store_true",
        help="print url to stdout instead of downloading",
    )
    args = parser.parse_args(sys.argv[1:])

    if args.encoding is not None:
        if args.encoding == "mp3":
            onsite_encoding = "MP3 320"
        elif args.encoding == "mp3v0":
            onsite_encoding = "MP3 V0"
        elif args.encoding == "ogg":
            onsite_encoding = "Ogg Vorbis"
        else:
            onsite_encoding = args.encoding.upper()
    else:
        onsite_encoding = None

    if args.driver is not None:
        if args.driver == "firefox":
            driver = webdriver.Firefox()
        elif args.driver in ("chrome", "chromium"):
            driver = webdriver.Chrome()
        elif args.driver == "edge":
            driver = webdriver.Edge()
        elif args.driver == "opera":
            driver = webdriver.Opera()
        elif args.driver == "safari":
            driver = webdriver.Safari()
        elif args.driver == "webkit":
            driver = webdriver.WebKitGTK()
    else:
        driver = None

    download_url = get_album_download_url(
        args.album_url,
        onsite_encoding=onsite_encoding,
        check_if_album_is_name_your_price=args.skip_nyp_check,
        page_load_wait_time=args.wait_time,
        preparing_wait_time=args.preparing_wait_time,
        driver=driver,
    )
    if type(download_url) is int:
        exit(download_url)
    if args.print_url:
        print(download_url)
    else:
        if args.download_dir is None:
            download_dir = os.path.curdir
        else:
            download_dir = args.download_dir
        download_dir = os.path.abspath(download_dir)
        download_file(download_url, download_dir)


def get_album_download_url(
    album_url,
    onsite_encoding=None,
    check_if_album_is_name_your_price=True,
    page_load_wait_time=10,
    preparing_wait_time=60,
    driver=None,
):
    if driver is None:
        driver = webdriver.Chrome()
    driver.get(album_url)

    # Check if album is actually name your price
    if (
        check_if_album_is_name_your_price
        and driver.find_element_by_xpath(
            "//span[@class='buyItemExtra buyItemNyp secondaryText']"
        ).text
        != "name your price"
    ):
        eprint("Album is not name your price. Aborting.")
        return 1

    buy_link = driver.find_element_by_xpath("//button[@class='download-link buy-link']")
    buy_link.click()

    price_input_filled = driver.find_element_by_xpath(
        "//input[@class='display-price numeric']"
    )
    price_input_filled.clear()
    price_input_filled.send_keys("0")

    free_download_link = WebDriverWait(driver, page_load_wait_time).until(
        EC.visibility_of_element_located(
            (By.XPATH, "//a[@class='download-panel-free-download-link']")
        )
    )
    free_download_link.click()

    # TODO: Handle bandcamp asking for email here

    checkout_button = driver.find_element_by_xpath(
        "//button[@class='download-panel-checkout-button']"
    )

    # Selenium thinks that checkout button is invisible and refuses to click it, so we click it with JavaScript
    driver.execute_script("arguments[0].click();", checkout_button)
    WebDriverWait(driver, 10).until(lambda driver: driver.current_url != album_url)

    # Choose encoding from dropdown list
    if onsite_encoding is not None:
        encoding_dropdown_button = WebDriverWait(driver, page_load_wait_time).until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    "//*[@id='post-checkout-info']/div[1]/div[2]/div[4]/div[3]/div",
                )
            )
        )
        encoding_dropdown_button.click()

        format_list_element = driver.find_element_by_xpath(
            f"//*[@id='post-checkout-info']/div[1]/div[2]/div[4]/div[4]/ul//*[text()='{onsite_encoding}']"
        )
        format_list_element.click()

    direct_download_link = WebDriverWait(driver, preparing_wait_time).until(
        EC.visibility_of_element_located(
            (By.XPATH, "//*[@id='post-checkout-info']/div[1]/div[2]/div[4]/span/a")
        )
    )
    return direct_download_link.get_attribute("href")


def download_file(url, download_dir):
    with requests.get(url, stream=True) as r:
        content_disposition_header = r.headers["content-disposition"]
        on_server_file_name = re.findall('filename="(.+)"', content_disposition_header)[
            0
        ]
        local_filename = os.path.join(download_dir, on_server_file_name)
        eprint("Downloading album to", local_filename, "...")
        with open(local_filename, "wb") as f:
            shutil.copyfileobj(r.raw, f)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


if __name__ == "__main__":
    main()
