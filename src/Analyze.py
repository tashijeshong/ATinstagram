import time
import os
import csv

from CollectData import Post
import Utilities as util
import BagOfWords as bag

METADATA_ROOT = "../metadata/"
DATA_ROOT = "../data/"
ALL_DATA = DATA_ROOT + "data_thinned.csv"
RESULTS_ROOT = "../results/"


class Info:
    def __init__(self):
        self.currTime = int(time.time())
        self.postDictionary = {} # dictionary of post objects (key is post id, value is post object)
        self.tagsCollected = [] # list of all tags collected (no duplicates, and single value of "[All_Tags]" if all tags are collected)
        self.topTags = {} # dictionary of top tags sorted by descending value (key is tag, value is number of times tag is used)
        self.topAdjectives = {} # dictionary of top adjectives sorted by descending value (key is adjective, value is number of times adjective is used)
        self.topWords = {} # dictionary of top words sorted by descending value (key is word, value is number of times word is used)
        self.topUsers = {} # dictionary of top users sorted by descending value (key is user, value is number of times posts user has made)
        self.numPosts = 0 # number of unique posts collected
        self.numTags = -1 # number of unique tags collected, -1 if not yet calculated
        self.numUsers = -1 # number of unique users collected, -1 if not yet calculated

        self.sentimentCalculated = False
        self.posPostIds = [] # list of post ids of posts with positive sentiment
        self.negPostIds = [] # list of post ids of posts with negative sentiment
        self.neutralPostIds = [] # list of post ids of posts with neutral sentiment

    # Add a list of posts to the Info object and update the number of posts
    def add_posts(self, posts):
        # Make the new post list into a dictionary
        postDict = util.posts_to_dict(posts)
        # Add the new posts to the post dictionary
        self.postDictionary = util.combine_dicts(self.postDictionary, postDict)
        # Update the number of posts
        self.numPosts = len(self.postDictionary)
    
    def __str__(self):
        return get_info(self)


def main():
    info = Info()
    while(True):
        load_data(info)
        run_analysis(info)
        print_data(info)


# Loads data specified by the user into the Info object (or continue without doing so)
    # and updates the number of posts and hashtags collected
# Gives option to print out the data or quit
def load_data(info):
    # Setup choices
    validInput = ["1", "2", "q", "i", "c"]
    usrChoice = -1
    # Ask for user input
    usrChoice = input("[1]Load all data\n[2]Load hashtag\n[Q]uit   | [I]nfo   | [C]ontinue\nUser Input: ").lower()
    restart = False
    if usrChoice not in validInput:
        print("Invalid input. Try again.")
        restart = True

    elif usrChoice == "q":
        exit("Safely exiting...")

    elif usrChoice == "i":
        print("\n" + str(info) + "\n")
        restart = True

    elif usrChoice == "1":
        print("Loading all data...")
        posts = util.read_posts(ALL_DATA)
        info.add_posts(posts)
        info.tagsCollected = "[All_Tags]"
        print("All " + str(info.numPosts) + " posts loaded.\n\n")
        restart = True

    elif usrChoice == "2":
        hashtag = input("Enter hashtag: ")
        print("Loading data for hashtag '" + hashtag + "'...")
        posts = util.read_posts(ALL_DATA)
        selectedPosts = []
        myHashtag = "#" + hashtag.lower()
        for post in posts:
            lowerTags = [tag.lower() for tag in post.tags]
            if myHashtag in lowerTags:
                selectedPosts.append(post)

        if len(selectedPosts) == 0:
            print("No data found for hashtag '" + hashtag + "'.")
        
        else:
            info.add_posts(selectedPosts)
            info.tagsCollected.append(hashtag)
            print(str(info.numPosts) + " posts loaded for hashtag '" + hashtag + "'.\n\n")
        
        restart = True
        

    elif usrChoice == "c":
        print("Continuing...")
        return
    
    if restart:
        load_data(info) # restart function


# Makes calculations on the data in the Info object as specified by the user
    # and updates the relevant data in the Info object
