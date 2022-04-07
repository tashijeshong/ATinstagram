import json
import glob
import re
import time
import csv
from langdetect import detect_langs

TAGTERMINATORS = [' ', '#', '\n', '\r', '\t', ',', '.', '&', '\'', '\"', ':', ';', '!', '?', '-', '_', '+', '=', '*', '%', '$', '@', '^', '&', '|', '~', '`', '(', ')', '{', '}', '[', ']', '<', '>', '/', '\\', '\u3000']
METADATA_ROOT = "../metadata/"
DATA_ROOT = "../data/"

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
    
    def getHeader(self):
        return ["Post_ID", "Post_Code", "Owner_ID", "Likes", "Time_Stamp", "Tags", "Caption"]

    def asArray(self):
        return [self.id, self.postCode, self.ownerId, self.likes, self.timeStamp, self.tags, self.caption]

    def timeToStr(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.timeStamp))


class PostSentiment:
    def __init__(self, post, wordScoreTuples, lexTuples, negationWords, sentimentDict, score):
        self.post = post
        self.wordScoreTuples = wordScoreTuples
        self.lexTuples = lexTuples
        self.negationWords = negationWords
        self.sentimentDict = sentimentDict
        self.score = score

    def __str__(self):
        return str(self.post) + "\t|Word_Score: " + str(self.wordScoreTuples) + "\t|Lex_Score: " + str(self.lexTuples) + "\t|Negation_Words: " + str(self.negationWords) + "\t|Sentiment_Scores: " + str(self.sentimentDict) + "\t|Score: " + str(self.score)
    
    def getHeader(self):
        return self.post.getHeader() + ["Word_Score", "Lex_Score", "Negation_Words", "Sentiment_Scores", "Score"]

    def asArray(self):
        return self.post.asArray() + [self.wordScoreTuples, self.lexTuples, self.negationWords, self.sentimentDict, self.score]

# Opens a file and returns a list of Post objects
# One Post object per line, and format is: "Post_ID: [id]	|Post_Code: [shortCode]	|Owner_ID: [ownerId]	|Likes: [likes]	|Time_Stamp: [timeStamp]	|Tags: [tags]	|Caption: [caption]"
def read_posts(filename):
    extension = filename.split('.')[-1]
    if extension == "txt":
        return read_txt(filename)
    elif extension == "csv":
        return read_csv(filename)
    else:
        exit("Invalid file extension '" + extension + "' from file '" + filename + "'")
        

# Function that takes a .txt filename and returns a list of post objects
# Example: read_txt("../data/data_thinned.txt")
def read_txt(filename):
    posts = []
    with open(filename, 'r', encoding="utf8") as f:
        for line in f:
            info = line.split("\t|")
            id = info[0].split("Post_ID:")[1].strip()
            shortCode = info[1].split("Post_Code:")[1].strip()
            ownerId = info[2].split("Owner_ID:")[1].strip()
            likes = int(info[3].split("Likes:")[1].strip())
            timeStamp = int(info[4].split("Time_Stamp:")[1].strip())
            tags = strToArr(info[5].split("Tags:")[1].strip())
            caption = ""
            for i in range(6, len(info)):
                caption += info[i]
                if i != len(info) - 1:
                    caption += " | "
            caption = caption.split("Caption:")[1].strip()

            post = Post(id, shortCode, ownerId, likes, timeStamp, tags, caption)
            posts.append(post)
    return posts


# Function that takes a .csv filename and returns a list of post objects
# Example: read_csv("../data/data_thinned.csv")
def read_csv(filename):
    posts = []
    with open(filename, 'r', encoding="utf8") as f:
        reader = csv.reader(f, delimiter=',')
        # Skip header
        next(reader)
        for row in reader:
            id = row[0]
            shortCode = row[1]
            ownerId = row[2]
            likes = int(row[3])
            timeStamp = int(row[4])
            tags = strToArr(row[5])
            caption = row[6]
            post = Post(id, shortCode, ownerId, likes, timeStamp, tags, caption)
            posts.append(post)
    return posts

# Converts list of Post objects to a dictionary, using the id as a key and the Post object as the value
def posts_to_dict(posts):
    post_dict = {}
    for post in posts:
        post_dict[post.id] = post
    return post_dict

# Function that takes a JSON string as input and returns a JSON object
def read_json(json_str):
    json_obj = json.loads(json_str)
    return json_obj

# Function that takes a tag and number and makes a URL from it
def make_url(hashtag, num_posts, end_cursor=None):
    url = "https://www.instagram.com/graphql/query/?query_id=17875800862117404&variables=%7B%22tag_name%22%3A%22" + hashtag + "%22%2C%22first%22%3A" + str(num_posts)
    if end_cursor is not None:
        url += "%2C%22after%22%3A%22" + end_cursor + "%22"
    url += "%7D"
    return url

# Function that takes a string representation of an array and returns it as an array
def strToArr(str):
    new_str = str.replace('[','').replace(']','').replace("'", "")
    if new_str == "":
        return []
    return new_str.split(', ')

