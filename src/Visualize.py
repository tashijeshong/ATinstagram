import os
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt

import networkx as nx
from pyvis.network import Network

from CollectGeoData import DATA_ROOT, GeoPost
import Utilities as util

# Function that builds up a dictionary of tags that occured with other tags per each post
def get_tag_arr(connections=150, sourceTags=[], interestingTags=[]):
    # print(connections, "connections")
    # print(interestingTags)
    allData = DATA_ROOT + "data_thinned.txt"
    # atnoboData = DATA_ROOT + "atnoboXXXX/atnobo2019_1644256478ut_8pages.txt"
    posts = util.read_posts(allData)
    if len(sourceTags) > 0:
        newPosts = []
        for post in posts:
            commonTags = [tag for tag in post.tags if tag in sourceTags]
            if len(commonTags) > 0:
                newPosts.append(post)
        posts = newPosts

    tagDict = {}
    counter = 0
    total = len(posts)
    for post in posts:
        combos = get_tag_combos(post.tags)
        for combo in combos:
            if combo not in tagDict:
                tagDict[combo] = 1
            else:
                tagDict[combo] += 1
        counter += 1
        if counter % (int(total / 1000) + 1) == 0 or counter == total:
            util.printProgressBar(counter, total, prefix = 'Progress:', suffix = 'Complete', length = 50)

    interestingDict = {}
    for key in tagDict.keys():
        if key[0] in interestingTags or key[1] in interestingTags:
            interestingDict[key] = tagDict[key]


    # sort the dictionary by value
    sorted_x = sorted(tagDict.items(), key=lambda kv: kv[1], reverse=True)
    if len(interestingTags) > 0:
        sorted_x = sorted(interestingDict.items(), key=lambda kv: kv[1], reverse=True)
 

    shortSorted = sorted_x[:connections]
    
    formattedArr = []
    for item in shortSorted:
        formattedArr.append([item[0][0], item[0][1], item[1]])
    
    return formattedArr



def get_tag_combos(tagsArr):
    # get a list of tuples for every unique combination of tags for post123
    tagCombos = []
    for tag in tagsArr:
        for tag2 in tagsArr:
            if tag != tag2:
                arr = [tag, tag2]
                arr.sort()
                tup = (arr[0], arr[1])
                if tup not in tagCombos:
                    tagCombos.append(tup)
    # print(tagCombos)
    return tagCombos

# connections specifies how many top tag connections to display
def show_connected_graph(connections=150, sourceTags=[], interestingTags=[]):
    colNames = ["Source", "Target", "weight"]
    net = Network(notebook=True)


    data = get_tag_arr(connections, sourceTags, interestingTags)
    df = pd.DataFrame(data, columns=colNames)
    print(df)

    G = nx.from_pandas_edgelist(df, source='Source', target='Target', edge_attr='weight')

    # nx.draw_networkx(G)
    # plt.show()

    dataTypeLabel = "AllData"
    if len(interestingTags) > 0:
        dataTypeLabel = "TrimmedData"

    net.from_nx(G)
    net.show("../results/" + dataTypeLabel + str(connections) + ".html")

# Function that takes a filename and returns a list of GeoPost objects
def read_geo_posts(filename):
    posts = []
    with open(filename, "r", encoding='utf8') as f:
        for line in f:
            line = line.strip()
            lineSplit = line.split("\t|")
            id = lineSplit[0].split(": ")[1]
            postCode = lineSplit[1].split(": ")[1]
            name = lineSplit[2].split(": ")[1]
            shortname = lineSplit[3].split(": ")[1]
            placeID = lineSplit[4].split(": ")[1]
            address = lineSplit[5].split(": ")[1]
            city = lineSplit[6].split(": ")[1]
            lat = float(lineSplit[7].split(": ")[1])
            lng = float(lineSplit[8].split(": ")[1])

            if name == " ":
                name = "[Null]"
            if shortname == " ":
                shortname = "[Null]"
            if address == " ":
                address = "[Null]"
            if city == " ":
                city = "[Null]"
            

            posts.append(GeoPost(id, postCode, name, shortname, placeID, address, city, lat, lng))
    return posts