# Gives option to print out the data or quit
def run_analysis(info):
    # Setup choices
    validInput = ["1", "2", "3", "4", "5", "q", "i","c"]
    usrChoice = -1
    # Ask for user input
    usrChoice = input("\n[1]Count number of unique tags\n[2]Count number of unique users\n[3]Calculate top 5 words\n[4]Calculate top 5 adjectives\n[5]Calculate sentiment\n[Q]uit   | [I]nfo   | [C]ontinue\nUser Input: ").lower()
    restart = False
    if usrChoice not in validInput:
        print("Invalid input. Try again.")
        restart = True

    elif usrChoice == "q":
        exit("Safely exiting...")

    elif usrChoice == "i":
        print("\n" + str(info) + "\n")
        restart = True

    elif usrChoice == "1":
        print("Calculating number of unique tags...")
        calculateUniqueTags(info)
        restart = True
    
    elif usrChoice == "2":
        print("Calculating number of unique users...")
        calculateUniqueUsers(info)
        restart = True
    
    elif usrChoice == "3":
        print("Calculating top 5 words...")
        calculateTopWords(info)
        restart = True
    
    elif usrChoice == "4":
        print("Calculating top 5 adjectives...")
        calculateTopAdjectives(info)
        restart = True
    
    elif usrChoice == "5":
        print("Calculating sentiment...")
        calculateSentiment(info)
        restart = True
    
    elif usrChoice == "c":
        print("Continuing...")
        return
    
    if restart:
        run_analysis(info) # restart function


def print_data(info):
    # Setup choices
    validInput = ["1", "q", "i", "c"]
    usrChoice = -1
    # Ask for user input
    usrChoice = input("\n[1]Print all data\n[Q]uit   | [I]nfo   | [C]ontinue\nUser Input: ").lower()
    restart = False
    if usrChoice not in validInput:
        print("Invalid input. Try again.")
        restart = True

    elif usrChoice == "q":
        exit("Safely exiting...")

    elif usrChoice == "i":
        print("\n" + str(info) + "\n")
        restart = True

    elif usrChoice == "1":
        print_info(info)
        restart = True
    
    elif usrChoice == "c":
        print("Continuing...")
        return
    
    if restart:
        print_data(info) # restart function

# Calculates the number of each unique tag in the posts in the Info object
def calculateUniqueTags(info):
    # Get all tags from all posts and record their counts
    for key in info.postDictionary:
        post = info.postDictionary[key]
        for tag in post.tags:
            if tag not in info.topTags:
                info.topTags[tag] = 1
            else:
                info.topTags[tag] += 1
    
    # Calculate the number of unique tags
    info.numTags = len(info.topTags)
    
    # Sort tags by count
    sortedTags = sorted(info.topTags.items(), key=lambda x: x[1], reverse=True)
    info.topTags = {}
    for tag in sortedTags:
        info.topTags[tag[0]] = tag[1]


# Calculates the number of each unique user in the posts in the Info object
def calculateUniqueUsers(info):
    # Get all users from all posts and record their counts
    for key in info.postDictionary:
        post = info.postDictionary[key]
        if post.ownerId not in info.topUsers:
            info.topUsers[post.ownerId] = 1
        else:
            info.topUsers[post.ownerId] += 1

    # Calculate number of unique users
    info.numUsers = len(info.topUsers)

    # Sort users by count
    sortedUsers = sorted(info.topUsers.items(), key=lambda x: x[1], reverse=True)
    info.topUsers = {}
    for user in sortedUsers:
        info.topUsers[user[0]] = user[1]


# Calculates the top words in the posts in the Info object
# Word count is calculated by the number of times a word is used (not the number of posts it is used in)
def calculateTopWords(info):
    # Gets all common words
    commonWords = []
    with open(DATA_ROOT + "CleanedCommonWords.txt", "r") as f:
        for line in f:
            commonWords.append(line.strip())

    # Get all words from all posts and record their counts
    for key in info.postDictionary:
        post = info.postDictionary[key]
        words = util.split_caption(post.caption)
        for word in words:
            if not word in commonWords and '#' not in word and len(word) > 2:
                if word not in info.topWords:
                    info.topWords[word] = 1
                else:
                    info.topWords[word] += 1
    
    # Sort words by count
    sortedWords = sorted(info.topWords.items(), key=lambda x: x[1], reverse=True)
    info.topWords = {}
    for word in sortedWords:
        info.topWords[word[0]] = word[1]

