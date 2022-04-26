#!/usr/bin/env python
# coding: utf-8

# In[53]:


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


# In[ ]:





# In[54]:


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


# In[55]:


chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(
        ChromeDriverManager().install(),
        options=chrome_options
        )


# In[56]:


def click(driver, by_locator):
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(by_locator)).click()

def is_visible(driver,by_locator):
        element=WebDriverWait(driver, 10).until(EC.visibility_of_element_located(by_locator))
        return bool(element)


# ## NPR

# ### Define Locators

# In[57]:


MORE_JOBS_BUTTON=(By.XPATH,"//*[@id='LoadMoreJobs']")
OPPORTUNITY_SUMMARY = (By.XPATH, "//*[@aria-live='polite']" )




# In[58]:


url = "https://recruiting.ultipro.com/NAT1011NATPR/JobBoard/af823b19-a43b-4cda-b6c2-c06508d84cf6"
driver.get(url)
is_visible(driver, OPPORTUNITY_SUMMARY)

loop = "y"
while loop == "y":
    try:
        click(driver, MORE_JOBS_BUTTON)
    except:        
        loop = "n"
        


# In[59]:


html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')


# In[60]:


job_list_chunk = soup.find("div", {"id": "Opportunities"})
ls_jobs = job_list_chunk.find_all("div", {"data-automation":"opportunity"})
ls_job_urls = []
ls_job_duration = []
for job in ls_jobs:
    try:
        title_chunk = job.find("a", {"data-automation":"job-title"})
        url_string = title_chunk["href"]
        url = f"https://recruiting.ultipro.com{url_string}"
        

    except:
        url = "NA"

    ls_job_urls.append(url)


    try:
        job_duration = job.find("span", {"data-automation":"job-hours"}).text
    except: 
        job_duration = "NA"
    ls_job_duration.append(job_duration)

   



# ### Scrape Information on All Jobs

# In[61]:


npr_jobs = []
for i in tqdm(range(len(ls_job_urls))):
    try:
        url = ls_job_urls[i]
        driver.get(url)
        time.sleep(2)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        
        try:
            job_category = soup.find("span", {"data-bind":"text: JobCategoryName()"}).text
        except:
            job_category = "NA" 
        

        try:
            url = url
        except:
            url = "NA"
            
        
        try:
            job_location = soup.find("span", {"data-automation":"location-description"}).text
            
            if job_location == "":
                
                try:
                    job_location = soup.find("span", {"data-bind":"text: localizedNameAndLocationId()"}).text
                except:
                    job_location = "NA"
        except: 
            try:
                job_location = soup.find("span", {"data-bind":"text: localizedNameAndLocationId()"}).text
            except:
                job_location = "NA"
        try:
            job_duration = ls_job_duration[i]
        except: 
            job_duration = "NA"
        try:
            job_title = soup.find("span", {"data-bind": "text: formattedTitle"}).text
        except: 
            job_title = "NA"
        try:
            date_posted = soup.find("span", {"data-automation":"job-posted-date"}).text
            
        except: 
            date_posted = "NA"

        job = {"company": "NPR", "job_title": job_title,"job_location":job_location, "job_duration": job_duration,"job_category": job_category ,"date_posted": date_posted, "url":url, }
        npr_jobs.append(job)
    except:
        pass

    


# ### Save and Export

# In[62]:


df_npr_jobs = pd.DataFrame(npr_jobs)
df_npr_jobs.to_csv("data/npr-jobs.csv", index = False)

