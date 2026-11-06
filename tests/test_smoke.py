import pytest
from selenium.webdriver.common.by import By

from pages.apply_page import ApplyPage, MyApplicationsPage
from pages.events_page import EventsPage
from pages.login_page import LoginPage
from tests.helpers import ADMIN, ANNA, OLEG

pytestmark = [pytest.mark.smoke, pytest.mark.ui]


def test_afisha_opens_with_eight_cards(driver, base_url):
    page = EventsPage(driver, base_url).open()
    assert len(page.titles()) == 8


def test_participant_can_log_in(driver, base_url):
    login = LoginPage(driver, base_url).open()
    login.login(*ANNA)
    login.wait_url_path("/")
    assert login.current_login() == "anna_k"


def test_admin_sees_applications(driver, base_url):
    login = LoginPage(driver, base_url).open()
    login.login(*ADMIN)
    login.wait_url_path("/")
    login.open("/admin")
    cards = login.wait.until(lambda d: d.find_elements(By.CSS_SELECTOR, ".app-card"))
    assert len(cards) == 6


def test_participant_sends_application(driver, base_url):
    LoginPage(driver, base_url).open().login(*OLEG)
    events = EventsPage(driver, base_url)
    events.wait_url_path("/")
    event = events.open_event("Велосипед в городе зимой")
    event.apply_link().click()
    ApplyPage(driver, base_url).fill("Основной зал", "Банковская карта", "Приду на велосипеде").submit()
    my = MyApplicationsPage(driver, base_url)
    my.wait_url_path("/my")
    assert any("Велосипед в городе зимой" in row for row in my.rows())


def test_guest_is_redirected_from_admin(driver, base_url):
    EventsPage(driver, base_url).open("/admin")
    page = LoginPage(driver, base_url)
    page.wait_url_contains("/login")
    assert page.visible(LoginPage.LOGIN).is_displayed()
