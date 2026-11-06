import re

import requests

ANNA = ("anna_k", "Parol2026Anna")
OLEG = ("oleg_s", "Parol2026Oleg")
ADMIN = ("admin_konf", "Admin2026Konf")


class Portal:
    """Клиент для проверок на уровне HTTP: сам берёт csrf-токен перед отправкой формы."""

    def __init__(self, base_url):
        self.base = base_url
        self.s = requests.Session()

    def get(self, path, **kw):
        return self.s.get(self.base + path, allow_redirects=False, **kw)

    def token(self, path="/login"):
        html = self.get(path).text
        return re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)

    def post(self, path, data, form_page=None):
        data = dict(data)
        data.setdefault("csrf_token", self.token(form_page or path))
        return self.s.post(self.base + path, data=data, allow_redirects=False)

    def login(self, user, password):
        return self.post("/login", {"login": user, "password": password}, "/login")

    def register(self, **fields):
        data = dict(login="tester_1", email="tester@mail.test", phone="+7 916 000-11-22", password="Parol2026Test", password2="Parol2026Test")
        data.update(fields)
        return self.post("/register", data, "/register")

    def apply(self, event_id, room="Малый зал", payment="Банковская карта", comment=""):
        # токен берём со страницы «Мои заявки»: форма заявки на прошедшее мероприятие не открывается
        return self.post(f"/events/{event_id}/apply", {"room": room, "payment": payment, "comment": comment}, "/my")


def new_portal(base_url):
    return Portal(base_url)