# Calculates the top adjectives in the posts in the Info object
# Adjective count is calculated by the number of posts that use it
def calculateTopAdjectives(info):
    # Gets all adjectives
    adjectives = []
    THRESHHOLD = 0 # Threshold for how many times a word must appear in order to be considered an adjective
    with open(DATA_ROOT + "sorted_adjectives.txt", "r") as f:
        for line in f:
            # Each line is of format: "[adjective]: [count]"
            adjCount = line.split(":")
            adj = adjCount[0].strip()
            count = int(adjCount[1].strip())
            if count > THRESHHOLD:
                adjectives.append(adj)


    # Get all words from all posts and record the counts of each relevant adjective
    for key in info.postDictionary:
        post = info.postDictionary[key]
        words = util.split_caption(post.caption)
        for adj in adjectives:
            if adj in words:
                if adj not in info.topAdjectives:
                    info.topAdjectives[adj] = 1
                else:
                    info.topAdjectives[adj] += 1
    
    # Sort adjectives by count
    sortedWords = sorted(info.topAdjectives.items(), key=lambda x: x[1], reverse=True)
    info.topAdjectives = {}
    for word in sortedWords:
        info.topAdjectives[word[0]] = word[1]

# Calculates the sentiment of the posts in the Info object
# Stores post ids in info.posPostIds and info.negPostIds
def calculateSentiment(info):
    # Get positive and negative adjectives
    posAdjs = []
    negAdjs = []
    with open(DATA_ROOT + "positive.txt", "r") as f:
        for line in f:
            posAdjs.append(line.strip())
    with open(DATA_ROOT + "negative.txt", "r") as f:
        for line in f:
            negAdjs.append(line.strip())
    
    # Check all post captions for positive and negative adjectives
    # If a post contains more positive adjectives than negative, it is considered positive
    info.posPostIds = []
    info.negPostIds = []
    info.neutralPostIds = []
    for key in info.postDictionary:
        post = info.postDictionary[key]
        words = util.split_caption(post.caption)
        posCount = 0
        negCount = 0
        for word in words:
            if word in posAdjs:
                posCount += 1
            if word in negAdjs:
                negCount += 1
        if posCount > negCount:
            info.posPostIds.append(key)
        elif negCount > posCount:
            info.negPostIds.append(key)
        else:
            info.neutralPostIds.append(key)
    
    info.sentimentCalculated = True
            

def get_info(infoObj):
    info = "Current Analysis Information:\n"

    # Print which tags (if any or all) are collected
    if infoObj.tagsCollected == "[All_Tags]":
        info += "Tags collected:\t\t\tAll tags collected\n"
    elif len(infoObj.tagsCollected) == 0:
        info += "Tags collected:\t\t\tNo tags collected\n"
    else:
        info += "Tags collected:\t\t\t" + str(infoObj.tagsCollected) + "\n"

    # Print number of posts collected
    info += "Number of posts collected:\t" + str(infoObj.numPosts) + "\n"

    # Print number of users collected
    if infoObj.numUsers != -1:
        info += "Number of unique users:\t\t" + str(infoObj.numUsers) + "\n"
    else:
        info += "Number of unique users:\t\t[Not yet calculated]\n"
        
    # Print number of tags collected
    if infoObj.numTags != -1:
        info += "Number of unique tags:\t\t" + str(infoObj.numTags) + "\n"
    else:
        info += "Number of unique tags:\t\t[Not yet calculated]\n"
    
    # Print number of positive posts
    if infoObj.sentimentCalculated:
        info += "Number of positive posts:\t" + str(len(infoObj.posPostIds)) + "\n"
    else:
        info += "Number of positive posts:\t[Not yet calculated]\n"
    
    # Print number of negative posts
    if infoObj.sentimentCalculated:
        info += "Number of negative posts:\t" + str(len(infoObj.negPostIds)) + "\n"
    else:
        info += "Number of negative posts:\t[Not yet calculated]\n"
    
    # Print number of neutral posts
    if infoObj.sentimentCalculated:
        info += "Number of neutral posts:\t" + str(len(infoObj.neutralPostIds)) + "\n"
    else:
        info += "Number of neutral posts:\t[Not yet calculated]\n"

    # Print top 5 tags or fewer if there are less than 5 tags
    if len(infoObj.topTags) == 0:
        info += "No top tags stored yet\n"
    else:
        numTagsPrinting = min(5, len(infoObj.topTags))
        info += "\nTop " + str(numTagsPrinting) + " tags:\n"
        # Print top tags without removing them from the dictionary
        i = 0
        for key in infoObj.topTags:
            if i == numTagsPrinting:
                break
            info += key + ":\t" + str(infoObj.topTags[key]) + "\n"
            i += 1
        
    # Print top 5 adjectives or fewer if there are less than 5 adjectives
    if len(infoObj.topAdjectives) == 0:
        info += "\nNo top adjectives stored yet\n"
    else:
        numAdjectivesPrinting = min(5, len(infoObj.topAdjectives))
        info += "\nTop " + str(numAdjectivesPrinting) + " adjectives:\n"
        # Print top adjectives without removing them from the dictionary
        i = 0
        for key in infoObj.topAdjectives.keys():
            if i == numAdjectivesPrinting:
                break
            info += key + ":\t" + str(infoObj.topAdjectives[key]) + "\n"
            i += 1
        
    # Print top 5 words or fewer if there are less than 5 words
    if len(infoObj.topWords) == 0:
        info += "\nNo top words stored yet\n"
    else:
        numWordsPrinting = min(5, len(infoObj.topWords))
        info += "\nTop " + str(numWordsPrinting) + " words:\n"
        # Print top words without removing them from the dictionary
        i = 0
        for key in infoObj.topWords.keys():
            if i == numWordsPrinting:
                break
            info += key + ":\t" + str(infoObj.topWords[key]) + "\n"
            i += 1

    return info

