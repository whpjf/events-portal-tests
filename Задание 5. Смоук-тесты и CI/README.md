# Задание 5. Смоук-тесты и CI

Смоук-набор проверяет, что основные сценарии портала вообще работают. Пять тестов в `tests/test_smoke.py`, у каждого метка `smoke`, запуск: `python -m pytest -m smoke -v`.

## Смоук-тесты

| Тест | Что проверяет |
|---|---|
| `test_afisha_opens_with_eight_cards` | афиша открывается без входа, на ней 8 карточек |
| `test_participant_can_log_in` | участник входит, в шапке его логин |
| `test_admin_sees_applications` | администратор открывает «Заявки», видит 6 карточек |
| `test_participant_sends_application` | участник выбирает мероприятие, подаёт заявку и видит её в «Мои заявки» |
| `test_guest_is_redirected_from_admin` | гость, открывший `/admin`, попадает на страницу входа |

Тесты используют те же Page Object и фикстуры, что и тесты входа: портал запускается на отдельной базе, перед каждым тестом данные возвращаются к исходным.

## CI

Файл `.github/workflows/smoke.yml`, GitHub Actions. Запускается на каждый `push` в `main`, на pull request и вручную. Шаги:

1. забирает этот репозиторий и репозиторий портала `whpjf/events-portal` в папку `events-portal`;
2. ставит Python 3.12 и зависимости портала и тестов;
3. печатает версию Chrome (на машине GitHub Chrome уже стоит, драйвер Selenium скачивает сам);
4. запускает `python -m pytest -m smoke -v`; портал поднимается внутри тестов на порту 8103;
5. если тесты упали, выкладывает скриншоты из папки `failed` и `server.log` как артефакт.

## Результат

Первый запуск после `push` (коммит `3f87d46`, запуск № 1, номер в адресе `42314463792`): успешно, общее время 44 секунды. Версии на машине GitHub: Ubuntu, Python 3.12.16, Google Chrome 156. Тесты: `5 passed, 57 deselected in 19.66s`. Красных запусков не было, исправлять в CI было нечего.

Ссылка на запуск: https://github.com/whpjf/events-portal-tests/actions/runs/42314463792

## Скриншоты

| Файл | Что показано |
|---|---|
| screens/01-pytest-smoke.png | запуск смоук-набора на своём компьютере |
| screens/02-actions-spisok.png | вкладка Actions репозитория |
| screens/03-actions-zapusk.png | страница запуска: успешно, 44 с |
| screens/04-actions-zhurnal.png | шаги задачи `smoke` |
