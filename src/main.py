import hashlib
import logging
import os
from pathlib import Path, PurePath

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from forge_api import ForgeItem, ForgeCredentials, ForgeURLs

logging.basicConfig(level=logging.WARNING, format="%(asctime)s : %(levelname)s : %(message)s")
load_dotenv(Path(PurePath(__file__).parents[1], ".env"))


def upload_make_live(driver: webdriver, item: ForgeItem, new_file: Path) -> None:
    urls = ForgeURLs()
    item.open_manage_item_page(driver, urls)
    item.upload_item_build(driver, new_file, urls)


def main() -> None:
    pass_md5 = hashlib.md5(os.environ["FG_USER_PASS"].encode("utf-8")).hexdigest()
    creds = ForgeCredentials(os.environ["FG_USER_ID"], os.environ["FG_USER_NAME"], os.environ["FG_USER_PASS"], pass_md5)
    item = ForgeItem(creds, os.environ["FG_ITEM_ID"])
    new_file = Path(PurePath(__file__).parents[1], os.environ["FG_UL_FILE"])
    logging.debug("File upload path determined to be: %s", new_file)

    options = webdriver.ChromeOptions()
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--headless=new")
    with webdriver.Chrome(service=Service(), options=options) as driver:
        upload_make_live(driver, item, new_file)


if __name__ == "__main__":
    main()
