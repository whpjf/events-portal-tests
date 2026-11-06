from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage


class LoginPage(BasePage):
    path = "/login"

    LOGIN = (By.NAME, "login")
    PASSWORD = (By.NAME, "password")
    SUBMIT = (By.CSS_SELECTOR, "form[action='/login'] button[type=submit]")
    FORM_ERROR = (By.CSS_SELECTOR, "p.errors")

    def fill(self, login, password):
        field = self.visible(self.LOGIN)
        field.clear()
        field.send_keys(login)
        field = self.visible(self.PASSWORD)
        field.clear()
        field.send_keys(password)
        return self

    def submit(self):
        self.clickable(self.SUBMIT).click()
        return self

    def login(self, login, password):
        return self.fill(login, password).submit()

    def field_error(self, name):
        """Ждёт, пока под полем появится текст ошибки, и возвращает его."""
        locator = (By.CSS_SELECTOR, f".field-error[data-for='{name}']")
        self.wait.until(lambda d: d.find_element(*locator).text.strip() != "")
        return self.driver.find_element(*locator).text

    def form_error(self):
        return self.text_of(self.FORM_ERROR)
