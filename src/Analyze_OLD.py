import glob
import time
import sys
import os
import csv

from CollectData import Post
import Utilities as util
import BagOfWords as bag

METADATA_ROOT = "..\\metadata\\"
DATA_ROOT = "..\\data\\"
ERR_USAGE = "Usage:\nTo combine files of a tag:\npython Analyze.py -c <hashtag>\n\nTo find empty tag entries from files with a tag:\npython Analyze.py -e <hashtag>\n\nTo analyze a tag:\npython Analyze.py -a <hashtag> <[list of space-separated tags to check against]>\n\nTo cluster posts:\npython Analyze.py -u <hashtag> <number of clusters>"

def main():
    if len(sys.argv) < 3:
        print("Invalid number of arguments\n" + ERR_USAGE)
        return -1
    if sys.argv[1] == "-c":
        if len(sys.argv) == 3:
            tag = sys.argv[2]
            combine_files(tag)
            return 0
    if sys.argv[1] == "-e":
        tag = sys.argv[2]
        print("Finding posts with no tags in the data folder...\n")
        pull_empty_tags(tag)
        return 0
    if sys.argv[1] == "-a":
        myTag = sys.argv[2]
        list = []
        for i in range(3, len(sys.argv)):
            tag = "#" + sys.argv[i]
            list.append(tag)
        print("Analyzing all relevant files in the data folder...\n")
        analyze_tag(myTag, list)
        return 0
    if sys.argv[1] == "-u":
        myTag = sys.argv[2]
        numClusters = int(sys.argv[3])
        print("Clustering all relevant posts from the data folder...\n")
        cluster_posts(myTag, numClusters)
        return 0
    if sys.argv[1] == "-i":
        get_info()
        return 0
    print("Invalid usage\n" + ERR_USAGE)
    return -1


# Opens a file and returns a list of Post objects
# One Post object per line, and format is: "Post_ID: [id]	|Post_Code: [shortCode]	|Owner_ID: [ownerId]	|Likes: [likes]	|Time_Stamp: [timeStamp]	|Tags: [tags]	|Caption: [caption]"
def read_posts(filename):
    posts = []
    with open(filename, 'r', encoding="utf8") as f:
        for line in f:
            info = line.split("\t|")
            id = info[0].split("Post_ID:")[1].strip()
            shortCode = info[1].split("Post_Code:")[1].strip()
            ownerId = info[2].split("Owner_ID:")[1].strip()
            likes = int(info[3].split("Likes:")[1].strip())
            timeStamp = int(info[4].split("Time_Stamp:")[1].strip())
            tags = util.strToArr(info[5].split("Tags:")[1].strip())
            caption = ""
            for i in range(6, len(info)):
                caption += info[i]
                if i != len(info) - 1:
                    caption += " <BAR> "
            caption = caption.split("Caption:")[1].strip()

            post = Post(id, shortCode, ownerId, likes, timeStamp, tags, caption)
            posts.append(post)
    return posts

# Converts list of Post objects to a dictionary, using the id as a key and the Post object as the value
def posts_to_dict(posts):
    post_dict = {}
    for post in posts:
        post_dict[post.id] = post
    return post_dict


# Takes a tag and parses all files in the data folder, and creates a new combined file with all Post objects from matching files
# An optional parameter 'num_pages' can be passed in to only combine files with a certain number of pages in the filename
# Not passing in this parameter will have the function also look into output files of this function if they match the tag
def combine_files(myTag):
    # Get all files that match the tag and (optionally) number of pages
    filenames = util.get_filenames(myTag)
    
    # Loop through each filename, and combine the results into one dictionary
    combined_dict = {}
    for filename in filenames:
        posts = read_posts(filename)
        combined_dict = util.combine_dicts(combined_dict, posts_to_dict(posts))

    # Make a new list of all filenames but without the prefix DATA_ROOT
    cleanFilenames = []
    for filename in filenames:
        cleanFilenames.append(filename[len(DATA_ROOT):])

    # Create output file and copy in the data
    outputFilename = DATA_ROOT + util.tag_to_folder(myTag) + "\\" + myTag + "_" + str(len(combined_dict)) + "combined_" + str(int(time.time())) + ".txt"
    with open(outputFilename, 'w', encoding="utf8") as f:
        for key in combined_dict.keys():
            f.write(str(combined_dict[key]) + "\n")

    # Print out the filenames that were combined
    print("Combined " + str(len(cleanFilenames)) + " files:")
    for filename in cleanFilenames:
        print(filename)
    print("\nAll " + str(len(combined_dict.keys())) + " posts can be found in " + outputFilename) # print the output filename


