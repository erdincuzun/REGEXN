from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import os
class BrowserInteractions:
    def __init__(self, url,browser,driver_path, wait="0", scrolldownfor=10):
        self.wait = wait
        self.scrolldownfor = scrolldownfor
        if browser=="firefox":
            self.driver = webdriver.Firefox(executable_path=driver_path)
        elif browser=="chrome":
            self.driver = webdriver.Chrome(executable_path=driver_path)
        elif browser=="safari":
            self.driver = webdriver.Safari(executable_path=driver_path)
        elif browser == "ie":
            self.driver = webdriver.Ie(executable_path=driver_path)
        elif browser=="edge":
            self.driver = webdriver.Edge(executable_path=driver_path)
        elif browser=="opera":
            self.driver = webdriver.Opera(executable_path=driver_path)
        self.driver.implicitly_wait(wait)
        self.driver.get(url)

    def set_url(self, url):
        print(url)
        self.driver.implicitly_wait(self.wait)
        self.driver.get(url)
        if int(self.scrolldownfor) > 0:
            SCROLL_PAUSE_TIME = 2
            # Get scroll height
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            x=0
            while x < self.scrolldownfor:
                # Scroll down to bottom
                #self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                #self.driver.execute_script("window.scrollTo({top: 2000,behavior: 'smooth',});")
                #self.driver.execute_script("scroll(0, document.body.scrollHeight-300);")
                son = self.driver.execute_script("return document.body.scrollHeight")
                for _ in range(0, son, 20):
                    self.driver.execute_script("window.scrollBy(0, 20);")

                #self.driver.find_element_by_tag_name('body').send_keys(Keys.END)
                # Wait to load page
                time.sleep(SCROLL_PAUSE_TIME)

                # Calculate new scroll height and compare with last scroll height
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                x=x+1


    def return_html(self):
        #return self.driver.page_source
        html = self.driver.execute_script("return document.documentElement.outerHTML;")
        return html


