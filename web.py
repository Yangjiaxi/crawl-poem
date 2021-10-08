import requests
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver


def create_safari():
    return webdriver.Safari()


def create_chrome():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome("/usr/local/bin/chromedriver", chrome_options=options)
    return driver


def create_worker(select="chrome"):
    if select == "chrome":
        return create_chrome()
    if select == "safari":
        return create_safari()

    raise ValueError("Browser `{}` is not supported.".format(select))


def do_get_driver(driver: WebDriver, url):
    driver.get(url)
    driver.implicitly_wait(5)
    text = driver.find_element_by_css_selector("body").get_attribute("innerHTML")
    return text


def do_get_plain(url):
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
    }
    r = requests.get(url, headers=headers)
    if r.ok:
        return r.text
    raise ValueError(f"\tcode: {r.status_code}, reason: {r.reason}")
