#!/usr/bin/env python
# coding: utf-8

# In[112]:


import pandas as pd
import requests
from bs4 import BeautifulSoup


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
from tqdm import tqdm
from selenium.webdriver import ActionChains


# In[113]:


url = "https://nytimes.wd5.myworkdayjobs.com/NYT"


# In[114]:


def scrape_requests(url):
    page = requests.get(url)
    if page.status_code == 200:
        soup = BeautifulSoup(page.text, 'html.parser')
        return (soup)
    else:
        return(f"Error: {page.status_code}")    

def scrape_selenium(driver, url):
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    return(soup)

def selenium_driver():
    chrome_options = Options()
    driver = webdriver.Chrome(
            ChromeDriverManager().install(),
            options=chrome_options
            )
   
    return(driver)


# In[115]:


chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(
        ChromeDriverManager().install(),
        options=chrome_options
        )


# In[116]:


def click(driver, by_locator):
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(by_locator)).click()

def is_visible(driver,by_locator):
        element=WebDriverWait(driver, 10).until(EC.visibility_of_element_located(by_locator))
        return bool(element)


# ## NYT

# ### Define Locators

# In[5]:


#MORE_JOBS_BUTTON=(By.XPATH,"//*[@id='LoadMoreJobs']")
#OPPORTUNITY_SUMMARY = (By.XPATH, "//*[@aria-live='polite']" )




# In[117]:


driver.get(url)
time.sleep(5)


# In[118]:


SCROLL_PAUSE_TIME = 5

# Get scroll height
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load page
    time.sleep(SCROLL_PAUSE_TIME)

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height


# In[119]:


html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')


job_list_chunk = soup.find("div", {"class": ["WFPO", "WJOO"]})
ls_jobs = job_list_chunk.find_all("div", {"data-automation-id":"promptOption"})  
print(len(ls_jobs))


# In[149]:


nyt_jobs = []
for job in tqdm(ls_jobs):
    id = job["id"]
    #print(id)

    elem = driver.find_element(By.XPATH,f"//*[@id='{id}']" )
    actionChain = ActionChains(driver)
    actionChain.context_click(elem).perform()
    time.sleep(1)
    elem2 = driver.find_element(By.XPATH,"//*[@data-automation-id='seeInNewWindow']" )
    actionChain.click(elem2).perform()
    time.sleep(2)
    windows = driver.window_handles
    parent = windows[0]
    child = windows[1]
    driver.switch_to.window(child)
    time.sleep(2)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    ## Download content
    try:
        json_script = soup.find("script", {"type":"application/ld+json"}).text
        json_info = json.loads(json_script)
    except:
        pass
    try:
        date_posted = json_info["datePosted"]
    except:
        date_posted = "NA"
    try:
        job_title = json_info["title"]
    except:
        job_title = "NA"
    try:
        job_duration = json_info["employmentType"]
    except:
        job_duration = "NA"
    try:
        job_location = soup.find("div", {"class":["gwt-Label", "WGDP", "WPBP"], "data-automation-id":"promptOption"}).text

    except:
        job_location = "NA"
    try:              
        url = soup.find("div", {"class":"css-b3pn3b"})     
        url = url.find("a")
        url = url["href"]
    except:
        url = "NA"
    job = {"company": "New York Times", "job_title": job_title,"job_location":job_location, "job_duration": job_duration,"date_posted": date_posted, "url":url, }
    nyt_jobs.append(job)

    # Close tab

    driver.close()
    time.sleep(5)
    driver.switch_to.window(parent)


# In[125]:


df_nyt_jobs = pd.DataFrame(nyt_jobs)
df_nyt_jobs.to_csv("data/nyt-jobs.csv", index = False)

