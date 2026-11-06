"""Демонстрация скриншота при падении теста (задание 4). В обычный запуск не входит: python -m pytest -m demo"""
import pytest

from pages.login_page import LoginPage
from tests.helpers import ANNA

pytestmark = [pytest.mark.demo, pytest.mark.ui]


def test_login_name_in_header_is_upper_case(driver, base_url):
    page = LoginPage(driver, base_url).open().login(*ANNA)
    page.wait_url_path("/")
    # ожидание заведомо неверное: в шапке логин пишется как есть, маленькими буквами
    assert page.current_login() == "ANNA_K"
