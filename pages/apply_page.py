from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from pages.base_page import BasePage


class ApplyPage(BasePage):
    ROOM = (By.NAME, "room")
    PAYMENT = (By.NAME, "payment")
    COMMENT = (By.NAME, "comment")
    SUBMIT = (By.CSS_SELECTOR, "main form button[type=submit]")

    def fill(self, room, payment, comment=""):
        Select(self.visible(self.ROOM)).select_by_visible_text(room)
        Select(self.visible(self.PAYMENT)).select_by_visible_text(payment)
        if comment:
            self.visible(self.COMMENT).send_keys(comment)
        return self

    def submit(self):
        self.clickable(self.SUBMIT).click()
        return self


class MyApplicationsPage(BasePage):
    path = "/my"
    ROWS = (By.CSS_SELECTOR, "table.table-cards tr:not(:has(th))")

    def rows(self):
        self.visible(self.ROWS)
        return [r.text for r in self.driver.find_elements(*self.ROWS)]
