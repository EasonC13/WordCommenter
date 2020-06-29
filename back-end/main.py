def createBrowser():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    chrome_options = Options()

    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--headless')
    #chrome_options.add_argument('blink-settings=imagesEnabled=false')
    #chrome_options.add_argument('--disable-gpu')
    chrome_options.binary_location = "/usr/bin/google-chrome-stable"

    browser = webdriver.Chrome(executable_path="/usr/bin/chromedriver", chrome_options=chrome_options)
    return browser


def getTranslation(text, browser, method = "AllFreq"):
    text = text.lower()
    text = quote(text)
    browser.get('https://translate.google.com.tw/?hl=zh-TW#view=home&op=translate&sl=auto&tl=zh-TW&text=%s'%text) # 進入網頁
    from time import sleep
    sleep(0.01)
    for i in range(2):
        try:
            result = getAllTranslationByFreq(browser)
            break
        except:
            continue
    
    if 'result' in locals() and len(result) > 0:
        return " ".join(result)
    else:
        return getOneTranslation(browser)

def getOneTranslation(browser):
    return browser.find_element_by_xpath("/html/body/div[2]/div[2]/div[1]/div[2]/div[1]/div[1]/div[2]/div[3]/div[1]/div[2]/div/span[1]").text

    target = browser.find_element_by_css_selector(".container")
    target = target.find_element_by_css_selector(".tlid-results-container")
    target = target.find_element_by_css_selector(".tlid-result")
    target = target.find_element_by_css_selector(".tlid-translation")
    return target.find_element_by_tag_name("span").text


def getAllTranslationByFreq(browser, want = ["常見翻譯"]):
    target = browser.find_element_by_css_selector(".container")
    target = target.find_element_by_css_selector(".gt-cc-l-i")
    target = target.find_element_by_css_selector(".gt-baf-table")
    allTr = target.find_elements(by = "tag name", value = "tr")
    return FilterTranslation(allTr, want)

def FilterTranslation(all_tr_element, want = ["常見翻譯"]):
    out = []
    for tr in all_tr_element:
        text = tr.find_elements_by_tag_name("div")[0].text
        freq = tr.find_elements_by_tag_name("div")[2].get_property("title")
        if "使用頻率" in text and freq == "":
            continue
        elif freq in want:
            out.append(text)
        else:
            break
    return out



####


import configparser
from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, HTTPException, Query, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import uvicorn
import time
from base64 import b64encode, b64decode
from urllib.parse import unquote, quote 

import datetime



app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#browser = createBrowser()



@app.get("/translate")
async def translate(text: str = ""):
    print(text)
    if text != "":
        text = getTranslation(text)
    return {"text":text}

@app.get("/translate-multi")
async def translate_multi(request: Request, text: str = ""):
    try:
        browser = createBrowser()
        texts = unquote(text)
        print(datetime.datetime.now())
        print(texts)
        texts = texts.split("\n")
        out = []
        outJson = {}
        for text in texts:
            if text != "":
                print(text, getTranslation(text, browser))
                result = getTranslation(text, browser)
                outJson[text] = result
                text = text + chr(9) + result
            out.append(text)
        out = "\n".join(out)
        out = quote(out)
        #print(out)
        browser.close()
        return {"text":out, "json":outJson}
    except:
        browser.close()

