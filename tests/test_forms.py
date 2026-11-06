"""Задание 3. Форма регистрации: классы эквивалентности и граничные значения.
Каждая строка в parametrize это один тест-кейс из таблицы в README задания."""
import pytest

from tests.helpers import new_portal

OK, BAD = 303, 422


def check(base_url, expected, **fields):
    resp = new_portal(base_url).register(**fields)
    assert resp.status_code == expected, resp.text[:300]
    return resp


LOGIN_CASES = [
    ("F-01", "abc", OK),               # нижняя граница, 3 символа
    ("F-02", "ab", BAD),               # ниже границы
    ("F-03", "a" * 30, OK),            # верхняя граница
    ("F-04", "a" * 31, BAD),           # выше границы
    ("F-05", "a_1", OK),               # буквы, цифра и подчёркивание
    ("F-06", "анна", BAD),             # кириллица
    ("F-07", "an na", BAD),            # пробел внутри
    ("F-08", "user-1", BAD),           # дефис
    ("F-09", "", BAD),                 # пусто
    ("F-10", "anna_k", BAD),           # логин уже занят
    ("F-11", "ANNA_K", BAD),           # тот же логин в другом регистре
    ("F-12", "tester" + chr(10), BAD),  # перевод строки в конце
]


@pytest.mark.parametrize("case, login, expected", LOGIN_CASES, ids=[c[0] for c in LOGIN_CASES])
def test_login_field(base_url, case, login, expected):
    check(base_url, expected, login=login)


PASSWORD_CASES = [
    ("F-13", "Abcdef1", BAD),          # 7 символов
    ("F-14", "Abcdef12", OK),          # 8 символов
    ("F-15", "        ", BAD),         # 8 пробелов
    ("F-16", "A" * 200, OK),           # очень длинный
]


@pytest.mark.parametrize("case, password, expected", PASSWORD_CASES, ids=[c[0] for c in PASSWORD_CASES])
def test_password_field(base_url, case, password, expected):
    check(base_url, expected, password=password, password2=password)


def test_password_mismatch(base_url):  # F-17
    resp = check(base_url, BAD, password="Parol2026Test", password2="Parol2026Other")
    assert "Пароли не совпадают" in resp.text


EMAIL_CASES = [
    ("F-18", "a@mail.ru", OK),
    ("F-19", "a@mail", BAD),           # нет зоны
    ("F-20", "a mail.ru", BAD),        # нет @
    ("F-21", "a@b.c", BAD),            # зона из одной буквы
    ("F-22", "a@mail.ru" + chr(10), BAD),  # перевод строки в конце
]


@pytest.mark.parametrize("case, email, expected", EMAIL_CASES, ids=[c[0] for c in EMAIL_CASES])
def test_email_field(base_url, case, email, expected):
    check(base_url, expected, email=email)


PHONE_CASES = [
    ("F-23", "+7 916 123-45-67", OK),
    ("F-24", "8 (916) 123-45-67", OK),
    ("F-25", "89161234567", OK),
    ("F-26", "+7 916 123-45-6", BAD),      # на цифру меньше
    ("F-27", "+7 916 123-45-678", BAD),    # на цифру больше
    ("F-28", "+7 916 abc-45-67", BAD),     # буквы
    ("F-29", "+1 916 123-45-67", BAD),     # другая страна
    ("F-30", "+7 ٩١٦ ١٢٣-٤٥-٦٧", BAD),  # арабские цифры
]


@pytest.mark.parametrize("case, phone, expected", PHONE_CASES, ids=[c[0] for c in PHONE_CASES])
def test_phone_field(base_url, case, phone, expected):
    check(base_url, expected, phone=phone)


def test_phone_is_stored_in_one_format(base_url):  # F-31
    portal = new_portal(base_url)
    portal.register(phone="8 (916) 123-45-67")
    assert "+79161234567" in portal.get("/cabinet").text


def test_registration_without_token_is_rejected(base_url):  # F-32
    import requests
    resp = requests.post(base_url + "/register", data={"login": "x1x1", "email": "a@mail.ru", "phone": "89161234567",
                                                        "password": "Parol2026Test", "password2": "Parol2026Test"}, allow_redirects=False)
    assert resp.status_code == 403
