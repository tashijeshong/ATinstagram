import json
import glob
import re
from langdetect import detect_langs

TAGTERMINATORS = [' ', '#', '\n', '\r', '\t', ',', '.', '&', '\'', '\"', ':', ';', '!', '?', '-', '_', '+', '=', '*', '%', '$', '@', '^', '&', '|', '~', '`', '(', ')', '{', '}', '[', ']', '<', '>', '/', '\\', '\u3000']
METADATA_ROOT = "..\\metadata\\"
DATA_ROOT = "..\\data\\"

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
    return glob.glob(DATA_ROOT + folder + "\\" + tag + "_*.txt")


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

class Post:
    def __init__(self, id, postCode, ownerId, likes, timeStamp, tags, caption):
        self.id = str(id)
        self.postCode = str(postCode)
        self.ownerId = str(ownerId)
        self.likes = int(likes)
        self.timeStamp = int(timeStamp)
        self.tags = tags # list of strings
        self.caption = str(caption)

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
    caption = remove_emoji(caption).lower().encode("ascii", "ignore").decode()
    caption = caption.replace("<br>", " ").replace("&nbsp;", " ")
    # Split the caption into words
    words = caption.split()
    # Remove punctuation
    words = [word.strip(',.;:!?)(+-_=*&^][}{|•—….“”"\'~`<>/\\') for word in words]
    # Remove empty words
    words = [word for word in words if word]
    
    return words # need to remove elements that are just '#'
                 # potentially replace special characters with spaces (except for single quote "'") first
