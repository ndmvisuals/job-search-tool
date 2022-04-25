#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import re
import sys
import json
import tweepy
import requests
import pandas as pd
import tweepy
from datetime import date
from datetime import timedelta


# In[2]:


#def get_keys(path):
#    with open(path) as f:
#        return json.load(f)
        
#keys = get_keys("keys.txt")



# In[3]:


# WAPO

df_wapo = pd.read_csv("https://raw.githubusercontent.com/ndmvisuals/job-search-tool/main/data/thewashingtonpost-jobs.csv")
df_wapo['date_posted'] = pd.to_datetime(df_wapo['date_posted'],format = "%Y-%m-%d" )


# NPR

df_npr = pd.read_csv("https://raw.githubusercontent.com/ndmvisuals/job-search-tool/main/data/npr-jobs.csv", parse_dates = ["date_posted"])
#df_npr['date_posted'] = pd.to_datetime(df_npr['date_posted'],format = "%b %m, %Y" )


# NYT
df_nyt = pd.read_csv("https://raw.githubusercontent.com/ndmvisuals/job-search-tool/main/data/nyt-jobs.csv", parse_dates = ["date_posted"])


# In[4]:


def _summarize_job_time(df_date):
     df_job_time = df_date["job_duration"].value_counts().to_frame()
     df_job_time.reset_index(inplace=True)
     df_job_time = df_job_time.rename(columns = {'index':'job_type', "job_duration":"number_jobs"})
     return(df_job_time)

def _create_job_sentence(df_date):
    df_job_time = _summarize_job_time(df_date)
    df_job_time.head()
    job_duration_sentences = []
    number_job_types = df_job_time.shape[0]

    for i in range(df_job_time.shape[0]):
        job_type = df_job_time.loc[i]["job_type"].lower()
        job_numbers = df_job_time.loc[i]["number_jobs"]
        job_type_sentence = f"{job_numbers} {job_type} jobs"
        if number_job_types >1 :
            if i+1 == number_job_types :
                job_duration_sentences.append(" and ")
                job_duration_sentences.append(job_type_sentence)
            
            else:
                if number_job_types >2:
                    job_duration_sentences.append(f"{job_type_sentence}, ")
                else:
                    job_duration_sentences.append(f"{job_type_sentence}")

        else:        
            job_duration_sentences.append(job_type_sentence) 

    sentence = "".join(job_duration_sentences)
    return(sentence)
    
def _create_tweet_threads(df_date):
    
    ls_threads = []    
    for i in range(df_date.shape[0]):
        
        job_title = df_date.loc[i]["job_title"]
        job_location = df_date.loc[i]["job_location"]
        job_duration = df_date.loc[i]["job_duration"]
        job_url = df_date.loc[i]["url"]

        thread = f"Job: {job_title}{chr(10)}Location: {job_location}{chr(10)}Type: {job_duration}{chr(10)}URL: {job_url}"
        ls_threads.append(thread)

    return(ls_threads)



def construct_tweet(company, df, date, day_word):

    # Build months
    yesterday = date.strftime("%Y-%m-%d")
    yesterday_month = date.strftime("%b")
    yesterday_day = date.strftime("%d")

    # Filter jobs to specific date ---
    df_date = (df['date_posted'] == yesterday) 
    df_date = df.loc[df_date] 
    df_date = df_date.reset_index()
      

    # Create job type summary sentences
    job_time_sentence = _create_job_sentence(df_date)    
    tweet_threads = _create_tweet_threads(df_date)
    main_tweet = f"{day_word}, {yesterday_month} {yesterday_day}, {company} posted {job_time_sentence}. Job titles and links are posted in thread: "   

    if df_date.shape[0] >0:
        tweet_status = "y"
    else:
        tweet_status = "n"
    return(main_tweet, tweet_threads, tweet_status)

def _get_tweet_id(response):    
    response_json = json.loads(json.dumps(response[0]))
    tweet_id = response_json["id"]
    return(tweet_id)


def publish_tweet(main_tweet, thread_post, client):
    
    response = client.create_tweet(text= main_tweet)
    main_tweet_id = _get_tweet_id(response)

    for thread in thread_post:
        client.create_tweet(text = thread, in_reply_to_tweet_id= main_tweet_id)    
    
    pass
   


# In[240]:


# client = tweepy.Client(consumer_key= keys["consumer_key"],
#                        consumer_secret= keys["consumer_secret"],
#                        access_token= keys["access_token"],
#                        access_token_secret= keys["access_token_secret"],
#                        bearer_token= keys["bearer_token"])

client = tweepy.Client(consumer_key= os.environ.get('CONSUMER_KEY'),
                       consumer_secret= os.environ.get('CONSUMER_SECRET'),
                       access_token= os.environ.get('ACCESS_TOKEN'),
                       access_token_secret= os.environ.get('ACCESS_TOKEN_SECRET'),
                       bearer_token= os.environ.get('BEARER_TOKEN'))


# In[5]:

client.create_tweet(text= "test from github")

#today = date.today()
#yesterday = today - timedelta(days = 1)


#schedule = [[ "@washingtonpost", df_wapo, yesterday, "Yesterday"], 
#["@npr", df_npr, yesterday, "Yesterday" ], 
#["@nyt", df_nyt, yesterday, "Yesterday"]  ]

#for post in schedule:
#    main_tweet, thread_posts, tweet_status = construct_tweet(post[0], post[1], post[2], post[3])

#    print(main_tweet)
#    print(tweet_status)
#    for i in thread_posts:
#        print(i)

#    if tweet_status == "y":
#        publish_tweet(main_tweet, thread_posts, client)   