def print_info(infoObj):
    # Make header for a metadata file
    metaInfo = get_info(infoObj)

    # Make a new folder for the results in the results folder
    newFolderPath = RESULTS_ROOT + "Results_" + str(infoObj.currTime)
    # check if path exists
    if not os.path.exists(newFolderPath):
        os.makedirs(newFolderPath)
    newFolderPath += "/"

    # Write metadata to file
    with open(newFolderPath + "metadata.txt", "w", encoding="utf8") as f:
        f.write(metaInfo)
    
    # If the number of users is calculated, print the user ids and counts
    if infoObj.numUsers != -1:
        with open(newFolderPath + "user_ids.txt", "w", encoding="utf8") as f:
            for user in infoObj.topUsers:
                f.write(str(user) + ": " + str(infoObj.topUsers[user]) + "\n")

    # If the number of tags is calculated, print the tags and their count
    if infoObj.numTags != -1:
        with open(newFolderPath + "tags.txt", "w", encoding="utf8") as f:
            for tag in infoObj.topTags:
                f.write(str(tag) + ": " + str(infoObj.topTags[tag]) + "\n")
    
    # If the number of adjectives is calculated, print the adjectives and their count
    if len(infoObj.topAdjectives) != 0:
        with open(newFolderPath + "adjectives.txt", "w", encoding="utf8") as f:
            for adj in infoObj.topAdjectives.keys():
                f.write(adj + ": " + str(infoObj.topAdjectives[adj]) + "\n")

    # If the number of words is calculated, print the words and their count
    if len(infoObj.topWords) != 0:
        with open(newFolderPath + "words.txt", "w", encoding="utf8") as f:
            for word in infoObj.topWords.keys():
                f.write(str(word) + ": " + str(infoObj.topWords[word]) + "\n")

    # If the pos/neg posts are calculated, print the posts to .csv files
    if infoObj.sentimentCalculated:
        header = ["Post_ID", "Post_Code", "Owner_ID", "Likes", "Time_Stamp", "Tags", "Caption"]
        with open(newFolderPath + "positive_posts.csv", "w", encoding="utf8", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for post in infoObj.posPostIds:
                writer.writerow(infoObj.postDictionary[post].asArray())
        
        with open(newFolderPath + "negative_posts.csv", "w", encoding="utf8", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for post in infoObj.negPostIds:
                writer.writerow(infoObj.postDictionary[post].asArray())
        
        with open(newFolderPath + "neutral_posts.csv", "w", encoding="utf8", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for post in infoObj.neutralPostIds:
                writer.writerow(infoObj.postDictionary[post].asArray())

# start main
if __name__ == "__main__":
    main()
