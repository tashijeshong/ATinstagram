# This program is used for parsing data from websites
import requests
from lxml import html
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# import os
# import getpass
# import json
# import io
# import time
# from datetime import datetime



# link = 'https://www.instagram.com/accounts/login/'
# login_url = 'https://www.instagram.com/accounts/login/ajax/'

# time = int(datetime.now().timestamp())
# response = requests.get(link)
# csrf = response.cookies['csrftoken']

# username = ""
# password = ""

# payload = {
#     'username': username,
#     'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{time}:{password}',
#     'queryParams': {},
#     'optIntoOneTap': 'false'
# }

# login_header = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
#     "X-Requested-With": "XMLHttpRequest",
#     "Referer": "https://www.instagram.com/accounts/login/",
#     "x-csrftoken": csrf
# }

# login_response = requests.post(login_url, data=payload, headers=login_header)
# json_data = json.loads(login_response.text)

# if json_data["authenticated"]:

#     print("login successful")
#     cookies = login_response.cookies
#     cookie_jar = cookies.get_dict()
#     csrf_token = cookie_jar['csrftoken']
#     print("csrf_token: ", csrf_token)
#     session_id = cookie_jar['sessionid']
#     print("session_id: ", session_id)
# else:
#     print("login failed ", login_response.text)



numPosts = 100

# This function takes a URL and returns the HTML of the page
def get_html(url):
    page = requests.get(url)
    return page.text

# This function parses JSON-like strings to report all values associated with "text" keys
# The format of the desired output is as follows: ..."text":"<VALUE>"...
def parse_json(html):
    ans = []
    for i in range(len(html)):
        if(html[i] == '"'):
            if(html[i+1] == 't' and html[i+2] == 'e' and html[i+3] == 'x' and html[i+4] == 't' and html[i+5] == '"'):
                i = i + 8
                while(html[i] != '"'):
                    ans.append(html[i])
                    i = i + 1
    string = ""
    for a in ans:
        string += a
    return string

# This function parses text for tags, specifically for "#<TAG>"
def parse_tags(text):
    ans = []
    for i in range(len(text)):
        if(text[i] == '#'):
            ans.append('#')
            i = i + 1
            if i >= len(text):
                print("break")
                break
            while(text[i] != ' ' and text[i] != '\\'):
                ans.append(text[i])
                i = i + 1
                if i >= len(text):
                    print("break")
                    ans.append(' ')
                    break
            ans.append(' ')
    string = ""
    for a in ans:
        string += a
    return string

# This function cleans up empty tags from a list of tags
# Removes any tag that has a space right after it
def clean_tags(tags):
    ans = tags.split('#')
    cleanTags = []
    for i in range(len(ans)):
        if len(ans[i]) > 1:
            cleanTags.append(ans[i])
    return cleanTags

# This function takes an array of cleaned tags and returns dictionary of each tag and its frequency
def tag_freq(tags):
    tagFreq = {}
    for tag in tags:
        if tag in tagFreq:
            tagFreq[tag] = tagFreq[tag] + 1
        else:
            tagFreq[tag] = 1
    return tagFreq

# This function returns a subset dictionary of tags that are in the top x% of tag frequencies
def top_tags(tags, tagFreq=0.1):
    if tagFreq > 1 or tagFreq < 0:
        print("Invalid tag frequency, setting to default 0.1")
        tagFreq = 0.1
    sortedTags = sorted(tags.items(), key=lambda x: x[1], reverse=True)
    topTags = {}
    for i in range(len(sortedTags)):
        if i < len(sortedTags) * tagFreq:
            topTags[sortedTags[i][0]] = sortedTags[i][1]
    return topTags

# This function takes a word + frequency and finds the most popular tags used with that tag from [3 most popular and 10 most recent posts]
def popular_tags(word, tagFreq):
    print("Starting...")
    baseURL = "https://www.instagram.com/graphql/query/?query_id=17875800862117404&variables=%7B%22tag_name%22%3A%22"
    tagURL = baseURL + word + "%22%2C%22first%22%3A" + str(numPosts) +"%7D"
    html_doc = get_html(tagURL)
    print("Parsing...")
    parsedJSON = parse_json(html_doc)
    parsedTags = parse_tags(parsedJSON)
    cleanTags = clean_tags(parsedTags)
    cleanTags.sort()
    freqTags = tag_freq(cleanTags)
    print("Done!")
    return top_tags(freqTags, tagFreq)

# This function takes a word and finds all tags used with that word from [3 most popular and 10 most recent posts]
def all_tags(word):
    print("Starting...")
    baseURL = "https://www.instagram.com/graphql/query/?query_id=17875800862117404&variables=%7B%22tag_name%22%3A%22"
    tagURL = baseURL + word + "%22%2C%22first%22%3A" + str(numPosts) +"%7D"
    html_doc = get_html(tagURL)
    print("Parsing...")
    parsedJSON = parse_json(html_doc)
    parsedTags = parse_tags(parsedJSON)
    cleanTags = clean_tags(parsedTags)
    cleanTags.sort()
    freqTags = tag_freq(cleanTags)
    print("Done!")
    return freqTags



print("\nlnt:\n", popular_tags("lnt", 0.1))
print("\nleavenotrace:\n", popular_tags("leavenotrace", 0.1))
print("\nat:\n", popular_tags("at", 0.1))
print("\nappalachiantrail:\n", popular_tags("appalachiantrail", 0.1))

# print("\nlnt:\n", all_tags("lnt"))
# print("\nleavenotrace:\n", all_tags("leavenotrace"))
# print("\nat:\n", all_tags("at"))
# print("\nappalachiantrail:\n", all_tags("appalachiantrail"))

# print("Starting...")
# tagURL = "https://www.instagram.com/graphql/query/?query_id=17875800862117404&variables=%7B%22tag_name%22%3A%22leavenotrace%22%2C%22first%22%3A15%7D"
# html_doc = get_html(tagURL)
# print("Parsing...")
# parsedJSON = parse_json(html_doc)
# parsedTags = parse_tags(parsedJSON)
# cleanTags = clean_tags(parsedTags)
# cleanTags.sort()
# freqTags = tag_freq(cleanTags)
# print("Done!")

# # print(html_doc)
# print("JSON:\n" + parsedJSON)
# print("TAGS:\n" + parsedTags)