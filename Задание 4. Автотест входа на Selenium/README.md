# Задание 4. Автотест формы входа на Selenium

Проверяется форма входа портала `/login`. Использованы Python, pytest и Selenium WebDriver (Chrome), Page Object, явные ожидания, скриншот при падении теста.

## Как устроено

| Файл | Что в нём |
|---|---|
| `pages/base_page.py` | общий класс страницы: открыть адрес, дождаться элемента (`WebDriverWait`), прочитать текст, имя пользователя в шапке |
| `pages/login_page.py` | страница входа: локаторы полей и кнопки, методы `fill`, `submit`, `login`, `field_error`, `form_error` |
| `tests/test_login.py` | девять тестов входа |
| `conftest.py` | запуск портала на отдельной базе, браузер, возврат данных к исходным перед каждым тестом, хук скриншота при падении |

Ожидания только явные: после действия тест ждёт нужный элемент или адрес (`visibility_of_element_located`, `element_to_be_clickable`, `url_contains`, свои условия через `wait.until`). Пауз `time.sleep` в тестах нет, неявные ожидания не включены.

Локаторы по приоритету: `By.NAME` для полей формы (`login`, `password`), `By.CSS_SELECTOR` для кнопки отправки (`form[action='/login'] button[type=submit]`) и для сообщений (`.field-error[data-for='login']`, `p.errors`), `By.LINK_TEXT` для ссылок.

## Тесты

| Тест | Что проверяет |
|---|---|
| `test_login_with_correct_data` | верные данные: переход на главную, в шапке `anna_k` |
| `test_admin_gets_admin_links` | у администратора в меню «Заявки» и «Мероприятия» |
| `test_wrong_data_shows_error` (2 набора) | неверный пароль и несуществующий логин: «Неверный логин или пароль», остаёмся на `/login` |
| `test_login_does_not_depend_on_letter_case` | `ANNA_K` входит как `anna_k` |
| `test_empty_form_shows_messages_under_fields` | пустая форма: под обоими полями «Заполните это поле», переход не происходит |
| `test_logout` | после «Выйти» в меню снова «Вход» |
| `test_login_is_blocked_after_five_wrong_attempts` | после 5 неверных попыток вход закрыт, сообщение о блокировке |
| `test_return_to_requested_page_after_login` | гость открыл `/my`, вошёл и вернулся на `/my` |

Тест блокировки использует отдельного пользователя `lock_user`, потому что счётчик неудачных входов живёт в памяти сервера и не сбрасывается между тестами (на этом ошиблась в первом прогоне: тест блокировки закрыл вход учебному пользователю `oleg_s`, и упал соседний тест).

## Скриншот при падении

Хук `pytest_runtest_makereport` в `conftest.py` сохраняет снимок окна браузера в папку `failed/`, если тест с браузером упал. Для демонстрации есть тест `tests/test_demo_failure.py` с нарочно неверным ожиданием (ждёт логин `ANNA_K` в шапке, а там `anna_k`). Он помечен `demo` и в обычный запуск не входит: `python -m pytest -m demo`.

## Как запустить

```
python -m venv .venv
.venv\Scripts\pip install -r ..\events-portal\portal\requirements.txt -r requirements.txt
.venv\Scripts\python -m pytest tests/test_login.py -v
```
Портал должен лежать рядом, в папке `events-portal`, или путь задаётся переменной `PORTAL_DIR`. Порт 8103 должен быть свободен. Окно браузера показать можно так: `set HEADLESS=0`.

## Скриншоты

| Файл | Что показано |
|---|---|
| screens/01-pytest-vhod.png | запуск `tests/test_login.py`, 9 тестов проходят |
| screens/02-padenie-i-skrinshot.png | демонстрационный тест падает |
| screens/03-skrinshot-pri-padenii.png | снимок страницы, сохранённый хуком при падении |
