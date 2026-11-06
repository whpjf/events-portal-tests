from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    """Общие действия: открыть адрес, дождаться элемента, прочитать текст."""

    path = "/"

    def __init__(self, driver, base_url, timeout=8):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, timeout)

    def open(self, path=None):
        self.driver.get(self.base_url + (path or self.path))
        return self

    def visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def clickable(self, locator):
        return self.wait.until(EC.element_to_be_clickable(locator))

    def text_of(self, locator):
        return self.visible(locator).text

    def wait_url_contains(self, part):
        self.wait.until(EC.url_contains(part))

    def wait_url_path(self, path):
        self.wait.until(lambda d: d.current_url.split("?")[0].rstrip("/") == (self.base_url + path).rstrip("/"))

    # шапка сайта
    WHO = (By.CSS_SELECTOR, "nav .who")
    LOGOUT = (By.CSS_SELECTOR, "nav form button")
    FLASH = (By.CSS_SELECTOR, ".flash")

    def current_login(self):
        return self.text_of(self.WHO)

    def logout(self):
        self.clickable(self.LOGOUT).click()
        self.wait.until(EC.invisibility_of_element_located(self.WHO))
