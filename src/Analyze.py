import time
import os
import csv

from Utilities import Post
from Utilities import PostSentiment
import Utilities as util
import BagOfWords as bag

from vader.vaderSentiment.vaderSentiment import NEGATE, SentimentIntensityAnalyzer

METADATA_ROOT = "../metadata/"
DATA_ROOT = "../data/"
ALL_DATA = DATA_ROOT + "data_thinned.csv"
RESULTS_ROOT = "../results/"
PROG_CHARS = "░▒▓█෴ᛞ០═" #unused


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
        self.posPosts = [] # list of post sentiment objects with positive sentiment
        self.negPosts = [] # list of post sentiment objects with negative sentiment
        self.neutralPosts = [] # list of post sentiment objects with neutral sentiment

        self.clusters = [] # list of clusters
        self.clusterWords = [] # list of the relevant words used in each cluster

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
    validInput = ["1", "2", "3", "4", "5", "6", "q", "i","c"]
    usrChoice = -1

    # Ask for user input
    optionStr = """
[1]Count number of unique tags
[2]Count number of unique users
[3]Calculate top 5 words
[4]Calculate top 5 adjectives
[5]Calculate sentiment
[6]Cluster posts
[Q]uit   | [I]nfo   | [C]ontinue\nUser Input: """

    usrChoice = input(optionStr).lower()
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
    
    elif usrChoice == "6":
        print("Clustering posts...")
        clusterPosts(info)
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
    idx = 0
    total = len(info.postDictionary)
    for key in info.postDictionary:
        post = info.postDictionary[key]
        lowerTags = [tag.lower() for tag in post.tags]
        for tag in lowerTags:
            if tag not in info.topTags:
                info.topTags[tag] = 1
            else:
                info.topTags[tag] += 1
        idx += 1
        if idx % (int(total / 1000) + 1) == 0 or idx == total:
            util.printProgressBar(idx, total, prefix = 'Progress:', suffix = 'Complete', length = 50)
    
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
    idx = 0
    total = len(info.postDictionary)
    for key in info.postDictionary:
        post = info.postDictionary[key]
        if post.ownerId not in info.topUsers:
            info.topUsers[post.ownerId] = 1
        else:
            info.topUsers[post.ownerId] += 1
        idx += 1
        if idx % (int(total / 1000) + 1) == 0 or idx == total:
            util.printProgressBar(idx, total, prefix = 'Progress:', suffix = 'Complete', length = 50)

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
    idx = 0
    total = len(info.postDictionary)
    for key in info.postDictionary:
        post = info.postDictionary[key]
        words = util.split_caption(post.caption)
        for word in words:
            if not word in commonWords and word.isalpha() and len(word) > 2:
                if word not in info.topWords:
                    info.topWords[word] = 1
                else:
                    info.topWords[word] += 1
        idx += 1
        if idx % (int(total / 1000) + 1) == 0 or idx == total:
            util.printProgressBar(idx, total, prefix = 'Progress:', suffix = 'Complete', length = 50)
    
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
    posAdjs = []
    negAdjs = []
    with open(DATA_ROOT + "positive.txt", "r") as f:
        for line in f:
            posAdjs.append(line.strip())
    with open(DATA_ROOT + "negative.txt", "r") as f:
        for line in f:
            negAdjs.append(line.strip())
    
    adjectives.extend(posAdjs)
    adjectives.extend(negAdjs)


    # Get all words from all posts and record the counts of each relevant adjective
    idx = 0
    total = len(info.postDictionary)
    for key in info.postDictionary:
        post = info.postDictionary[key]
        words = util.split_caption(post.caption)
        for adj in adjectives:
            if adj in words:
                if adj not in info.topAdjectives:
                    info.topAdjectives[adj] = 1
                else:
                    info.topAdjectives[adj] += 1
        idx += 1
        if idx % (int(total / 1000) + 1) == 0 or idx == total:
            util.printProgressBar(idx, total, prefix = 'Progress:', suffix = 'Complete', length = 50)
    
    # Sort adjectives by count
    sortedWords = sorted(info.topAdjectives.items(), key=lambda x: x[1], reverse=True)
    info.topAdjectives = {}
    for word in sortedWords:
        info.topAdjectives[word[0]] = word[1]

