"""Ошибочные адреса и поиск: найденные при ручной проверке дефекты оформлены тестами."""
import pytest
import requests

from tests.helpers import ADMIN, ANNA, OLEG, new_portal


def is_site_page(resp):
    return "text/html" in resp.headers.get("content-type", "") and "Конференции" in resp.text


@pytest.mark.parametrize("path", ["/nope", "/events/abc", "/events/0", "/events/99999999999999999999", "/static/nothing.css"])
def test_unknown_address_shows_site_error_page(base_url, path):
    resp = requests.get(base_url + path)
    assert resp.status_code in (404, 422), resp.status_code
    assert is_site_page(resp)


def test_wrong_method_shows_site_error_page(base_url):
    resp = requests.get(base_url + "/logout")
    assert resp.status_code == 405
    assert is_site_page(resp)


@pytest.mark.parametrize("query", ["закваска", "ЗАКВАСКА", "Закваска", "хлеб", "ХЛЕБ ДОМА"])
def test_search_ignores_case_of_russian_letters(base_url, query):
    html = requests.get(base_url + "/", params={"q": query}).text
    assert "Закваска и хлеб дома" in html


def test_search_finds_nothing_for_unknown_word(base_url):
    html = requests.get(base_url + "/", params={"q": "самолёт"}).text
    assert "Ничего не найдено" in html


def test_application_for_past_event_is_rejected(base_url):
    portal = new_portal(base_url)
    portal.login(*OLEG)
    resp = portal.apply(1)  # событие 1 прошло
    assert resp.status_code in (403, 422)
    assert "Пчеловодство" not in portal.get("/my").text


def test_application_cannot_be_finished_before_event(base_url):
    admin = new_portal(base_url)
    admin.login(*ADMIN)
    admin.post("/admin/applications/5/advance", {}, "/admin")  # новая -> назначено
    admin.post("/admin/applications/5/advance", {}, "/admin")  # назначено -> завершено, а мероприятие ещё не прошло
    oleg = new_portal(base_url)
    oleg.login(*OLEG)
    assert oleg.get("/my/5/review").status_code == 303


def test_event_title_with_long_word_does_not_break_phone_layout(driver, base_url):
    admin = new_portal(base_url)
    admin.login(*ADMIN)
    resp = admin.post("/admin/events/new", {"title": "Ж" * 100, "event_date": "2027-02-01T18:00", "place": "Библиотека №14",
                                              "description": "Описание из десяти и более символов", "image": "bees.jpg"})
    assert resp.status_code == 303
    driver.set_window_size(390, 844)
    driver.get(base_url + "/")
    wide = driver.execute_script("return document.documentElement.scrollWidth - document.documentElement.clientWidth")
    assert wide <= 0, f"страница шире экрана на {wide} px"
