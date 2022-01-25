import webbrowser
import time
import json

import InstaParser as IP

PAGES = 10

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys

class ParseRequest:
    def __init__(self, tag, num_posts, end_cursor=None):
        self.tag = tag
        self.num_posts = num_posts
        self.end_cursor = end_cursor

# main function
def main():
    hashtag, num_posts, end_cursor = get_input() # get user input
    request = ParseRequest(hashtag, num_posts, end_cursor) # create request object
    url = make_url(hashtag, num_posts, end_cursor) # make url
    print(url) #display url



    #Open url in default browser
    # webbrowser.open(url, new=2) # opens in uncontrollable default browser
    all_tags = selenium(request, PAGES) # opens in controlled browser
    top_tags = IP.top_tags(all_tags, 0.1)
    print(top_tags)

    all_tags = IP.sort_tags(all_tags)
    print(all_tags)

    # Prints results of all_tags to a file ../Data/leavenotrace20pages.txt
    outputfilename = "../Data/" + request.tag + "." + str(PAGES) + "pages.txt"
    with open(outputfilename, 'w', encoding="utf8") as f:
        for tag in all_tags:
            f.write(str(all_tags[tag]) + "\t" + tag + "\n")


# Function that takes a tag and number and makes a URL from it
def make_url(hashtag, num_posts, end_cursor):
    url = "https://www.instagram.com/graphql/query/?query_id=17875800862117404&variables=%7B%22tag_name%22%3A%22" + hashtag + "%22%2C%22first%22%3A" + str(num_posts)
    if end_cursor is not None:
        url += "%2C%22after%22%3A%22" + end_cursor + "%22"
    url += "%7D"
    return url

# Asks user input for a hashtag and a number of posts to retrieve
# Also asks for an end cursor if it exists (set to null if no input received)
def get_input():
    hashtag = input("Enter a hashtag: ")
    num_posts = input("Enter the number of rows of posts to retrieve (1-50): ")
    end_cursor = input("Enter the end cursor (if applicable): ")
    if end_cursor == "":
        end_cursor = None
    return hashtag, num_posts, end_cursor


# Function that takes a JSON string as input and returns a JSON object
def read_json(json_str):
    json_obj = json.loads(json_str)
    return json_obj


# Given a properly established browser, logs in to Instagram using the credentials.txt file
def sel_login(browser):
    #open file "../auth/credentials.txt" and store the first line in variable username and second line in variable password
    with open("../auth/credentials.txt", "r") as f:
        username = f.readline()
        password = f.readline()

    #create chrome browser
    browser.get("https://www.instagram.com/")
    wait = WebDriverWait(browser, 10) # [1] code adapted from https://stackoverflow.com/questions/54125384/instagram-login-script-with-selenium-not-being-able-to-execute-send-keystest

    second_page_flag = wait.until(EC.presence_of_element_located(
        (By.CLASS_NAME, "KPnG0")))  # util login page appear


    user = browser.find_element_by_name("username") 
    passw = browser.find_element_by_name('password')

    ActionChains(browser)\
        .move_to_element(user).click()\
        .send_keys(username)\
        .move_to_element(passw).click()\
        .send_keys(password)\
        .send_keys(Keys.RETURN)\
        .perform() # [/1]

# This function parses data from a given URL and returns relevant information
def sel_parse(browser, url):
    browser.get(url)
    time.sleep(5) # wait for next page to load
    html = browser.page_source
    html = html[84:-20] # remove first and last part of html to only get JSON contents of page
    json1 = IP.read_json(html)
    # tag = json1["data"]["hashtag"]["name"]
    # num_entries = len(json1['data']['hashtag']['edge_hashtag_to_media']['edges'])
    end_cursor = json1["data"]["hashtag"]["edge_hashtag_to_media"]["page_info"]["end_cursor"]
    
    return html, end_cursor


# function that does everything related to selenium (opens browser, logs in, reads posts under tags, closes browser)
# might make this return a giant dictionary or datastructure of everything it found
def selenium(request, num_pages):
    print("Tag: ", request.tag)
    print("Number of entries: " + request.num_posts)
    browser = webdriver.Chrome(executable_path="C:/Users/nickh/Downloads/chromedriver_win32/chromedriver.exe")
    sel_login(browser)
    time.sleep(5) # wait for login to complete

    all_tags = None

    for i in range(num_pages):
        print("Parsing page " + str((i+1)))
        url = make_url(request.tag, request.num_posts, request.end_cursor)
        html, end_cursor = sel_parse(browser, url)
        request.end_cursor = end_cursor
        tags = IP.all_tags(html)
        all_tags = IP.combine_tags(all_tags, tags)


    browser.quit()
    # tags = IP.combine_tags(tags1, tags2)
    return all_tags

# start main
if __name__ == "__main__":
    main()
