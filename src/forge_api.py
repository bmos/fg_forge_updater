"""Provides classes for authenticating to and managing items on the FantasyGrounds Forge marketplace"""

import logging
from dataclasses import dataclass
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from dropzone import DropzoneErrorHandling, drag_build_to_dropzone

logging.basicConfig(level=logging.WARNING, format="%(asctime)s : %(levelname)s : %(message)s")

TIMEOUT: float = 15


class ForgeURLs:
    """Contains URL strings for webpages used on the forge"""

    MANAGE_CRAFT: str = "https://forge.fantasygrounds.com/crafter/manage-craft"
    API_CRAFTER_ITEMS: str = "https://forge.fantasygrounds.com/api/crafter/items"


@dataclass(frozen=True)
class ForgeCredentials:
    """Dataclass used to store the authentication credentials used on FG Forge"""

    user_id: str
    username: str
    password: str
    password_md5: str


@dataclass(frozen=True)
class ForgeItem:
    """Dataclass used to interact with an item on the FG Forge"""

    creds: ForgeCredentials
    item_id: str

    def login(self, driver: webdriver, urls: ForgeURLs) -> None:
        """Open manage-craft and login if prompted"""
        driver.get(urls.MANAGE_CRAFT)

        try:
            WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.ID, "login-form")))
            username_field = driver.find_element(By.NAME, "vb_login_username")
            password_field = driver.find_element(By.NAME, "vb_login_password")
            username_field.send_keys(self.creds.username)
            password_field.send_keys(self.creds.password)
            password_field.submit()
        except TimeoutException:
            pass

    @staticmethod
    def open_items_list(driver: webdriver, urls: ForgeURLs) -> None:
        """Open the manage craft page, raising an exception if the item table size selector isn't found."""
        driver.get(urls.MANAGE_CRAFT)

        try:
            WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.NAME, "items-table_length")))
            items_per_page = Select(driver.find_element(By.NAME, "items-table_length"))
            items_per_page.select_by_visible_text("100")
        except TimeoutException:
            raise Exception("Could not load the Manage Craft page!")

    def open_item_page(self, driver: webdriver) -> None:
        """Open the management page for a specific forge item, raising an exception if a link matching the item_id isn't found."""

        try:
            WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, f"//a[@data-item-id='{self.item_id}']")))
            item_link = driver.find_element(By.XPATH, f"//a[@data-item-id='{self.item_id}']")
            item_link.click()
        except TimeoutException:
            raise Exception("Could not find item page, is FORGE_ITEM_ID correct?")

    @staticmethod
    def add_build(driver: webdriver, new_build: Path) -> None:
        """Uploads a new build to this Forge item, raising an exception if the new_build isn't added to the dropzone or doesn't upload successfully."""

        drag_build_to_dropzone(driver, TIMEOUT, new_build)

        WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "submit-build-button")))
        submit_button = driver.find_element(By.ID, "submit-build-button")
        submit_button.click()

        dropzone_errors = DropzoneErrorHandling(driver, TIMEOUT)
        dropzone_errors.check_report_toast_error()
        dropzone_errors.check_report_dropzone_upload_error()
        dropzone_errors.check_report_upload_percentage()

    @staticmethod
    def set_latest_build_live(driver: webdriver) -> None:
        """Set the latest build as active on the Live release channel, raising an exception if the build selector isn't found."""

        try:
            WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, "//select[@class='form-control item-build-channel item-build-option']"))
            )
            item_builds = driver.find_elements(By.XPATH, "//select[@class='form-control item-build-channel item-build-option']")
            item_builds_latest = Select(item_builds[0])
            item_builds_latest.select_by_visible_text("Live")
        except TimeoutException:
            raise Exception("Could not find item page, is FORGE_ITEM_ID correct?")
