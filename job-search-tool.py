#!/usr/bin/env python
# coding: utf-8

# In[1]:


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


# In[3]:


url = "https://washpost.wd5.myworkdayjobs.com/washingtonpostcareers/jobs"


# In[4]:


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


# In[5]:


chrome_options = Options()
driver = webdriver.Chrome(
        ChromeDriverManager().install(),
        options=chrome_options
        )


# In[6]:


def click(driver, by_locator):
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(by_locator)).click()

def is_visible(driver,by_locator):
        element=WebDriverWait(driver, 10).until(EC.visibility_of_element_located(by_locator))
        return bool(element)


# ## Washington Post

# ### Define Locators

# In[7]:


NEXT_BUTTON=(By.XPATH,"//*[@aria-label='next']")
JOBS=(By.XPATH,"//*[@data-automation-id='jobTitle']")
JOB_TIME = (By.XPATH,"//*[@data-automation-id='time']")



# ### Get All Job Links

# In[8]:


page_to_click = True
job_links = []
counter = 1
while page_to_click == True:
    if counter == 1:
        url = "https://washpost.wd5.myworkdayjobs.com/washingtonpostcareers/jobs"
        driver.get(url)
    else:
        try:
            click(driver, NEXT_BUTTON)
            time.sleep(2)
        except:
            print("This was the last page")
            page_to_click = False
            break


    try:
        is_visible(driver, JOBS)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        job_list_chunk = soup.find("section", {"data-automation-id": "jobResults"})
        url_chunks = job_list_chunk.find_all("a", {"data-automation-id": "jobTitle"})
        for url_chunk in url_chunks:
            start_url = "https://washpost.wd5.myworkdayjobs.com"
            end_url = url_chunk["href"]
            url = f"{start_url}{end_url}"
            job_links.append(url)
        counter = counter + 1
        
        
        
    except:
        print("Page didn't load")
        page_to_click = False      


# ### Scrape Information on All Jobs

# In[9]:


wapo_jobs = []
for url in tqdm(job_links):

    driver.get(url)
    is_visible(driver, JOB_TIME)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    try:
        job_location = soup.find("div", {"data-automation-id": "locations"}).text.split("locations")[1]
    except: 
        job_location = "NA"
    try:
        job_duration= soup.find("div", {"data-automation-id": "time"}).text.split("time type")[1]
    except: 
        job_duration = "NA"
    try:
        job_title= soup.find("h2", {"data-automation-id": "jobPostingHeader"}).text
    except: 
        job_title = "NA"
    try:
        json_script = soup.find("script", {"type":"application/ld+json"}).text
        json_info = json.loads(json_script)
        date_posted = json_info["datePosted"]
    except: 
        date_posted = "NA"

    job = {"company": "The Washington Post", "job_title": job_title,"job_location":job_location, "job_duration": job_duration, "date_posted": date_posted, "url":url, }
    wapo_jobs.append(job)


# ### Save and Export

# In[53]:


df_wapo_jobs = pd.DataFrame(wapo_jobs)
df_wapo_jobs.to_csv("data/thewashingtonpost-jobs.csv", index = False)


# In[47]:





# In[13]:




