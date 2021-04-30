import os
import requests
from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

DRIVER_PATH = 'V:\Vincent\Programming\chromedriver\chromedriver'

class Scraper:
    def __init__(self):
        self.headers= {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"}

        self.session = requests.Session()
        self.options = Options()
        self.options.add_argument('headless')
        self.options.add_argument('User-Agent={0}'.format(self.headers['User-Agent']))
        self.options.add_argument("--window-size=1920,1200")
        self.options.add_argument("--log-level=3")
        self.driver = Chrome(options=self.options, executable_path=DRIVER_PATH)

    def getPageSelenium(self, url, wait=False, waitClassName=None, delay=3):
        """ Get Page from given url
        :param url: url to get
        :return: BeautifulSoup object or None
        """
        try:
            self.driver.get(url)
            if wait:
                try:
                    elements_present = EC.presence_of_all_elements_located((By.CLASS_NAME, waitClassName))
                    WebDriverWait(self.driver, delay).until(elements_present)
                except TimeoutException:
                    print("Loading took too much time!")

            html = self.driver.page_source
            # print(html)
        except Exception as e:
            print(e)
            return None
        bs = BeautifulSoup(html, "html.parser")
        return bs

    def getPage(self, url):
        """ Get Page from given url
        :param url: url to get
        :return: BeautifulSoup object or None
        """
        try:
            self.driver.get(url)
            self.driver.implicitly_wait(30)
            html = self.driver.page_source
        except Exception as e:
            print(e)
            return None
        bs = BeautifulSoup(html, "html.parser")
        # f = open("test.txt", "a")
        # f.write(str(bs))
        # f.close()
        return bs

    def openURL(self, url):
        """Open URL as python requests."""
        try:
            req = self.session.get(url, headers=self.headers)
        except Exception as e:
            req = None
            print(f"[-] Error when opening URL: {e}")
        finally:
            return req

    def restartDriver(self):
        print("Restarting chromedriver...")
        self.driver.close()
        self.driver = Chrome(options=self.options, executable_path=DRIVER_PATH)

    def saveImgToFolder(self, img_url, img_name, folder_path):
        img_req = requests.get(img_url)
        path = os.path.join(folder_path, img_name)
        if img_req.status_code == 200:
            with open(path, 'wb') as f:
                f.write(img_req.content)