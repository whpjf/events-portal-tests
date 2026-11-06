"""Задание 4. Автотест формы входа: Page Object, явные ожидания, скриншот при падении (хук в conftest.py)."""
import pytest

from pages.login_page import LoginPage
from tests.helpers import ADMIN, ANNA, new_portal

pytestmark = pytest.mark.ui


def test_login_with_correct_data(driver, base_url):
    page = LoginPage(driver, base_url).open().login(*ANNA)
    page.wait_url_path("/")
    assert page.current_login() == "anna_k"


def test_admin_gets_admin_links(driver, base_url):
    page = LoginPage(driver, base_url).open().login(*ADMIN)
    page.wait_url_path("/")
    links = [a.text for a in driver.find_elements("css selector", "nav a")]
    assert "Заявки" in links and "Мероприятия" in links


@pytest.mark.parametrize("login, password", [("anna_k", "wrong-password"), ("nobody", "Parol2026Anna")])
def test_wrong_data_shows_error(driver, base_url, login, password):
    page = LoginPage(driver, base_url).open().login(login, password)
    assert page.form_error() == "Неверный логин или пароль"
    assert "/login" in driver.current_url


def test_login_does_not_depend_on_letter_case(driver, base_url):
    page = LoginPage(driver, base_url).open().login("ANNA_K", "Parol2026Anna")
    page.wait_url_path("/")
    assert page.current_login() == "anna_k"


def test_empty_form_shows_messages_under_fields(driver, base_url):
    page = LoginPage(driver, base_url).open().submit()
    assert page.field_error("login") == "Заполните это поле"
    assert page.field_error("password") == "Заполните это поле"
    assert "/login" in driver.current_url


def test_logout(driver, base_url):
    page = LoginPage(driver, base_url).open().login(*ANNA)
    page.wait_url_path("/")
    page.logout()
    assert driver.find_element("link text", "Вход").is_displayed()


def test_login_is_blocked_after_five_wrong_attempts(driver, base_url):
    # счётчик неудачных входов хранится в памяти сервера и не сбрасывается между тестами,
    # поэтому блокируем отдельного пользователя, а не учебных
    new_portal(base_url).register(login="lock_user", password="Parol2026Lock", password2="Parol2026Lock")
    page = LoginPage(driver, base_url).open()
    for _ in range(5):
        page.open().login("lock_user", "wrong-password")
        page.form_error()
    page.open().login("lock_user", "Parol2026Lock")
    assert "Слишком много неудачных попыток" in page.form_error()


def test_return_to_requested_page_after_login(driver, base_url):
    driver.get(base_url + "/my")
    page = LoginPage(driver, base_url)
    page.wait_url_contains("/login")
    page.login(*ANNA)
    page.wait_url_path("/my")
