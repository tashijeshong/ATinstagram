import json

BASE = "../data/" ###CHANGE THIS DEPENDING ON WHERE YOU'RE RUNNING THE PROJECT

# This is the main function that runs the program
def main():
    file1 = BASE + "res1.txt"
    file2 = BASE + "res2.txt"
    file3 = BASE + "res3.txt"
    html1 = open(file1, 'r', encoding="utf8").read()
    html2 = open(file2, 'r', encoding="utf8").read()
    html3 = open(file3, 'r', encoding="utf8").read()

    tag1 = all_tags(html1) #extracts all tags from a file
    tag2 = all_tags(html2)
    tag3 = all_tags(html3)

    allTags = combine_tags(tag1, tag2) #combines two results into one (assumes that their contents are mutually exclusive, will program a check in later)
    allTags = combine_tags(allTags, tag3)
    print(top_tags(allTags, 0.25)) #prints the top tags of combined results (top 25%)





# This function parses JSON-like strings to report all values associated with "text" keys
# The format of the desired output is as follows: ..."text":"<VALUE>"...
def parse_json(html):
    ans = []
    json = read_json(html)
    for i in range(len(json['data']['hashtag']['edge_hashtag_to_media']['edges'])):
        edge = json['data']['hashtag']['edge_hashtag_to_media']['edges'][i]['node']['edge_media_to_caption']['edges']
        if len(edge) > 0:
            ans.append(edge[0]['node']['text'])
        else:
            ans.append("")

    return ans


# This function parses text for tags, specifically for "#<TAG>"
def parse_tags(descriptions):
    cleanTags = []
    for desc in descriptions:
        tmpTag = ""
        # add every tag to tmpTag
        for i in range(len(desc)):
            if desc[i] == '#':
                tmpTag += '#'
                i = i + 1
                if i >= len(desc):
                    break
                while(desc[i] != ' ' and desc[i] != '#' and desc[i] != '\n' and desc[i] != '\r'):
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


# This function takes an array of cleaned tags and returns dictionary of each tag and its frequency
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
