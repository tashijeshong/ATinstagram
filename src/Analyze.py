import glob
import time
import sys

from CollectData import Post
import Utilities as util
import BagOfWords as bag

METADATA_ROOT = "..\\metadata\\"
DATA_ROOT = "..\\data\\"
ERR_USAGE = "Usage:\nTo combine files of a tag:\npython Analyze.py -c <hashtag>\npython Analyze.py -c <hashtag> <num_pages>\n\nTo find empty tag entries from files with a tag:\npython Analyze.py -e <hashtag>\n\nTo analyze a tag:\npython Analyze.py -a <hashtag> <[list of space-separated tags to check against]>\n\nTo cluster posts:\npython Analyze.py -u <hashtag> <number of clusters>"

def main():
    if len(sys.argv) < 3:
        print("Invalid number of arguments\n" + ERR_USAGE)
        return -1
    if sys.argv[1] == "-c":
        if len(sys.argv) == 3:
            tag = sys.argv[2]
            combine_files(tag)
            return 0
        if len(sys.argv) == 4:
            tag = sys.argv[2]
            num_pages = int(sys.argv[3])
            combine_files(tag, num_pages)
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
    print("Invalid usage\n" + ERR_USAGE)


# Opens a file and returns a list of Post objects
# One Post object per line, and format is: "Post id: [id] | Post_Code: [shortCode] | Likes: [likes] | Time Stamp: [timeStamp] | Tags: [tags] | Caption: [caption]"
def read_posts(filename):
    posts = []
    with open(filename, 'r', encoding="utf8") as f:
        for line in f:
            info = line.split(" | ")
            id = info[0].split("Post_ID:")[1].strip()
            shortCode = info[1].split("Post_Code:")[1].strip()
            likes = int(info[2].split("Likes:")[1].strip())
            timeStamp = int(info[3].split("Time Stamp:")[1].strip())
            tags = util.strToArr(info[4].split("Tags:")[1].strip())
            caption = ""
            for i in range(5, len(info)):
                caption += info[i]
                if i != len(info) - 1:
                    caption += " <\\BAR> "
            caption = caption.split("Caption:")[1].strip()

            post = Post(id, shortCode, likes, timeStamp, tags, caption)
            posts.append(post)
    return posts

# Converts list of Post objects to a dictionary, using the id as a key and the Post object as the value
def posts_to_dict(posts):
    post_dict = {}
    for post in posts:
        post_dict[post.id] = post
    return post_dict

# Combines two dictionaries of Post objects, and returns a dictionary of Post objects
# For duplicates, the Post object with more likes is used
def combine_dicts(dict1, dict2):
    # if either dictionary is empty, return the other dictionary
    if len(dict1) == 0:
        return dict2
    if len(dict2) == 0:
        return dict1

    combined_dict = {}
    for key1 in dict1.keys():
        combined_dict[key1] = dict1[key1]
    for key2 in dict2.keys():
        if key2 in combined_dict.keys():
            if combined_dict[key2].likes < dict2[key2].likes: # add Post object with more likes
                combined_dict[key2] = dict2[key2]
        else:
            combined_dict[key2] = dict2[key2] # add new Post objects
    return combined_dict


