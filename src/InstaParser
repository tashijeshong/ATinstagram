import json

BASE = "../data/"

# This is the main function that runs the program
def main():
    tag1 = all_tags(BASE + "res1.txt", 0.1) #extracts all tags from a file
    # print(tag1)
    tag2 = all_tags(BASE + "res2.txt", 0.1)
    # print(tag2)
    tag3 = all_tags(BASE + "res3.txt", 0.1)
    # print(tag3)

    allTags = combine_tags(tag1, tag2) #combines two results into one (assumes that their contents are mutually exclusive, will program a check in later)
    allTags = combine_tags(allTags, tag3)
    print(top_tags(allTags, 0.25)) #prints the top tags of combined results (top 25%)


    # file1 = BASE + "res1.txt"
    # html_doc1 = open(file1, 'r', encoding="utf8").read()
    # json1 = read_json(html_doc1)
    # print("Number of entries: ", len(json1['data']['hashtag']['edge_hashtag_to_media']['edges']))
    # print("Has next page: ", json1['data']['hashtag']['edge_hashtag_to_media']['page_info']['has_next_page'])
    # print("End cursor: ", json1['data']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor'])






# This function parses JSON-like strings to report all values associated with "text" keys
# The format of the desired output is as follows: ..."text":"<VALUE>"...
def parse_json(html):
    ans = []
    for i in range(len(html)):
        if(html[i] == '"'):
            if(html[i+1] == 't' and html[i+2] == 'e' and html[i+3] == 'x' and html[i+4] == 't' and html[i+5] == '"'):
                i = i + 8
                while(html[i] != '"'):
                    ans.append(html[i])
                    i = i + 1
    string = ""
    for a in ans:
        string += a
    return string

# This function parses text for tags, specifically for "#<TAG>"
def parse_tags(text):
    ans = []
    for i in range(len(text)):
        if(text[i] == '#'):
            ans.append('#')
            i = i + 1
            if i >= len(text):
                print("break")
                break
            while(text[i] != ' ' and text[i] != '\\'):
                ans.append(text[i])
                i = i + 1
                if i >= len(text):
                    print("break")
                    ans.append(' ')
                    break
            ans.append(' ')
    string = ""
    for a in ans:
        string += a
    return string

# This function cleans up empty tags from a list of tags
# Removes any tag that has a space right after it
def clean_tags(tags):
    ans = tags.split('#')
    cleanTags = []
    for i in range(len(ans)):
        if len(ans[i]) > 1:
            cleanTags.append(ans[i])
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


# This function takes a file and returns a dictionary of the most popular tags in the file
def popular_tags(file, tagFreq):
    print("Starting...")
    #set html_doc to the contents of the entire file
    html_doc = open(file, 'r', encoding="utf8").read()
    print("Parsing...")
    parsedJSON = parse_json(html_doc)
    parsedTags = parse_tags(parsedJSON)
    cleanTags = clean_tags(parsedTags)
    cleanTags.sort()
    freqTags = tag_freq(cleanTags)
    print("Done!")
    return top_tags(freqTags, tagFreq)

# This function takes a file and returns a dictionary of all tags in the file
def all_tags(file, tagFreq):
    print("Starting...")
    #set html_doc to the contents of the entire file
    html_doc = open(file, 'r', encoding="utf8").read()
    print("Parsing...")
    parsedJSON = parse_json(html_doc)
    parsedTags = parse_tags(parsedJSON)
    cleanTags = clean_tags(parsedTags)
    cleanTags.sort()
    freqTags = tag_freq(cleanTags)
    print("Done!")
    return freqTags

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