# Function that takes list of geoPost objects and returns a list of coordinates (skip post if coordinates are -1, -1)
def get_coordinates(posts):
    coordinates = []
    for post in posts:
        if post.lat != -1 and post.lng != -1:
            coordinates.append((post.lat, post.lng))
    return coordinates

# Function that takes a list of coordinates and displays them on a graph
def plot_coordinates(coordinates):
    x = []
    y = []
    for coordinate in coordinates:
        y.append(coordinate[0])
        x.append(coordinate[1])
    plt.plot(x, y, 'ro')
    plt.show()


def visualize_geo():
    # get a list of every file in the geodata folder
    geoFiles = os.listdir("../geodata")
    # print(geoFiles)
    filenames = []
    for geofile in geoFiles:
        filenames.append("../geodata/" + geofile)
    
    # filenames = ["../geodata/ut_12,072posts_geodata[18,165 total post covered] - 12,072 collected.txt"]
    print(filenames)

    geoPosts = []
    for filename in filenames:
        geoPosts.extend(read_geo_posts(filename))
    
    
    print("Found " + str(len(geoPosts)) + " posts")

    print("Thinning results...")
    thinnedGeoPosts = {}
    for post in geoPosts:
        if post.postCode not in thinnedGeoPosts and int(post.lat) != post.lat and int(post.lng) != post.lng:
            thinnedGeoPosts[post.postCode] = post
    
    print("Found " + str(len(thinnedGeoPosts)) + " unique/viable posts")

    # print("Coalescing results...")
    cleanGeoPosts = []
    for post in thinnedGeoPosts.values():
        cleanGeoPosts.append(post)
    
    # print("Using " + str(len(cleanGeoPosts)) + " posts")

    print("Getting coordinates...")
    coords = get_coordinates(cleanGeoPosts)

    # geoPosts = read_geo_posts("../geodata/ut_12,072posts_geodata[18,165 total post covered] - 12,072 collected.txt")
    # coords = get_coordinates(geoPosts)
    # # plot_coordinates(coords)



    print("Plotting results")

    df = pd.DataFrame(coords)

    ### https://stackoverflow.com/questions/53233228/plot-latitude-longitude-from-csv-in-python-3-6#fromHistory
    fig = px.scatter_geo(df,lat=0,lon=1)
    fig.update_layout(title = 'World map', title_x=0.5)
    fig.show()
    ### https://stackoverflow.com/questions/53233228/plot-latitude-longitude-from-csv-in-python-3-6#fromHistory

def main():
    interestingTags = []
    sourceTags = []

    # UNCOMMENT THIS TO LIMIT RESULTS TO ONLY INCLUDE THESE TAGS
    # interestingTags = ["#appalachiantrail", "#leavenothingbutfootprints", "#leavenotrace", "#lnt"]
    # for year in range(2018, 2022):
    #     interestingTags.append("#atnobo" + str(year))
    #     interestingTags.append("#atnobo" + str(year))
    #     interestingTags.append("#atclassof" + str(year))
    
    interestingTags = ["#atnobo2018"]

    # CHANGE THIS TO ONLY COLLECT DATA FROM POSTS WITH THESE TAG(S)
    sourceTags = ["#appalachiantrail", "#leavenothingbutfootprints", "#leavenotrace", "#lnt"]
    for year in range(2018, 2022):
        sourceTags.append("#atnobo" + str(year))
        sourceTags.append("#atnobo" + str(year))
        sourceTags.append("#atclassof" + str(year))
    
    sourceTags = ["#atnobo2018"]

    choices = """[1]Show connected graph
[2]Visualize geo data
[Q]uit
User Input: """
    choice = input(choices)
    if choice == "1":
        connections = int(input("How many connections to show? "))
        show_connected_graph(connections, sourceTags, interestingTags)
    elif choice == "2":
        visualize_geo()
    elif choice == "Q" or choice == "q":
        print("Exiting...")
        exit()


if __name__ == "__main__":
    main()

