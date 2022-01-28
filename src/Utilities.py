import json

# Function that takes a JSON string as input and returns a JSON object
def read_json(json_str):
    json_obj = json.loads(json_str)
    return json_obj

# Function that takes a tag and number and makes a URL from it
def make_url(hashtag, num_posts, end_cursor):
    url = "https://www.instagram.com/graphql/query/?query_id=17875800862117404&variables=%7B%22tag_name%22%3A%22" + hashtag + "%22%2C%22first%22%3A" + str(num_posts)
    if end_cursor is not None:
        url += "%2C%22after%22%3A%22" + end_cursor + "%22"
    url += "%7D"
    return url

def strToArr(str):
    return str.replace('[','').replace(']','').replace("'", "").split(', ')