def get_sentiment(sentence, analyzer=SentimentIntensityAnalyzer()):
    words_list = analyzer.list_of_words(sentence)
    score_list = analyzer.scores_of_each_words(sentence)
    wordScoreTuples = []
    if len(words_list) != len(score_list):
        print("Error: words_list and score_list are not the same length", len(words_list), len(score_list))
        print(words_list)
        print(score_list)
        # print(sentence)
    for i in range(len(words_list)):
        wordI = words_list[i]
        scoreI = score_list[i]
        wordScoreTuples.append((wordI, scoreI))
    # print(words_list)
    # print(score_list)

    lex_words = analyzer.list_of_lexicon_words(words_list)
    lex_tuples = [(lex, analyzer.lexicon[lex.lower()]) for lex in lex_words]
    # print(lex_tuples)

    negate_count = 0
    negate_words = []
    for word in words_list:
                if word in NEGATE:
                    negate_count += 1
                    negate_words.append(word)

    vs = analyzer.polarity_scores(sentence)
    # print(vs)
    total_score = vs["compound"]
    # if total_score >= 0.5:
    #     pass# print("The sentence in overall had positive sentiment with compounding score")
    # elif total_score >= 0.25 and total_score < 0.5:
    #     pass# print("The sentence in overall had slightly positive sentiment with compounding score")
    # elif total_score >= -0.25 and total_score < 0.25:
    #     pass# print("The sentence in overall had neutral sentiment with compounding score")
    # elif total_score > -0.5 and total_score < -0.25:
    #     pass# print("The sentence in overall had slightly negative sentiment with compounding score")
    # elif total_score <= -0.5:
    #     pass# print("The sentence in overall had negative sentiment with compounding score")

    return wordScoreTuples, lex_tuples, negate_words, vs

# Calculates the sentiment of the posts in the Info object
# Stores post ids in info.posPostIds and info.negPostIds
def calculateSentiment(info):
    # Start sentiment analyzer
    analyzer = SentimentIntensityAnalyzer()
    
    # Check all post captions for positive and negative adjectives
    # If a post contains more positive adjectives than negative, it is considered positive
    info.posPosts = []
    info.negPosts = []
    info.neutralPosts = []
    postSentiments = []
    idx = 0
    total = len(info.postDictionary)
    if total == 0:
        print("No posts to analyze")
        return
    for key in info.postDictionary:
        post = info.postDictionary[key]
        newCaption = util.split_caption(post.caption)
        newCaption = ' '.join(newCaption)
        wordScoreTuples, lex_tuples, negate_words, vs = get_sentiment(newCaption)
        sentimentPost = PostSentiment(post, wordScoreTuples, lex_tuples, negate_words, vs, vs["compound"])

        if sentimentPost.score >= 0.5:
            info.posPosts.append(sentimentPost)
        elif sentimentPost.score <= -0.5:
            info.negPosts.append(sentimentPost)
        else:
            info.neutralPosts.append(sentimentPost)

        postSentiments.append(sentimentPost)
        idx += 1
        if idx % (int(total / 1000) + 1) == 0 or idx == total:
            util.printProgressBar(idx, total, prefix = 'Progress:', suffix = 'Complete', length = 50)
    
    info.sentimentCalculated = True

