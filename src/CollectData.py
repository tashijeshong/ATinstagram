###TODO list
# 1. Get rid of "&nbsp;" in captions

import time
import sys
import os

import Utilities as util
from Utilities import Post

PAGES = 20
MAX_POSTS_PER_PAGE = 50
METADATA_ROOT = "..\\metadata\\"
DATA_ROOT = "..\\data\\"
ERR_USAGE = "Usage:\npython CollectData.py <hashtag>\npython CollectData.py <hashtag> <numPages>\npython CollectData.py <hashtag> <numPages> <endCursor>"

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys

class ParseRequest:
    def __init__(self, tag, numPages=PAGES, endCursor=None):
        self.tag = tag
        self.numPages = numPages
        self.endCursor = endCursor

class Post:
    def __init__(self, id, postCode, ownerId, likes, timeStamp, tags, caption):
        self.id = str(id)
        self.postCode = str(postCode)
        self.ownerId = str(ownerId)
        self.likes = int(likes)
        self.timeStamp = int(timeStamp)
        self.tags = tags # list of strings
        self.caption = str(caption)

class GeoPost:
    def __init__(self,id, name, address, city, lng, lat):
        self.id = str(id)
        self.name = str(name)
        self.address = str(address)
        self.city = str(city)
        self.lng = int(lng)
        self.lat = int(lat)
    
    def __str__(self):
        return "Post_ID: " + self.id + "\t|Post_Code: " + self.postCode + "\t|Owner_ID: " + self.ownerId + "\t|Likes: " + str(self.likes) + "\t|Time_Stamp: " + str(self.timeStamp) + "\t|Tags: " + str(self.tags) + "\t|Caption: " + self.caption 
    
    def asArray(self):
        return [self.id, self.postCode, self.ownerId, self.likes, self.timeStamp, self.tags, self.caption]

    def timeToStr(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.timeStamp))

# main function
def main():
    start = time.time()
    # check if proper number of arguments are given
    # and set up request object
    if len(sys.argv) < 2 or len(sys.argv) > 4:
        print("Invalid number of arguments\n" + ERR_USAGE)
        return -1
    
    request = ParseRequest(sys.argv[1].lower()) # default to numPages = PAGES, endCursor = None
    if len(sys.argv) == 3:
        request.numPages = int(sys.argv[2])
    elif len(sys.argv) == 4:
        request.numPages = int(sys.argv[2])
        request.endCursor = sys.argv[3]
    
    # create url from request object
    url = util.make_url(request.tag, MAX_POSTS_PER_PAGE, request.endCursor) # make url
    print(url) #display url


    # create browser and store results
    currTime = int(time.time())
    allPosts, firstCursor, finalCursor = selenium(request) # opens in controlled browser
    print("Number of posts: ", len(allPosts))

    # Check if folder DATA_ROOT/<tagGroup> exists, if not, create it
    tagGroup = util.tag_to_folder(request.tag)
    if not os.path.exists(DATA_ROOT + tagGroup):
        os.makedirs(DATA_ROOT + tagGroup)

    # Prints results of all_tags to a file <DATA_ROOT>/<tagGroup>/<tag>_<unix_time>ut_<numPages>pages.txt
    outputFilename = DATA_ROOT + "\\" + tagGroup + "\\" + request.tag + "_" + str(currTime) + "ut_" + str(request.numPages) + "pages.txt"
    with open(outputFilename, 'w', encoding="utf8") as f:
        for post in allPosts:
            f.write(str(post) + "\n")
    
    # Check if folder METADATA_ROOT/<tagGroup> exists, if not, create it
    if not os.path.exists(METADATA_ROOT + tagGroup):
        os.makedirs(METADATA_ROOT + tagGroup)

    # Print metadata to a file <METADATA_ROOT>/<tagGroup>/<tag>_bookmark_<unix_time>ut_<numPages>pages.txt
    metaFilename = METADATA_ROOT + "\\" + tagGroup + "\\" + request.tag + "_bookmark_" + str(currTime) + "ut_" + str(request.numPages) + "pages" + ".txt"
    with open(metaFilename, 'w', encoding="utf8") as f:
        f.write("Number of posts: " + str(len(allPosts)) + "\n\n")

        f.write("First Cursor: " + str(firstCursor) + "\n")
        f.write("Final Cursor: " + str(finalCursor) + "\n\n")


    end = time.time()
    print("Time taken: " + str(end - start))
    return 0