def pull_empty_tags(myTag):
    # Get all files that match the tag
    filenames = util.get_filenames(myTag)
    
    # Loop through each filename, and combine the results into one dictionary
    combined_dict = {}
    for filename in filenames:
        posts = read_posts(filename)
        combined_dict = util.combine_dicts(combined_dict, posts_to_dict(posts))
    

    # Loop through dictionary and report posts that have an empty list of tags
    numPosts = len(combined_dict)
    emptyPosts = []
    empty_tags = 0
    for key in combined_dict.keys():
        if len(combined_dict[key].tags) == 0:
            empty_tags += 1
            emptyPosts.append(combined_dict[key])
    print("For #" + myTag + ": " + str(empty_tags) + "/" + str(numPosts) + " posts have no tags or ~" + str(int(1000*(empty_tags/numPosts))/10) + "%")


    # Output all posts with no tags to a file
    myTag = myTag.replace("*", "X")
    outputFilename = METADATA_ROOT + util.tag_to_folder(myTag) + "\\" + "_empty_" + myTag + "_" + str(len(emptyPosts)) + str(int(time.time())) + ".txt"
    with open(outputFilename, 'w', encoding="utf8") as f:
        for post in emptyPosts:
            f.write(str(post) + "\n")


def analyze_tag(myTag, checkAgainst = []):
    # Get all files that match the tag
    filenames = util.get_filenames(myTag)
    
    # Loop through each filename, and combine the results into one dictionary
    combined_dict = {}
    for filename in filenames:
        posts = read_posts(filename)
        nonemptyPosts = []
        for post in posts:
            if len(post.tags) > 0:
                nonemptyPosts.append(post)
        combined_dict = util.combine_dicts(combined_dict, posts_to_dict(nonemptyPosts))
    
    
    # Add all tags to dictionary, key is tag and value is occurrences of tag
    allTags = {}
    for key in combined_dict.keys():
        for tag in combined_dict[key].tags:
            tag = tag.lower()
            if tag in allTags.keys():
                allTags[tag] += 1
            else:
                allTags[tag] = 1
    
    print("There are " + str(len(combined_dict.keys())) + " posts with the tag #" + myTag)
    for tag in checkAgainst:
        numPosts = 0
        if tag in allTags.keys():
            numPosts = allTags[tag]
        print("There are " + str(numPosts) + "\tposts with the tag " + tag)

    # Sort allTags by value
    sortedTags = sorted(allTags.items(), key=lambda x: x[1], reverse=True)

    # Print out the top 100 tags
    print("\nTop 25 of " + str(len(allTags.keys())) + " tags for #" + myTag + ":")
    for i in range(25):
        print(str(sortedTags[i][0]) + ": " + str(sortedTags[i][1]))


# Function that makes clusters of posts containing a tag based on their caption
def cluster_posts(myTag, numClusters):
    print("Getting files...")
    # Get all files that match the tag
    filenames = util.get_filenames(myTag)

    # CODE INJECTION
    # filenames = [DATA_ROOT + "leavenotrace\\leavenotrace_7339combined_1643647807.txt"]

    # Loop through each filename, and combine the results into one dictionary
    print("Combining files and extracting entries...")
    combined_dict = {}
    for filename in filenames:
        posts = read_posts(filename)
        # Discard posts without the tag in their caption
        validPosts = []
        for post in posts:  
            if "#" + myTag in post.tags:
                validPosts.append(post)
        combined_dict = util.combine_dicts(combined_dict, posts_to_dict(validPosts))
    
    # Create a list of tuples of the form (post id, caption)
    print("Formatting and sorting data...")
    post_tuples = []
    for key in combined_dict.keys():
        post_tuples.append((key, combined_dict[key].caption))
    
    justCaptions = [x[1] for x in post_tuples]
    uniqueWords = bag.get_unique_words(justCaptions)
    # sort uniqueWords by descending frequency
    uniqueWords = sorted(uniqueWords.items(), key=lambda x: x[1], reverse=True)
    # Get top 100 words as a list of strings
    top100 = [x[0] for x in uniqueWords[:100]]
    print(top100)
    
    # Find the clusters
    print("Finding clusters...\n")
    myClusters, myCenters = bag.train(post_tuples, numClusters, top100)#bag.SPARSEBAG)

    # Make a list of tuples of the form (word, score) for each center where score is myCenters[i] and word is top100[i]
    # Then sort the list by score for each cluster
    print("Finding top words for each cluster...")
    clusterWords = []
    for i in range(numClusters):
        clusterWords.append(sorted([(top100[j], myCenters[i][j]) for j in range(len(top100))], reverse=False))
    # print(clusterWords)
    
    # Find the top ten words for each cluster using myCenters and top100
    topClusterWords = []
    for i in range(numClusters):
        topClusterWords.append(clusterWords[i][:10])


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
            print("\nPosts in cluster " + str(inputVal) + ": " + str(topClusterWords[inputVal-1]))
            for id in thinClusters[inputVal - 1]:
                print(combined_dict[id].postCode)
        else:
            print("\nInvalid input, closing program...")
            inputValid = False
    
