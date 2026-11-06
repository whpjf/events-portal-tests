from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class EventsPage(BasePage):
    path = "/"

    CARDS = (By.CSS_SELECTOR, ".cards .card")
    SEARCH = (By.CSS_SELECTOR, ".search input[name=q]")
    SEARCH_BUTTON = (By.CSS_SELECTOR, ".search button")

    def titles(self):
        self.visible(self.CARDS)
        return [c.find_element(By.CSS_SELECTOR, "h2").text for c in self.driver.find_elements(*self.CARDS)]

    def search(self, text):
        field = self.visible(self.SEARCH)
        field.clear()
        field.send_keys(text)
        self.clickable(self.SEARCH_BUTTON).click()
        self.wait.until(lambda d: "q=" in d.current_url)
        return self

    def open_event(self, title):
        for link in self.driver.find_elements(By.CSS_SELECTOR, ".card h2 a"):
            if link.text == title:
                link.click()
                return EventPage(self.driver, self.base_url)
        raise AssertionError("нет мероприятия " + title)


class EventPage(BasePage):
    APPLY = (By.LINK_TEXT, "Подать заявку")

    def apply_link(self):
        return self.clickable(self.APPLY)