def clusterPosts(info):
    # Get all posts
    posts = []
    for key in info.postDictionary:
        posts.append(info.postDictionary[key])
    
    # Create a list of tuples of the form (post id, caption)
    print("Formatting and sorting data...")
    postTuples = []
    for post in posts:
        postTuples.append((post.id, post.caption))

    # Get top 500 words
    # calculateTopWords(info)
    # top500 = []
    # idx = 0
    # for word in info.topWords:
    #     top500.append(word)
    #     idx += 1
    #     if idx >= 500:
    #         break

    # justCaptions = [x[1] for x in postTuples]
    # uniqueWords = bag.get_unique_words(justCaptions)
    # sort uniqueWords by descending frequency
    # uniqueWords = sorted(uniqueWords.items(), key=lambda x: x[1], reverse=True)
    # Get top 500 words as a list of strings
    # top500 = [x[0] for x in uniqueWords[:10]]

    top500 = bag.SPARSEBAG

    # Find the clusters
    print("Finding clusters...\n")
    myClusters, myCenters = bag.train(postTuples, bag.NUMCLUSTERS, top500)
    print("Centers:")
    print(myCenters)

    info.clusters = myClusters

    # Make a list of tuples of the form (word, score) for each center where score is myCenters[i] and word is top100[i]
    # Then sort the list by score for each cluster
    print("Finding top words for each cluster...")
    clusterWords = []
    for i in range(bag.NUMCLUSTERS):
        clusterWords.append(sorted([(top500[j], myCenters[i][j]) for j in range(len(top500))], reverse=False))
    print(clusterWords)

    info.clusterWords = clusterWords
    
    # Find the top ten words for each cluster using myCenters and top100
    topClusterWords = []
    for i in range(bag.NUMCLUSTERS):
        topClusterWords.append(clusterWords[i][:10])
    print(topClusterWords)


    emptyClusters = 0
    for i in range(len(myClusters)):
        print("Length of cluster " + str(i+1) + ": " + str(len(myClusters[i])))
        if len(myClusters[i]) == 0:
            emptyClusters += 1
    print("There are " + str(len(myClusters) - emptyClusters) + " non-empty clusters")
    
    thinClusters = bag.thin_clusters(myClusters, myCenters, 3)

    inputValid = True
    while inputValid:
        inputVal = int(input("\nEnter a cluster number to see the top posts in that cluster: "))
        if inputVal > 0 and inputVal <= len(myClusters):
            sortedClusterWords = sorted(clusterWords[inputVal-1], key=lambda x: x[1], reverse=True)
            print("\nPosts in cluster " + str(inputVal) + ": " + str(sortedClusterWords))
            for id in thinClusters[inputVal - 1]:
                print(info.postDictionary[id[0]].postCode + "  " + str(id[1]))
        else:
            print("\nInvalid input, closing program...")
            inputValid = False


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
        info += "Number of positive posts:\t" + str(len(infoObj.posPosts)) + "\n"
    else:
        info += "Number of positive posts:\t[Not yet calculated]\n"
    
    # Print number of negative posts
    if infoObj.sentimentCalculated:
        info += "Number of negative posts:\t" + str(len(infoObj.negPosts)) + "\n"
    else:
        info += "Number of negative posts:\t[Not yet calculated]\n"
    
    # Print number of neutral posts
    if infoObj.sentimentCalculated:
        info += "Number of neutral posts:\t" + str(len(infoObj.neutralPosts)) + "\n"
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
        with open(newFolderPath + "positive_posts.csv", "w", encoding="utf8", newline='') as f:
            writer = csv.writer(f)
            if len(infoObj.posPosts) != 0:
                writer.writerow(infoObj.posPosts[0].getHeader())
            for post in infoObj.posPosts:
                writer.writerow(post.asArray())
        
        with open(newFolderPath + "negative_posts.csv", "w", encoding="utf8", newline='') as f:
            writer = csv.writer(f)
            if len(infoObj.negPosts) != 0:
                writer.writerow(infoObj.negPosts[0].getHeader())
            for post in infoObj.negPosts:
                writer.writerow(post.asArray())
        
        with open(newFolderPath + "neutral_posts.csv", "w", encoding="utf8", newline='') as f:
            writer = csv.writer(f)
            if len(infoObj.neutralPosts) != 0:
                writer.writerow(infoObj.neutralPosts[0].getHeader())
            for post in infoObj.neutralPosts:
                writer.writerow(post.asArray())
        
    if infoObj.clusters != []:
        header = ["Post_ID", "Post_Code", "Owner_ID", "Likes", "Time_Stamp", "Tags", "Caption"]
        # Make a folder for the clusters called "clusters"
        if not os.path.exists(newFolderPath + "clusters"):
            os.makedirs(newFolderPath + "clusters")

        clustersFolderPath = newFolderPath + "clusters/"
        # Print the posts in each cluster to a .csv file called "cluster_#.csv"
        for i in range(len(infoObj.clusters)):
            with open(clustersFolderPath + "cluster_" + str(i+1) + ".csv", "w", encoding="utf8", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(header)
                for postTuple in infoObj.clusters[i]:
                    writer.writerow(infoObj.postDictionary[postTuple[0]].asArray())
        
        # Print the cluster words to .txt files
        for i in range(len(infoObj.clusters)):
            with open(clustersFolderPath + "clusterWords_" + str(i+1) + "_words.txt", "w", encoding="utf8") as f:
                sortedClusterWords = sorted(infoObj.clusterWords[i], key=lambda x: x[1], reverse=True)
                for wordTuple in sortedClusterWords:
                    f.write(str(wordTuple[0]) + ": " + str(wordTuple[1]) + "\n")




# start main
if __name__ == "__main__":
    main()
