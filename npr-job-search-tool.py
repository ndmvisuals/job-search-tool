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


# In[2]:


url = "https://recruiting.ultipro.com/NAT1011NATPR/JobBoard/af823b19-a43b-4cda-b6c2-c06508d84cf6"


# In[3]:


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


# In[4]:


chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(
        ChromeDriverManager().install(),
        options=chrome_options
        )


# In[7]:


def click(driver, by_locator):
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(by_locator)).click()

def is_visible(driver,by_locator):
        element=WebDriverWait(driver, 10).until(EC.visibility_of_element_located(by_locator))
        return bool(element)


# ## NPR

# ### Define Locators

# In[5]:


MORE_JOBS_BUTTON=(By.XPATH,"//*[@id='LoadMoreJobs']")
OPPORTUNITY_SUMMARY = (By.XPATH, "//*[@aria-live='polite']" )




# In[10]:


driver.get(url)
is_visible(driver, OPPORTUNITY_SUMMARY)

loop = "y"
while loop == "y":
    try:
        click(driver, MORE_JOBS_BUTTON)
    except:        
        loop = "n"
        


# In[11]:


html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')


# In[12]:


job_list_chunk = soup.find("div", {"id": "Opportunities"})
ls_jobs = job_list_chunk.find_all("div", {"data-automation":"opportunity"})


# ### Scrape Information on All Jobs

# In[13]:


npr_jobs = []
for job in ls_jobs:
    title_chunk = job.find("a", {"data-automation":"job-title"})
    
    try:
        job_category = job.find("span", {"data-bind":"text: JobCategoryName()"}).text
    except:
        job_category = "NA" 
    

    try:
        url = f"https://recruiting.ultipro.com{title_chunk["href"]}"
    except:
        url = "NA"
        
    try:
        job_category = job.find("span", {"data-bind":"text: JobCategoryName()"}).text
    except:
        job_category = "NA"
    try:
        job_location = job.find("span", {"data-automation":"location-description"}).text
    except: 
        job_location = "NA"
    try:
        job_duration = job.find("span", {"data-automation":"job-hours"}).text
    except: 
        job_duration = "NA"
    try:
        job_title = title_chunk.text
    except: 
        job_title = "NA"
    try:
        date_posted = job.find("small", {"data-automation":"opportunity-posted-date"}).text
        
    except: 
        date_posted = "NA"

    job = {"company": "NPR", "job_title": job_title,"job_location":job_location, "job_duration": job_duration,"job_category": job_category ,"date_posted": date_posted, "url":url, }
    npr_jobs.append(job)

    


# ### Save and Export

# In[14]:


df_npr_jobs = pd.DataFrame(npr_jobs)
df_npr_jobs.to_csv("data/npr-jobs.csv", index = False)

