import glob

from CollectData import Post
import Utilities as util
import BagOfWords as bag

METADATA_ROOT = "..\\metadata\\"
DATA_ROOT = "..\\data\\"
ALL_DATA = DATA_ROOT + "data_thinned.csv"

class Info:
    def __init__(self):
        self.postDictionary = {} # dictionary of post objects (key is post id, value is post object)
        self.tagsCollected = [] # list of all tags collected (no duplicates, and single value of "[All_Tags]" if all tags are collected)
        self.topTags = {} # dictionary of top tags sorted by descending value (key is tag, value is number of times tag is used)
        self.topAdjectives = {} # dictionary of top adjectives sorted by descending value (key is adjective, value is number of times adjective is used)
        self.topWords = {} # dictionary of top words sorted by descending value (key is word, value is number of times word is used)
        self.topUsers = {} # [UNUSED]
        self.numPosts = 0 # number of unique posts collected
        self.numTags = -1 # number of unique tags collected, -1 if not yet calculated
        self.numUsers = -1 # number of unique users collected, -1 if not yet calculated
    
    # Add a list of posts to the Info object and update the number of posts
    def add_posts(self, posts):
        # Make the new post list into a dictionary
        postDict = util.posts_to_dict(posts)
        # Add the new posts to the post dictionary
        self.postDictionary = util.combine_dicts(self.postDictionary, postDict)
        # Update the number of posts
        self.numPosts = len(self.postDictionary)

    
    def __str__(self):
        info = "Current Analysis Information:\n"

        # Print which tags (if any or all) are collected
        if self.tagsCollected == "[All_Tags]":
            info += "Tags collected:\t\t\tAll tags collected\n"
        elif len(self.tagsCollected) == 0:
            info += "Tags collected:\t\t\tNo tags collected\n"
        else:
            info += "Tags collected:\t\t\t" + str(self.tagsCollected) + "\n"

        # Print number of posts collected
        info += "Number of posts collected:\t" + str(self.numPosts) + "\n"

        # Print number of users collected
        if self.numUsers != -1:
            info += "Number of unique users:\t\t" + str(self.numUsers) + "\n"
        else:
            info += "Number of unique users:\t\t[Not yet calculated]\n"
        
        # Print number of tags collected
        if self.numTags != -1:
            info += "Number of unique tags:\t\t" + str(self.numTags) + "\n"
        else:
            info += "Number of unique tags:\t\t[Not yet calculated]\n"
        
        # Print top 5 tags or fewer if there are less than 5 tags
        if len(self.topTags) == 0:
            info += "No top tags stored yet\n"
        else:
            numTagsPrinting = min(5, len(self.topTags))
            info += "\nTop " + str(numTagsPrinting) + " tags:\n"
            # Print top tags without removing them from the dictionary
            i = 0
            for key in self.topTags:
                if i == numTagsPrinting:
                    break
                info += key + ":\t" + str(self.topTags[key]) + "\n"
                i += 1
        
        # Print top 5 adjectives or fewer if there are less than 5 adjectives
        if len(self.topAdjectives) == 0:
            info += "\nNo top adjectives stored yet\n"
        else:
            numAdjectivesPrinting = min(5, len(self.topAdjectives))
            info += "\nTop " + str(numAdjectivesPrinting) + " adjectives:\n"
            # Print top adjectives without removing them from the dictionary
            i = 0
            for key in self.topAdjectives.keys():
                if i == numAdjectivesPrinting:
                    break
                info += key + ":\t" + str(self.topAdjectives[key]) + "\n"
                i += 1
        
        # Print top 5 words or fewer if there are less than 5 words
        if len(self.topWords) == 0:
            info += "\nNo top words stored yet\n"
        else:
            numWordsPrinting = min(5, len(self.topWords))
            info += "\nTop " + str(numWordsPrinting) + " words:\n"
            # Print top words without removing them from the dictionary
            i = 0
            for key in self.topWords.keys():
                if i == numWordsPrinting:
                    break
                info += key + ":\t" + str(self.topWords[key]) + "\n"
                i += 1

        return info


def main():
    info = Info()
    while(True):
        load_data(info)
        run_analysis(info)


# Loads data specified by the user into the Info object (or continue without doing so)
    # and updates the number of posts and hashtags collected
# Gives option to print out the data or quit
def load_data(info):
    # Setup choices
    validInput = ["1", "2", "Q", "q", "I", "i", "C", "c"]
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
        folder = util.tag_to_folder(hashtag)
        # use glob to get the csv file in the folder
        csvFile = glob.glob(DATA_ROOT + folder + "\\*.csv")

        if len(csvFile) == 0:
            print("No data found for hashtag '" + hashtag + "'.")
        
        else:
            posts = util.read_posts(csvFile[0])
            info.add_posts(posts)
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
    validInput = ["1", "2", "3", "4", "Q", "q", "I", "i", "C", "c"]
    usrChoice = -1
    # Ask for user input
    usrChoice = input("\n[1]Count number of unique tags\n[2]Count number of unique users\n[3]Calculate top 5 words\n[4]Calculate top 5 adjectives\n[Q]uit   | [I]nfo   | [C]ontinue\nUser Input: ").lower()
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
        # print(info.topTags)
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
        restart = True
    
    elif usrChoice == "c":
        print("Continuing...")
        return
    
    if restart:
        run_analysis(info) # restart function


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


# Calculates the top words in the posts in the Info object
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


# start main
if __name__ == "__main__":
    main()