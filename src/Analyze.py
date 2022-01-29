import glob
import time
# from re import search 

from CollectData import Post
import Utilities as util

DATA_ROOT = "..\\data\\"

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

    # Create output file and copy in the data
    outputFilename = DATA_ROOT + tag + "_" + str(len(combined_dict)) + "combined_" + str(int(time.time())) + ".txt"
    with open(outputFilename, 'w', encoding="utf8") as f:
        for key in combined_dict.keys():
            f.write(str(combined_dict[key]) + "\n")
    print("Results can be found in " + outputFilename) # print the output filename

