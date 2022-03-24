###TODO list

import time
import sys
import os

import Utilities as util
from Utilities import Post

PAGES = 1
MAX_POSTS_PER_PAGE = 50

DATA_ROOT = "../data/"
ERR_USAGE = "Usage:\npython CollectData.py <hashtag>\npython CollectData.py <hashtag> <numPages>\npython CollectData.py <hashtag> <numPages> <endCursor>"
postCodeVar = ""

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
    
    def __str__(self):
        return "Post_ID: " + self.id + "\t|Post_Code: " + self.postCode + "\t|Owner_ID: " + self.ownerId + "\t|Likes: " + str(self.likes) + "\t|Time_Stamp: " + str(self.timeStamp) + "\t|Tags: " + str(self.tags) + "\t|Caption: " + self.caption 
    
    def asArray(self):
        return [self.id, self.postCode, self.ownerId, self.likes, self.timeStamp, self.tags, self.caption]

    def timeToStr(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.timeStamp))


class GeoPost:
    def __init__(self,id, postCode, name, address, city, lng, lat):
        self.id = str(id)
        self.postCode = str(postCode)
        postCodeVar = str(postCode)
        self.name = str(name)
        self.address = str(address)
        self.city = str(city)
        self.lng = int(lng)
        self.lat = int(lat)

    def __str__(self):
        return "Post_ID: " + self.id + "\t|Post_Code: " + self.postCode + "\t|Post_Name: " + self.name + "\t|Address: " + self.address + "\t|City: " + str(self.city) + "\t|Longitude: " + str(self.lng) + "\t|Latitude: " + str(self.lat)
    
    def asArray(self):
        return [self.id, self.name, self.address, self.city, self.lng, self.lat]

    def timeToStr(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.timeStamp))

def make_GeoUrl(postCode):
    return 'https://www.instagram.com/p/' + postCode + '/?__a=1'

# main function
def main():
    start = time.time()
    # check if proper number of arguments are given
    # and set up request objects

    
    # create url from request object
    #url = util.make_url(request.tag, MAX_POSTS_PER_PAGE, request.endCursor) # make url

    posts = util.read_posts(DATA_ROOT + 'data_thinned.txt')

    posts = posts[:10]

    # create browser and store results
    currTime = int(time.time())
    allPostsGeo = selenium(posts) # opens in controlled browser
    print("Number of posts: ", len(allPostsGeo))

    # Check if folder DATA_ROOT/<tagGroup> exists, if not, create it
    geoFolderName = 'geodata'
    if not os.path.exists(DATA_ROOT + geoFolderName):
        os.makedirs(DATA_ROOT + geoFolderName)

    # Prints results of all_tags to a file <DATA_ROOT>/<tagGroup>/<tag>_<unix_time>ut_<numPages>pages.txt
    outputFilename = DATA_ROOT + "/" + geoFolderName + "/" + str(currTime) + "ut_"  + "geodata.txt"
    with open(outputFilename, 'w', encoding="utf8") as f:
        for post in allPostsGeo:
            f.write(str(post) + "\n")

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

    if jsonStr == '{}':         #if the account is private or lost 
        return None
    
    json1 = util.read_json(jsonStr) #convert to json object
   

    postID = json1[0]['items']['id']
    postName = json1[0]['items']['location']['name']
    postAddress = json1[0]['items']['location']['address']
    postCity = json1[0]['items']['location']['city']
    postlng = json1[0]['items']['location']['lng']
    postlat = json1[0]['items']['location']['lat']

    post = GeoPost(postID, postName, postAddress, postCity, postlng, postlat)
 

    return post


# Function that does everything related to selenium (opens browser, logs in, reads posts under tags, closes browser)
# Returns a list of all post objects found under the given tag, the first endCursor, and the final endCursor
def selenium(posts):
    browser = webdriver.Chrome(executable_path="/Users/zoobi/Desktop/chromedriver")
    sel_login(browser)
    time.sleep(5) # wait for login to complete

    allPostsGeo = []

    for i in range(len(posts)):
        print("Parsing post " + str((i+1)))
        url = make_GeoUrl(posts[i].postCode)
        geoPost = sel_parse(browser, url)
        if geoPost != None:
            allPostsGeo.append(geoPost)


    browser.quit()
    return allPostsGeo


# start main
if __name__ == "__main__":
    main()
