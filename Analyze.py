from CollectData import Post
import Utilities as util

# Opens a file and returns a list of Post objects
# One Post object per line, and format is: "Post id: [id] | Post_Code: [shortCode] | Likes: [likes] | Time Stamp: [timeStamp] | Tags: [tags] | Caption: [caption]"
def read_posts(filename):
    posts = []
    with open(filename, 'r', encoding="utf8") as f:
        for line in f:
            info = line.split("|")
            id = info[0].split(":")[1].strip()
            shortCode = info[1].split(":")[1].strip()
            likes = int(info[2].split(":")[1].strip())
            timeStamp = int(info[3].split(":")[1].strip())
            tags = util.strToArr(info[4].split("Tags:")[1].strip())
            caption = info[5].split(":")[1].strip()

            post = Post(id, shortCode, likes, timeStamp, tags, caption)
            posts.append(post)
    return posts

# Converts list of Post objects to a dictionary, using the id as a key and the Post object as the value
def posts_to_dict(posts):
    post_dict = {}
    for post in posts:
        post_dict[post.id] = post
    return post_dict

posts = read_posts("../Data/leavenotrace_3pages_1643404444.txt")
print(str(posts[0]))