# Given a properly established browser, logs in to Instagram using the credentials.txt file
def sel_login(browser):
    #open file "../auth/credentials.txt" and store the first line in variable username and second line in variable password
    with open("../auth/credentials.txt", "r") as f:
        username = f.readline()
        password = f.readline()

    # Create Chrome browser
    browser.get("https://www.instagram.com/")
    wait = WebDriverWait(browser, 10) # [1] code adapted from https://stackoverflow.com/questions/54125384/instagram-login-script-with-selenium-not-being-able-to-execute-send-keystest

    second_page_flag = wait.until(EC.presence_of_element_located(
        (By.CLASS_NAME, "KPnG0")))  # wait until login page appears


    user = browser.find_element_by_name("username") # Find username field
    passw = browser.find_element_by_name('password') # Find password field

    # Enters username and password
    ActionChains(browser)\
        .move_to_element(user).click()\
        .send_keys(username)\
        .move_to_element(passw).click()\
        .send_keys(password)\
        .send_keys(Keys.RETURN)\
        .perform() # [/1]

# This function parses data from a given URL and returns a list of Post objects, the end cursor for the next page, and if there is a next page
def sel_parse(browser, url):
    browser.get(url) # Gets the url and automatically waits for page to load
    html = browser.page_source
    jsonStr = html[84:-20] # Remove first and last part of HTML to only get JSON contents of page
    json1 = util.read_json(jsonStr)
    postsJSON = json1['data']['hashtag']['edge_hashtag_to_media']['edges']
    hasNext = json1['data']['hashtag']['edge_hashtag_to_media']['page_info']['has_next_page']

    posts = []
    for i in range(len(postsJSON)):
        id = postsJSON[i]['node']['id']
        shortCode = postsJSON[i]['node']['shortcode']
        ownerId = postsJSON[i]['node']['owner']['id']
        likes = postsJSON[i]['node']['edge_liked_by']['count']
        timeStamp = postsJSON[i]['node']['taken_at_timestamp']
        caption = postsJSON[i]['node']['edge_media_to_caption']['edges']
        tags = []
        if len(caption) > 0:
            caption = caption[0]['node']['text']
            tags = util.desc_to_tags(caption)
            caption = caption.replace('\n', "<br>").replace('\r', "<br>")
        else:
            caption = ""
        post = Post(id, shortCode, ownerId, likes, timeStamp, tags, caption)
        posts.append(post)
    
    endCursor = json1["data"]["hashtag"]["edge_hashtag_to_media"]["page_info"]["end_cursor"]
    
    return posts, endCursor, hasNext


# Function that does everything related to selenium (opens browser, logs in, reads posts under tags, closes browser)
# Returns a list of all post objects found under the given tag, the first endCursor, and the final endCursor
def selenium(request):
    print("Tag: ", request.tag)
    print("Number of entries: " + str(request.numPages))
    browser = webdriver.Chrome(executable_path="../chromedriver.exe")
    sel_login(browser)
    time.sleep(5) # wait for login to complete

    allPosts = []
    firstCursor = "[None]"
    lastCursor = "[None]"

    for i in range(request.numPages):
        print("Parsing page " + str((i+1)))
        url = util.make_url(request.tag, MAX_POSTS_PER_PAGE, request.endCursor)
        posts, endCursor, morePages = sel_parse(browser, url)
        allPosts.extend(posts)
        if morePages == False:
            print("No more pages")
            break

        lastCursor = endCursor
        request.endCursor = endCursor
        if i == 0:
            firstCursor = endCursor
    
    request.numPages = i + 1


    browser.quit()
    # tags = IP.combine_tags(tags1, tags2)
    return allPosts, firstCursor, lastCursor

# start main
if __name__ == "__main__":
    main()