# Mostly good function that determines if a character is a letter or not (multilingual support)
def is_letter(c):
    if ord(c) <= 255:
        return c.isalpha()
    if ord(c) >= 8189 and ord(c) <= 11903:
        return False # Symbols
    if ord(c) >= 12272 and ord(c) <= 12351:
        return False # More symbols
    if ord(c) >= 55204 and ord(c) <= 63743:
        return False
    if ord(c) >= 65020 and ord(c) <= 65135:
        return False
    if ord(c) >= 65277 and ord(c) <= 65280:
        return False
    if ord(c) >= 65281 and ord(c) <= 65374:
        newChar = chr(ord(c) - 65248)
        if newChar.isalnum():
            return True
    if ord(c) >= 65377:
        return False
    return True

# Get the name of the folder that a given tag is in
# Replaces non-alphabetic characters with 'X'
def tag_to_folder(tag):
    folder = ""
    for c in tag:
        if c.isalpha():
            folder += c
        else:
            folder += "X"
    return folder

# This function takes a tag and returns a list of filenames that start with that tag
# Uses the tag_to_folder function to get the folder name
def get_filenames(tag):
    folder = tag_to_folder(tag)
    return glob.glob(DATA_ROOT + folder + "/" + tag + "_*.txt")


# This function takes a description and returns an array of cleaned tags
def desc_to_tags(desc):
    cleanTags = []
    tmpTag = ""
    # add every tag to tmpTag
    for i in range(len(desc)):
        if desc[i] == '#':
            tmpTag += '#'
            i = i + 1
            if i >= len(desc):
                break
            while(desc[i] not in TAGTERMINATORS):
                tmpTag += desc[i]
                i = i + 1
                if i >= len(desc):
                    break
            tmpTag += ' '
    tags = tmpTag.split(' ')
        
    for tag in tags:
        if len(tag) > 1:
            cleanTags.append(tag)
    return cleanTags

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

def remove_emoji(text):
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U0001F1F2-\U0001F1F4"  # Macau flag
        u"\U0001F1E6-\U0001F1FF"  # flags
        u"\U0001F600-\U0001F64F"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U0001F1F2"
        u"\U0001F1F4"
        u"\U0001F620"
        u"\u200d"
        u"\u2640-\u2642"
        u"\U00002702-\U000027B0" # Dingbats
        u"\U000024C2-\U0001F251" # Enclosed Characters
        u"\U00002122-\U00002B55" # Uncategorized
        u"\U00003030-\U00003299" # Uncategorized
        u"\U0001F004-\U0001F0CF"
        u"\U0001F900-\U0001F9FF" # Unicode 9.0
        u"\U0001F780-\U0001F7FF" # Geometry shapes Unicode 12.0
        u"\U0001FA70-\U0001FAFF" # Symbols and Pictographs Extended-A
        # line 130 to 137 are emojis that I added. It removes all emojis from 500 pages dataset
        "]+", flags=re.UNICODE)

    refined_text = emoji_pattern.sub(r'', text)
    return refined_text

special_char = "!$%^&*().,;-?-~@':></[]|0123456789+`" # removed # symbol from the list


# Pass in any caption, and this will return True if it is in English and False if it is in another language
# !! Returns None if the post has no identifiable language !!
def is_english(caption):
    caption = caption.replace("<br>", "").replace("&nbsp;", " ").replace('_', ' ')
    caption = remove_emoji(caption)
    for char in special_char:
        caption = caption.replace(char, "")
    
    capSplit = caption.split('#')
    if len(capSplit[0]) > 15:
        caption = capSplit[0]

    res = None
    try:
        res = detect_langs(caption)[0].lang == "en"
    except:
        return None
    return res

# Function that splits a caption into its constituent words
def split_caption(caption):
    # Clean up some weirdness of the caption
    appPattern = re.compile("["
        u"\U00002019-\U00002019"  # apostrophe
        "]+", flags=re.UNICODE)
    caption = appPattern.sub(r"'", caption)

    appPattern = re.compile("["
        u"\U0000201C-\U0000201D"  # opening and closing double quotes
        "]+", flags=re.UNICODE)
    caption = appPattern.sub(r'"', caption)

    caption = remove_emoji(caption).lower().encode("ascii", "ignore").decode()
    caption = caption.replace("<br>", " ").replace("&nbsp;", " ")
    # Split the caption into words
    words = caption.split()
    # Remove punctuation
    words = [word.strip(',.;:!?)(+-_=*&^][}{|•—….“”"\'~`<>/\\') for word in words]
    # Remove empty words
    words = [word for word in words if word and word != '#']
    
    return words # need to remove elements that are just '#'
                 # potentially replace special characters with spaces (except for single quote "'") first


### FOLLOWING FUNCTION ADAPTED FROM HERE: https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters
# Print iterations progress
def printProgressBar(iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, chars = '░▒▓█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    idx = int((iteration / total) * len(chars))
    if idx == len(chars):
        idx -= 1
    fill = chars[idx]
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()
### END OF FUNCTION ADAPTED FROM HERE: https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters
