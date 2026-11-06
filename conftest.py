import os
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

import pytest
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

ROOT = Path(__file__).resolve().parent
# где лежит код портала: по умолчанию рядом, в папке events-portal
PORTAL_DIR = Path(os.environ.get("PORTAL_DIR", ROOT.parent / "events-portal" / "portal"))
PORT = int(os.environ.get("PORTAL_PORT", "8103"))
BASE_URL = f"http://127.0.0.1:{PORT}"
HEADLESS = os.environ.get("HEADLESS", "1") == "1"


def portal_env(db_path):
    env = dict(os.environ)
    env["PORTAL_DB"] = str(db_path)
    env["PYTHONUTF8"] = "1"
    return env


@pytest.fixture(scope="session")
def db_path(tmp_path_factory):
    return tmp_path_factory.mktemp("db") / "test.db"


@pytest.fixture(scope="session")
def server(db_path):
    """Поднимает портал на отдельной пустой базе: миграции, учебные данные, uvicorn."""
    env = portal_env(db_path)
    try:
        requests.get(BASE_URL + "/", timeout=1)
        raise RuntimeError(f"порт {PORT} уже занят другим сервером, остановите его или задайте PORTAL_PORT")
    except requests.ConnectionError:
        pass
    subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], cwd=PORTAL_DIR, env=env, check=True, capture_output=True)
    subprocess.run([sys.executable, "seed.py"], cwd=PORTAL_DIR, env=env, check=True, capture_output=True)
    log = open(ROOT / "server.log", "w", encoding="utf-8")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(PORT)],
        cwd=PORTAL_DIR, env=env, stdout=log, stderr=log,
    )
    for _ in range(60):
        try:
            if requests.get(BASE_URL + "/", timeout=1).status_code == 200:
                break
        except requests.RequestException:
            time.sleep(0.5)
    else:
        proc.terminate()
        raise RuntimeError("портал не запустился, смотрите server.log")
    yield BASE_URL
    proc.terminate()
    proc.wait(timeout=10)
    log.close()


@pytest.fixture(autouse=True)
def fresh_data(server, db_path):
    """Перед каждым тестом данные возвращаются к исходным, чтобы тесты не зависели друг от друга."""
    con = sqlite3.connect(db_path)
    for table in ("reviews", "applications", "events", "users"):
        con.execute(f"DELETE FROM {table}")
    con.commit()
    con.close()
    subprocess.run([sys.executable, "seed.py"], cwd=PORTAL_DIR, env=portal_env(db_path), check=True, capture_output=True)
    yield


@pytest.fixture
def base_url(server):
    return server


@pytest.fixture
def driver(server):
    options = Options()
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,900")
    options.add_argument("--lang=ru")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    drv = webdriver.Chrome(options=options)
    yield drv
    drv.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Если тест с браузером упал, сохраняем скриншот страницы в папку failed/."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        drv = item.funcargs.get("driver")
        if drv is not None:
            folder = ROOT / "failed"
            folder.mkdir(exist_ok=True)
            drv.save_screenshot(str(folder / (item.name.replace("/", "_") + ".png")))