# Function that grabs posts of all tags and puts them into a dictionary
# Prints stats like number of unique posts
def get_info():
    # Get all files from data folder
    # print("Getting file names...")
    # dataRes = os.listdir(DATA_ROOT)
    # tagFolders = []
    # for r in dataRes:
    #     if '.' not in r:
    #         tagFolders.append(DATA_ROOT + r + "\\")

    # filenames = []
    # for folder in tagFolders:
    #     files = os.listdir(folder)
    #     for file in files:
    #         if ".csv" not in file:
    #             filenames.append(str(folder) + str(file))


    # Loop through each filename, and combine the results into one dictionary
    print("Combining files and extracting entries...")
    allDataFilename = DATA_ROOT + "data_thinned.txt"
    combined_dict = {}
    allPosts = read_posts(allDataFilename)
    combined_dict = util.combine_dicts(combined_dict, posts_to_dict(allPosts))

    # Open files DATA_ROOT + "negative.txt" and DATA_ROOT + "positive.txt" and put all adjectives in a list
    positive = []
    negative = []
    with open(DATA_ROOT + "positive.txt", "r", encoding="utf8") as f:
        for line in f:
            positive.append(line.strip())
    with open(DATA_ROOT + "negative.txt", "r", encoding="utf8") as f:
        for line in f:
            negative.append(line.strip())
    
    adjectives = positive + negative

    adjDict = {}

    # For every post's caption, split the caption into words with util.split_caption(), and then go through each adjective and check if that adjective is in the post's list of words. If it is, increment the adjective's count in the dictionary.
    print("Counting adjectives...")
    counter = 0
    for key in combined_dict.keys():
        if counter % 1000 == 0:
            print(str(int(1000 * ((100*counter) / len(combined_dict.keys()))) / 1000) + "%")
        postWords = util.split_caption(combined_dict[key].caption)
        for adj in adjectives:
            if adj in postWords:
                if adj in adjDict.keys():
                    adjDict[adj] += 1
                else:
                    adjDict[adj] = 1
        counter += 1
    
    # Sort the dictionary by value
    sortedAdjDict = sorted(adjDict.items(), key=lambda x: x[1], reverse=True)

    # Output all sorted adjectives to a file DATA_ROOT + "sorted_adjectives.txt"
    with open(DATA_ROOT + "sorted_adjectives.txt", "w", encoding="utf8") as f:
        for item in sortedAdjDict:
            f.write(str(item[0]) + ": " + str(item[1]) + "\n")
    
    return 0

    # for filename in filenames:
    #     posts = read_posts(filename)
    #     # combined_dict = util.combine_dicts(combined_dict, posts_to_dict(posts))
    #     nonemptyPosts = []
    #     for post in posts:
    #         if len(post.tags) > 0:
    #             nonemptyPosts.append(post)
    #     combined_dict = util.combine_dicts(combined_dict, posts_to_dict(nonemptyPosts))
    
    # # Count the number of unique users
    # usersDict = {}
    # for key in combined_dict.keys():
    #     if combined_dict[key].ownerId in usersDict.keys():
    #         usersDict[combined_dict[key].ownerId] += 1
    #     else:
    #         usersDict[combined_dict[key].ownerId] = 1
    # print("There are " + str(len(usersDict.keys())) + " unique users")

    # # Sort the users by number of posts
    # sortedUsers = sorted(usersDict.items(), key=lambda x: x[1], reverse=True)
    # print("\nTop 100 users:")
    # for i in range(100):
    #     print(str(sortedUsers[i][0]) + ": " + str(sortedUsers[i][1]))
    
    print("\nCopying over English posts...")
    counter = 0
    slim_dict = {}
    for key in combined_dict.keys():
        if counter % 1000 == 0:
            print(str(int(1000 * ((100*counter) / len(combined_dict.keys()))) / 1000) + "%")
        if util.is_english(combined_dict[key].caption):
            slim_dict[key] = combined_dict[key]
        counter += 1
    
    # Print out the number of unique posts
    print("\nThere are " + str(len(combined_dict.keys())) + " unique posts")
    print("There are " + str(len(slim_dict.keys())) + " unique English posts")

    # Open a file to write all of the data to
    print("\nWriting data to file...")
    with open(DATA_ROOT + "data_thinned.txt", "w", encoding="utf8") as f:
        for key in slim_dict.keys():
            f.write(str(slim_dict[key]) + "\n")
    
    header = ["Post_ID", "Post_Code", "Owner_ID", "Likes", "Time_Stamp", "Tags", "Caption"]
    with open(DATA_ROOT + "data_thinned.csv", "w", encoding="utf8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for key in slim_dict.keys():
            writer.writerow(slim_dict[key].asArray())
    

# start main
if __name__ == "__main__":
    main()
