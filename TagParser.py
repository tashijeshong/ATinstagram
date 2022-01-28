TAGTERMINATORS = [' ', '#', '\n', '\r', '\t', ',', '.', '&', '\'', '\"', ':', ';', '!', '?', '-', '_', '+', '=', '*', '%', '$', '@', '^', '&', '|', '~', '`', '(', ')', '{', '}', '[', ']', '<', '>', '/', '\\', '\u3000']


# This function parses an array of descriptions and outputs an array of tags
# It also removes all punctuation and whitespace from tags
def parse_descs(descriptions):
    cleanTags = []
    for desc in descriptions:
        desc_tags = parse_desc(desc)
        cleanTags.extend(desc_tags)

    return cleanTags

# This function takes a description and returns an array of cleaned tags
def parse_desc(desc):
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