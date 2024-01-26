from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import selenium.webdriver as webdriver
import requests
from time import sleep
from threading import Lock


def init_driver() -> webdriver:
    chrome_options = Options()
    service = Service(executable_path="/usr/local/bin/chromedriver")
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=service, options= chrome_options)
    return driver

def get_queryGraph(driver: webdriver.Chrome,
                   query: str,
                   type: str,
                   resRef: dict,
                   lock: Lock
                   ) -> None:
    driver.get("https://www.google.com.tw/imghp?hl=zh-TW&authuser=0&ogbl")
    driver.maximize_window()
    image_urls = []
    q = driver.find_element(By.NAME, 'q')
    q.send_keys(query)
    q.submit()
    
    imgs = driver.find_elements(By.CLASS_NAME,'Q4LuWd')
    query_data = driver.find_elements(By.CSS_SELECTOR, ".iGVLpd.kGQAp.BqKtob.lNHeqe")
    
    count = 0 # 圖片編號 
    # 找十張圖片即可退出
    
    for img in imgs:
        img_url=img.get_attribute("src")
        temp_data = dict()
        if img_url != None:
            temp_data['Image'] = img_url
            temp_data['Title'] = query_data[count].get_attribute('title')
            temp_data['Url'] = query_data[count].get_attribute('href')
            image_urls.append(temp_data)
            count += 1
        if count > 10:
            break
        
    # pass by reference
    lock.acquire()
    resRef[f"{type}_image"] = image_urls
    lock.release()


def get_queryVideo(driver: webdriver.Chrome,
                   query: str,
                   type: str,
                   resRef: dict,
                   lock: Lock
                   ) -> None:
    
    driver.get(f"https://www.youtube.com/results?search_query={query}")
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'yt-image img')))

    # sleep(3) # 等一下，driver 會有問題
    result = []
    videos = driver.find_elements(By.TAG_NAME, "ytd-video-renderer")
    
    # print(v1.find_element(By.CSS_SELECTOR, "yt-image img").get_attribute("src"))     # image
    # print(v1.find_element(By.ID, "video-title").get_attribute("title"))     # title
    # print(v1.find_element(By.ID, "video-title").get_attribute("href"))     # url
    count = 0
    for v in videos:
        temp_dict = dict()
        temp_dict['Image'] = v.find_element(By.CSS_SELECTOR, "yt-image img").get_attribute("src")
        temp_dict['Title'] = v.find_element(By.ID, "video-title").get_attribute("title")
        temp_dict['Url'] = v.find_element(By.ID, "video-title").get_attribute("href")
        result.append(temp_dict)
        if count > 10:
            break
        count += 1
        
    # pass by reference
    lock.acquire()
    resRef[f"{type}_video"] = result
    lock.release()
    
def translation(inputTxt: str, model: str) -> str:
    req = dict()
    req['translation_text'] = inputTxt
    req['model'] = model
    res = requests.post("http://140.116.245.157:1002/translation", req)
    return res.json()['after_translation']

if __name__ == "__main__":
    driver = init_driver()
    get_queryGraph(driver, "花花")
    get_queryVideo(driver, '花花')
