from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import os, time, re

SYSTEM_PATH = os.getcwd()+"/chromedriver/chromedriver.exe"
DBPIA_URL = "https://www.dbpia.co.kr"

def crawl(key:str, repeat=1):
    driver = webdriver.Chrome(executable_path=SYSTEM_PATH)
    driver.get(DBPIA_URL)
    
    element = driver.find_element(By.ID,'searchInput')
    driver.find_element(By.ID,'searchInput').click()
    element.send_keys(key)
    element.send_keys("\n")
    time.sleep(2)
    
    get = []
    hrefs = []
    for i in range(1, repeat+1):
        driver.execute_script(f"setPageNum({i});")
        time.sleep(1)
        html_get = driver.page_source
        soup_get = BeautifulSoup(html_get, 'html.parser')
    
        time.sleep(2)
        links = soup_get.find_all('a', 'thesis__link title')
    
        for l in list(links):
            process = (re.findall('href="(.+?)"', str(l)))[0]
            hrefs.append(process)
        
        hrefs.append(int(i))
    
    index = 0
    page = 1
    max_page = 1
    max_index = 0
    
    for href in hrefs:
        if type(href) == int:
            page += 1
            continue
    
        stack = {}
    
        try:
            driver.get(DBPIA_URL+str(href))
        except:
            break
        sub_html = driver.page_source
        sub_soup = BeautifulSoup(sub_html, 'html.parser')
        title = (sub_soup.find_all('h1', 'thesisDetail__tit'))[0].text
    
        authors = sub_soup.find_all('a', 'authorList__author')
        author = []
    
        for name in authors:
            name = name.text
            name = re.sub(" ", "", name)
            name = re.sub("\n", "", name)
            name = re.sub("\t", "", name)
            author.append(name)
        author = list(set(author))
        
        nodeId = (re.findall(r"([?]nodeId=.+)", href))[0]
        view_link = DBPIA_URL+"/pdf/pdfView.do"+nodeId
    
        source = ""
        sources = sub_soup.find_all('a', 'journalList__link')
        for src in sources:
            src = src.text
            src = re.sub(" ", "", src)
            src = re.sub("\n", "", src)
            src = re.sub("\t", "", src)
            source = source + "_" + src
        source = source[1:]
        source = re.sub("_", " > ", source)
    
        keyword = []
        keywords = sub_soup.find_all('a', 'keywordWrap__keyword')
        for ky in keywords:
            process = (re.findall(r"<a .+>(#.+)</a>", str(ky)))[0]
            if not process: process = "None"
            keyword.append(process)
    
        stack["index"] = index              # <-- int
        stack["title"] = title              # <-- str
        stack["author"] = author            # <-- list[str]
        stack["href"] = DBPIA_URL+href # <-- str(link)
        stack["view_link"] = view_link      # <-- str(link)
        stack["source"] = source            # <-- str( > > )
        stack["keyword"] = keyword          # <-- list[str]
        stack["page"] = page                # <-- int
    
        get.insert(int(stack["index"]), stack)

        max_page = page
        max_index = index
    
        index += 1
    
    return get, max_page, max_index