#!/usr/bin/env python3

__version__ = "0.0.4"
__desc__ = "Automate process of downloading name your price albums from bandcamp."

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

import requests
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

drivers = (
    "chromium",
    "chrome",
    "edge",
    "firefox",
    "gecko",
    "opera",
    "phantomjs",
    "safari",
    "webkit",
)


def main():
    parser = argparse.ArgumentParser(
        prog="bandcamp_name_your_price_dl",
        description=__desc__,
    )
    parser.add_argument(
        "album_url",
        metavar="ALBUM_URL",
        type=str,
        help="url of desired bandcamp album",
    )
    parser.add_argument(
        "download_dir",
        metavar="DOWNLOAD_DIR",
        type=str,
        nargs="?",
        help="directory to download album to",
    )
    parser.add_argument(
        "--download-dir",
        "-d",
        type=str,
        help="directory to download album to",
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
        "--skip-name-your-price-check",
        action="store_true",
        help="don't check if album is name your price before downloading",
    )
    parser.add_argument(
        "--wait-time",
        metavar="SECONDS",
        type=int,
        default=10,
        help="period to wait for pages loading",
    )
    parser.add_argument(
        "--preparing-wait-time",
        metavar="SECONDS",
        type=int,
        default=60,
        help="period to wait for bandcamp preparing download",
    )
    parser.add_argument(
        "--driver",
        "--webdriver",
        choices=drivers,
        help="desired webdriver (default is chromium)",
    )
    parser.add_argument(
        "--show-browser-window",
        action="store_true",
        help="show browser window (is hidden by default)",
    )
    parser.add_argument(
        "--print-url",
        "-p",
        action="store_true",
        help="print url to stdout instead of downloading",
    )
    parser.add_argument(
        "--dont-skip-if-file-exists",
        action="store_true",
        help="don't skip downloading if desired file already exists in current directory or was"
        " already downloaded",
    )
    parser.add_argument(
        "--ignore-cache",
        action="store_true",
        help="don't load cache and pretend it is empty",
    )
    parser.add_argument(
        "--email",
        type=str,
        help="your email address (is used if bandcamp asks for email)",
    )
    parser.add_argument(
        "--country-abbrev",
        "--country",
        type=str,
        help="country abbreviation used if bandcamp asks for email",
    )
    parser.add_argument(
        "--postal-code",
        "--postcode",
        "--zip-code",
        type=str,
        help="postal code used if bandcamp asks for email",
    )
    args = parser.parse_args(sys.argv[1:])

    album_url = args.album_url
    download_url = None
    local_file_name = None

    # Load cache
    if not args.ignore_cache:
        import standardpaths

        loaded_cache = []

        def ask_to_overwrite_cache():
            if ask_yes_no("Cache seems corrupted. Overwrite?"):
                with open(cache_file, "w") as f:
                    json.dump(loaded_cache, f)
                return True
            else:
                return False

        standardpaths.configure(application_name="bandcamp_name_your_price_dl")
        cache_dir = standardpaths.get_writable_path("cache")
        os.makedirs(cache_dir, exist_ok=True)
        cache_file = os.path.join(cache_dir, "cache.json")
        Path(cache_file).touch()
        try:
            with open(cache_file) as f:
                loaded_cache = json.load(f)
        except json.JSONDecodeError as e:
            print(e.msg)
            if not ask_to_overwrite_cache():
                return 3

    # Search for entry with desired url in cache, if not found then create new one
    for entry in loaded_cache:
        if entry["album_url"] == album_url:
            try:
                download_url = entry["download_url"]
                local_file_name = entry["local_file_name"]
                cache_entry = entry
                break
            except KeyError as e:
                print(e.msg)
                if not ask_to_overwrite_cache():
                    return 3
    else:
        loaded_cache.append({"album_url": album_url})
        cache_entry = loaded_cache[-1]

    if download_url is None:
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

        if args.driver is None:
            args.driver = "chromium"
        if args.driver in ("chrome", "chromium"):
            if not args.show_browser_window:
                options = webdriver.ChromeOptions()
                options.add_argument("--headless")
            else:
                options = None
            driver = webdriver.Chrome(options=options)
        elif args.driver == "edge":
            driver = webdriver.Edge()
        elif args.driver in ("firefox", "gecko"):
            if not args.show_browser_window:
                os.environ["MOZ_HEADLESS"] = "1"
            driver = webdriver.Firefox()
        elif args.driver == "opera":
            driver = webdriver.Opera()
        elif args.driver == "phantomjs":
            driver = webdriver.PhantomJS()
        elif args.driver == "safari":
            driver = webdriver.Safari()
        elif args.driver == "webkit":
            driver = webdriver.WebKitGTK()

        check_if_album_is_name_your_price = not args.skip_nyp_check
        page_load_wait_time = args.wait_time
        preparing_wait_time = args.preparing_wait_time
        email_address = args.email
        country_abbrev = args.country_abbrev
        postal_code = args.postal_code

        eprint("Opening", album_url, "...")
        driver.get(album_url)

        # Check if album is free download
        try:
            direct_free_download_button = driver.find_element_by_xpath(
                "//button[@class='download-link buy-link'][text()='Free Download']"
            )
            direct_free_download_button.click()
        # except NoSuchElementException:
        except NoSuchElementException:
            # Check if album is name your price
            try:
                if (
                    check_if_album_is_name_your_price
                    and driver.find_element_by_xpath(
                        "//span[@class='buyItemExtra buyItemNyp secondaryText']"
                    ).text
                    != "name your price"
                ):
                    eprint("Album is not name your price. Aborting.")
                    return 1
            except NoSuchElementException:
                eprint(
                    "Element indicating if is album name your price not found. Aborting."
                )
                return 1

            try:
                buy_link = driver.find_element_by_xpath(
                    "//button[@class='download-link buy-link']"
                )
                buy_link.click()
            except NoSuchElementException:
                eprint('"Buy Digital Album" link not found. Aborting')
                return 1

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

            # Handle bandcamp asking for email
            try:
                # Check if element is interactable first to exit try block immediately if it is not
                # present
                email_input = driver.find_element_by_xpath("//*[@id='fan_email_address']")
                email_input.send_keys(str(email_address))

                asked_for_email = True
                if email_address is None or postal_code is None:
                    eprint(
                        "Bandcamp asked for email, but no email address or postal code specified."
                        " Aborting."
                    )
                    return 2
                if country_abbrev is not None:
                    country_dropdown_list = Select(
                        driver.find_element_by_xpath("//*[@id='fan_email_country']")
                    )
                    country_dropdown_list.select_by_value(country_abbrev.upper())
                postal_code_input = driver.find_element_by_xpath(
                    "//*[@id='fan_email_postalcode']"
                )
                postal_code_input.send_keys(postal_code)
            except ElementNotInteractableException:
                asked_for_email = False

            checkout_button = driver.find_element_by_xpath(
                "//button[@class='download-panel-checkout-button']"
            )
            # Selenium thinks that checkout button is invisible and refuses to click it, so we click
            # it with JavaScript
            driver.execute_script("arguments[0].click();", checkout_button)

            if asked_for_email:
                eprint(
                    "An email with download link has been sent to",
                    email_address + ".",
                    "Paste link here to continue: ",
                )
                link_from_email = input()
                driver.get(link_from_email)
            else:
                WebDriverWait(driver, page_load_wait_time).until(
                    lambda driver: driver.current_url != album_url
                )

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
                f"//*[@id='post-checkout-info']/div[1]/div[2]/div[4]/div[4]/ul"
                "//*[text()='{onsite_encoding}']"
            )
            format_list_element.click()

        direct_download_link = WebDriverWait(driver, preparing_wait_time).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//*[@id='post-checkout-info']/div[1]/div[2]/div[4]/span/a")
            )
        )

        download_url = direct_download_link.get_attribute("href")
    else:
        eprint("Download url exists in cache. Skipping scrapping.")

    if args.print_url:
        print(download_url)
    else:
        if not args.download_dir:
            download_dir = os.path.curdir
        else:
            download_dir = args.download_dir
        download_dir = os.path.abspath(download_dir)

        if local_file_name is not None:
            file_exists_in_initial_file_path = os.path.exists(local_file_name)
            download_directory_file_name = os.path.join(
                download_dir, os.path.split(local_file_name)[-1]
            )
            file_exists_in_download_dir = os.path.exists(download_directory_file_name)
        else:
            file_exists_in_initial_file_path = False
            file_exists_in_download_dir = False

        if (
            not file_exists_in_initial_file_path and not file_exists_in_download_dir
        ) or args.dont_skip_if_file_exists:
            with requests.get(download_url, stream=True) as r:
                content_disposition_header = r.headers["content-disposition"]
                on_server_file_name = re.findall(
                    'filename="(.+)"', content_disposition_header
                )[0]
                local_file_name = os.path.join(download_dir, on_server_file_name)
                eprint("Downloading album to", local_file_name, "...")
                with open(local_file_name, "wb") as f:
                    shutil.copyfileobj(r.raw, f)
        else:
            if file_exists_in_initial_file_path:
                file_name_to_print = local_file_name
            else:
                file_name_to_print = download_directory_file_name
            eprint(f"File exists in {file_name_to_print}. Skipping downloading.")

    # Add album url, download url and local file name to json file in cache in order to avoid
    # scrapping the page or downloading the album twice
    if not args.ignore_cache:
        cache_entry["album_url"] = album_url
        cache_entry["download_url"] = download_url
        cache_entry["local_file_name"] = local_file_name
        loaded_cache.append(cache_entry)
        with open(cache_file, "w") as f:
            json.dump(loaded_cache, f)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def ask_yes_no(question_string):
    eprint(question_string, "(Y/n)", end=" ")
    return input()[0] in ("Y", "y")


if __name__ == "__main__":
    exit(main())
