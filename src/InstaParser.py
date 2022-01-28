import json

BASE = "../data/"
TAGTERMINATORS = [' ', '#', '\n', '\r', '\t', ',', '.', '&', '\'', '\"', ':', ';', '!', '?', '-', '_', '+', '=', '*', '%', '$', '@', '^', '&', '|', '~', '`', '(', ')', '{', '}', '[', ']', '<', '>', '/', '\\', '\u3000']

# This is the main function that runs the program
def main():
    file1 = BASE + "res1.txt"
    file2 = BASE + "res2.txt"
    file3 = BASE + "res3.txt"
    json1 = open(file1, 'r', encoding="utf8").read()
    json2 = open(file2, 'r', encoding="utf8").read()
    json3 = open(file3, 'r', encoding="utf8").read()

    tag1 = all_tags(json1) # extracts all tags from a file
    print(tag1)
    tag2 = all_tags(json2)
    tag3 = all_tags(json3)

    allTags = combine_tags(tag1, tag2) # combines two results into one (assumes that their contents are mutually exclusive, will program a check in later)
    allTags = combine_tags(allTags, tag3)
    # print(top_tags(allTags, 0.25)) # prints the top tags of combined results (top 25%)
    print(order_tags(allTags))





# This function parses a JSON formatted string, searches for the description field of all posts
# and returns an array of all descriptions
def parse_json(json):
    ans = []
    json = read_json(json)
    for i in range(len(json['data']['hashtag']['edge_hashtag_to_media']['edges'])):
        edge = json['data']['hashtag']['edge_hashtag_to_media']['edges'][i]['node']['edge_media_to_caption']['edges']
        if len(edge) > 0: # checks if a caption exists
            ans.append(edge[0]['node']['text'])
        else:
            ans.append("")

    return ans

# This function takes a description and returns an array of cleaned tags
def parse_tag(desc):
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

# This function parses an array of descriptions and outputs an array of tags
# It also removes all punctuation and whitespace from tags
def parse_tags(descriptions):
    cleanTags = []
    for desc in descriptions:
        desc_tags = parse_tag(desc)
        cleanTags.extend(desc_tags)

    return cleanTags


# This function takes an array of cleaned tags and returns dictionary of each tag (key) and its frequency (value)
def tag_freq(tags):
    tagFreq = {}
    for tag in tags:
        if tag in tagFreq:
            tagFreq[tag] = tagFreq[tag] + 1
        else:
            tagFreq[tag] = 1
    return tagFreq

# This function returns a subset dictionary of tags that are in the top x% of tag frequencies
def top_tags(tags, tagFreq=0.1):
    if tagFreq > 1 or tagFreq < 0:
        print("Invalid tag frequency, setting to default 0.1")
        tagFreq = 0.1
    sortedTags = sorted(tags.items(), key=lambda x: x[1], reverse=True)
    topTags = {}
    for i in range(len(sortedTags)):
        if i < len(sortedTags) * tagFreq:
            topTags[sortedTags[i][0]] = sortedTags[i][1]
    return topTags


# This function alphabetizes a dictionary of tags and their frequencies
def alpha_tags(tags):
    tag_items = sorted(tags.items())

    sortedTags = {}
    for tuple in tag_items:
        sortedTags[tuple[0]] = tuple[1]
    return sortedTags

# This function orders tags by frequency
def order_tags(tags):
    return top_tags(tags, 1)

# This function takes a JSON formatted string and returns a dictionary of the most popular tags
def popular_tags(html, tagFreq):
    parsedJSON = parse_json(html)
    tagList = parse_tags(parsedJSON)
    tagDict = tag_freq(tagList)
    topTags = top_tags(tagDict, tagFreq)
    return topTags

# This function takes a JSON formatted string and returns a dictionary of all tags
def all_tags(html):
    parsedJSON = parse_json(html)
    tagList = parse_tags(parsedJSON)
    tagDict = tag_freq(tagList)
    return tagDict

# This function takes two dictionary of tags and their count and returns a dictionary of the two inputs combined, counts are added together
def combine_tags(tags1, tags2):
    if tags2 == None:
        return tags1
    if tags1 == None:
        return tags2

    ans = {}
    for tag in tags1:
        if tag in ans:
            ans[tag] = ans[tag] + tags1[tag]
        else:
            ans[tag] = tags1[tag]
    for tag in tags2:
        if tag in ans:
            ans[tag] = ans[tag] + tags2[tag]
        else:
            ans[tag] = tags2[tag]
    return ans

# Function that takes a JSON string as input and returns a JSON object
def read_json(json_str):
    json_obj = json.loads(json_str)
    return json_obj


if __name__ == "__main__":
    main()