# Takes a tag and parses all files in the data folder, and creates a new combined file with all Post objects from matching files
# An optional parameter 'num_pages' can be passed in to only combine files with a certain number of pages in the filename
# Not passing in this parameter will have the function also look into output files of this function if they match the tag
def combine_files(tag, num_pages=None):
    # Get all files that match the tag and (optionally) number of pages
    searchFor = DATA_ROOT + tag + "_"
    if num_pages is not None:
        searchFor += "*pages_"
    searchFor += "*.txt"
    filenames = glob.glob(searchFor)
    
    # Loop through each filename, and combine the results into one dictionary
    combined_dict = {}
    for filename in filenames:
        posts = read_posts(filename)
        combined_dict = combine_dicts(combined_dict, posts_to_dict(posts))

    # Make a new list of all filenames but without the prefix DATA_ROOT
    cleanFilenames = []
    for filename in filenames:
        cleanFilenames.append(filename[len(DATA_ROOT):])

    # Create output file and copy in the data
    outputFilename = DATA_ROOT + tag + "_" + str(len(combined_dict)) + "combined_" + str(int(time.time())) + ".txt"
    with open(outputFilename, 'w', encoding="utf8") as f:
        for key in combined_dict.keys():
            f.write(str(combined_dict[key]) + "\n")

    # Print out the filenames that were combined
    print("Combined " + str(len(cleanFilenames)) + " files:")
    for filename in cleanFilenames:
        print(filename)
    print("\nAll " + str(len(combined_dict.keys())) + " posts can be found in " + outputFilename) # print the output filename


def pull_empty_tags(tag):
    # Get all files that match the tag and (optionally) number of pages
    searchFor = DATA_ROOT + tag + "_*.txt"
    filenames = glob.glob(searchFor)
    
    # Loop through each filename, and combine the results into one dictionary
    combined_dict = {}
    for filename in filenames:
        posts = read_posts(filename)
        combined_dict = combine_dicts(combined_dict, posts_to_dict(posts))
    

    # Loop through dictionary and report posts that have an empty list of tags
    numPosts = len(combined_dict)
    emptyPosts = []
    empty_tags = 0
    for key in combined_dict.keys():
        if len(combined_dict[key].tags) == 0:
            empty_tags += 1
            emptyPosts.append(combined_dict[key])
    print("For #" + tag + ": " + str(empty_tags) + "/" + str(numPosts) + " posts have no tags or ~" + str(int(1000*(empty_tags/numPosts))/10) + "%")


    # Output all posts with no tags to a file
    outputFilename = METADATA_ROOT + "_empty_" + tag + "_" + str(len(emptyPosts)) + str(int(time.time())) + ".txt"
    with open(outputFilename, 'w', encoding="utf8") as f:
        for post in emptyPosts:
            f.write(str(post) + "\n")


def analyze_tag(myTag, checkAgainst = []):
    # Get all files that match the tag
    searchFor = DATA_ROOT + myTag + "_*.txt"
    filenames = glob.glob(searchFor)
    
    # Loop through each filename, and combine the results into one dictionary
    combined_dict = {}
    for filename in filenames:
        posts = read_posts(filename)
        nonemptyPosts = []
        for post in posts:
            if len(post.tags) > 0:
                nonemptyPosts.append(post)
        combined_dict = combine_dicts(combined_dict, posts_to_dict(nonemptyPosts))
    
    
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
def cluster_posts(tag, numClusters):
    # Get all files that match the tag
    searchFor = DATA_ROOT + tag + "_*.txt"
    filenames = glob.glob(searchFor)

    # CODE INJECTION
    # filenames = [DATA_ROOT + "leavenotrace_7339combined_1643647807.txt"]

    # Loop through each filename, and combine the results into one dictionary
    combined_dict = {}
    for filename in filenames:
        posts = read_posts(filename)
        # Discard posts without the tag in their caption
        validPosts = []
        for post in posts:  
            if "#" + tag in post.tags:
                validPosts.append(post)
        combined_dict = combine_dicts(combined_dict, posts_to_dict(validPosts))
    
    # Create a list of tuples of the form (post id, caption)
    post_tuples = []
    for key in combined_dict.keys():
        post_tuples.append((key, combined_dict[key].caption))
    
    # Find the clusters
    myClusters, myCenters = bag.train(post_tuples, numClusters)

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
            print("\nPosts in cluster " + str(inputVal) + ":")
            for id in thinClusters[inputVal - 1]:
                print(combined_dict[id].postCode)
        else:
            print("\nInvalid input, closing program...")
            inputValid = False
    

# start main
if __name__ == "__main__":
    main()
