from typing import List

from selenium import webdriver

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

EXECUTABLE_PATH = 'C:/Users/wangt/PycharmProject/SplinterWeb/venv/Scripts/chromedriver.exe'

# Set the time for start waiting for cort booking
START_TIME = "06:50:00"
END_TIME = "00:02:00"

# Type your UTORID and password for login.
USER_NAME = "XXX"
PASSWORD = "XXX"


class CourtBooking(object):
    """
    user_name
    password

    """

    def __init__(self, user_name: str, password: str):
        self.user_name = user_name
        self.password = password
        self.current_time = time.ctime()

        self.driver = webdriver.Chrome()

    def log_in(self, log_in_url):
        self.driver.get(log_in_url)
        self.driver.find_element_by_name("provider").click()  # why do we need a first here?
        self.driver.find_element_by_name("j_username").send_keys(self.user_name)
        self.driver.find_element_by_name("j_password").send_keys(self.password)
        self.driver.find_element_by_name("_eventId_proceed").click()

    def book_court(self) -> None:
        """
        make the booking.
        :return: None
        """

        self.driver_to_tennis_page()
        # take the 3-5pm row's all filed and change the priority to filed 4 first
        statuses: List[WebElement] = self.driver.find_elements_by_xpath("//tr[11]/td/div")[1:]
        statuses.reverse()
        busy = self.reserve(statuses)

        if busy == len(statuses) and self.current_time[11:16] != END_TIME[11:16]:
            print(str(time.ctime()[11:19]) + " Not yet")
            self.driver.refresh()
            self.book_court()
        else:
            print("success")

    def driver_to_tennis_page(self) -> None:
        """
        make the webDriver to tennis page
        :return: None
        """

        tennis = self.driver.find_elements_by_tag_name("a")[30]  # super inefficient, change it later
        self.driver.execute_script("arguments[0].click();", tennis)

        # wait after all tags loaded
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_all_elements_located((By.TAG_NAME, "tr"))
            )
        finally:
            pass

    def reserve(self, statuses: List[WebElement]) -> int:
        """
        Reserve in the list of tags and return the num of busy
        :param statuses:
        :return: busy[int]
        """

        busy = 0
        for status in statuses:
            if status.text == "Reserve":
                status.click()
                # wait after loaded
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.visibility_of_all_elements_located((By.ID, "ReserveForm"))
                    )
                finally:
                    pass
                # click the button for the next
                btn_reserve = self.driver.find_elements_by_id("btnReserve")[0]
                self.driver.execute_script("arguments[0].click();", btn_reserve)
                break
            else:
                busy += 1

        return busy

    @staticmethod
    def get_sleep_time() -> int:
        now_time = list(map(int, time.ctime()[11:19].split(":")))
        start_time = list(map(int, START_TIME.split(":")))

        t = CourtBooking.transfer_to_second(start_time) - CourtBooking.transfer_to_second(now_time)
        return t

    @staticmethod
    def transfer_to_second(ctime: List[int]) -> int:
        return 3600 * ctime[0] + 60 * ctime[1] + ctime[2]



if __name__ == "__main__":
    sleep_time = CourtBooking.get_sleep_time()
    print("u need to wait for " + str(sleep_time) + " seconds")
    time.sleep(sleep_time)

    project = CourtBooking(USER_NAME, PASSWORD)
    project.log_in("https://recreation.utoronto.ca/Account/Login?ReturnUrl=%2FCourtReservation")
    project.book_court()
