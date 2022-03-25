###TODO list

import time
import sys
import os

import Utilities as util
from Utilities import Post

PAGES = 1
MAX_POSTS_PER_PAGE = 50

DATA_ROOT = "/Users/tashijeshong/Downloads/"
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


class GeoPost:
    def __init__(self, id, postCode, name, shortName, placeID, address, city, lat, lng):
        self.id = str(id)
        self.postCode = str(postCode)
        self.name = str(name)
        self.shortName = str(shortName)
        self.placeID = int(placeID)
        self.address = str(address)
        self.city = str(city)
        self.lat = int(lat)
        self.lng = int(lng)

    def __str__(self):
        return "Post_ID: " + self.id + "\t|Post_Code: " + self.postCode + "\t|Place_Name: " + self.name + "\t|Short_Name: " + self.shortName + "\t|Place_ID: " + str(self.placeID) + "\t|Address: " + self.address + "\t|City: " + str(self.city) + "\t|Latitude: " + str(self.lat) + "\t|Longitude: " + str(self.lng) 
    
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

    posts = util.read_posts(DATA_ROOT + 'data_thinnedOLD.txt')

    posts = posts[:1000]

    # create browser and store results
    currTime = int(time.time())
    allPostsGeo = selenium(posts) # opens in controlled browser
    print("Number of posts: ", len(allPostsGeo))

    # Check if folder DATA_ROOT/<tagGroup> exists, if not, create it
    geoFolderName = '../geodata'
    if not os.path.exists(geoFolderName):
        os.makedirs(geoFolderName)

    # Prints results of all_tags to a file <DATA_ROOT>/<tagGroup>/<tag>_<unix_time>ut_<numPages>pages.txt
    #outputFilename = geoFolderName + "/" + str(currTime) + "ut_" + str(len(allPostsGeo)) + "posts_geodata.txt"
    #with open(outputFilename, 'w', encoding="utf8") as f:
    #    for post in allPostsGeo:
    #        f.write(str(post) + "\n")

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
def sel_parse(browser, post):
    url = make_GeoUrl(post.postCode)
    browser.get(url) # Gets the url and automatically waits for page to load
    html = browser.page_source
    jsonStr = html[84:-20] # Remove first and last part of HTML to only get JSON contents of page

    if jsonStr == '{}':         #if the account is private or lost 
        return None
    
    json1 = util.read_json(jsonStr) #convert to json object

    postGeoInfo = json1['items'][0]
    
    if not 'location' in postGeoInfo.keys():
        return None

    postID = post.id
    postCode = post.postCode

    postName = "[Null]"
    if 'name' in postGeoInfo['location'].keys():
        postName = postGeoInfo['location']['name']
    
    postShortName = "[Null]"
    if 'short_name' in postGeoInfo['location'].keys():
        shortName = postGeoInfo['location']['short_name']

    postPlaceID = -1
    if 'facebook_places_id' in postGeoInfo['location'].keys():
        placeID = postGeoInfo['location']['facebook_places_id']
    
    postAddress = "[Null]"
    if 'address' in postGeoInfo['location'].keys():
        postAddress = postGeoInfo['location']['address']

    postCity = "[Null]"
    if 'city' in postGeoInfo['location'].keys():
        postCity = postGeoInfo['location']['city']
    
    postLat = -1
    if 'lat' in postGeoInfo['location'].keys():
        postLat = postGeoInfo['location']['lat']

    postLng = -1
    if 'lng' in postGeoInfo['location'].keys():
        postLng = postGeoInfo['location']['lng']
    
    
    

    post = GeoPost(postID, postCode, postName, shortName, placeID, postAddress, postCity, postLat, postLng)
 

    return post


# Function that does everything related to selenium (opens browser, logs in, reads posts under tags, closes browser)
# Returns a list of all post objects found under the given tag, the first endCursor, and the final endCursor
def selenium(posts):
    browser = webdriver.Chrome(executable_path="../chromedriver")
    sel_login(browser)
    time.sleep(5) # wait for login to complete

    allPostsGeo = []

    startInner = time.time()

        # Check if folder DATA_ROOT/<tagGroup> exists, if not, create it
    geoFolderName = '../geodata'
    if not os.path.exists(geoFolderName):
        os.makedirs(geoFolderName)

    for i in range(len(posts)):
        print("Parsing post " + str((i+1)))
        geoPost = sel_parse(browser, posts[i])
        if geoPost != None:
            allPostsGeo.append(geoPost)
        
    # Prints results of all_tags to a file <DATA_ROOT>/<tagGroup>/<tag>_<unix_time>ut_<numPages>pages.txt
        outputFilename = geoFolderName + "/" + "ut_" + str(len(allPostsGeo)) + "posts_geodata.txt"
        with open(outputFilename, 'w', encoding="utf8") as f:
            for post in allPostsGeo:
                f.write(str(post) + "\n")


        if (i == 500):
            time.sleep(3600)
    
    endInner = time.time()
    print("Inner loop time taken: " + str(endInner - startInner))


    browser.quit()
    return allPostsGeo


# start main
if __name__ == "__main__":
    main()
