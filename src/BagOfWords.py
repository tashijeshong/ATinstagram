# Assign vectors
# Randomly assign clusters
# Find centers
# Reassign clusters to data points closest to centers
# Repeat until little-to-no change

import math
import Utilities as util
import random

BAGOFWORDS = ['leaveitbetter', 'better', 'leavenotrace', 'leav', 'not leav', 'no', 'trace', 'plan', 'dispose', 'damage', 'fire', 'respect', 'conserv', 'wild', 'considerate', 'trail', 'clean', 'up', 'cleanup', 'good', 'bad', 'sad', 'better', 'total', 'recycle', 'trash', 'garbage', 'goal', 'natural', 'mess', 'ethic']
COMMONWORDS = ["the", "and", "for", "are", "of", "an", "to", "a", "in", "is", "it", "you", "that", "with", "as", "was", "he", "be", "on", "at", "by", "this", "have", "from", "or", "but", "his", "not", "they", "which", "one", "had", "word", "what", "all", "were", "we", "when", "your", "can", "said", "there", "use", "each", "", "i", "up", "my", "so", "more", "us", "go", "if", "no", "our", "into", "like", "im", "out", "see", "him", "been", "had", "them", "some", "time", "they", "may", "did", "who", "oil", "now", "get", "come", "just", "know", "take", "people", "into", "year", "your", "good", "some", "could", "them", "then", "only", "those", "very", "she", "well", "were", "need", "any", "these", "also", "over", "think", "also", "back", "after", "use", "two", "how", "way", "our", "work", "first", "well", "well", "these", "went", "made", "were", "well", "being", "through", "where", "much", "before", "want", "because", "those", "those", "while", "those", "again", "where", "how", "well", "being", "through", "where", "much", "before", "want", "because", "those", "those", "while", "those", "again", "where", "how", "well", "being", "through", "where", "much", "before", "want", "because", "those", "those", "while", "those", "again", "where", "how", "well", "being", "through", "where", "much", "before", "want", "because", "those", "those", "while", "those", "again", "where", "how", "well", "being", "through", "where", "much", "before", "want", "because", "those", "those", "while", "those", "again", "where", "how", "well", "being", "through", "where", "much", "before", "want", "because", "those", "those", "while", "those", "again", "where", "how", "well", "being", "through", "where", "much", "before", "want", "because", "those", "those", "while", "those", "again", "where", "how", "well", "being", "through", "where", "much"]
NUMCLUSTERS = 3

# Return a vector from a caption representing which words from the bagOfWords are present in the caption
def assign_vector(text, bagOfWords=BAGOFWORDS):
    text = clean_caption(text)
    vector = [0] * len(bagOfWords)
    for word in bagOfWords:
        if word in text:
            vector[bagOfWords.index(word)] = 1
    return vector

def find_centers(clusters):
    # Find the center of each cluster
    centers = []
    for cluster in clusters:
        center = [0] * len(BAGOFWORDS)
        for vector in cluster:
            for i in range(len(vector[1])):
                center[i] += vector[1][i]
        for i in range(len(center)):
            if len(cluster) == 0:
                continue
            center[i] /= len(cluster)
        centers.append(center)
    return centers

# Assigns each vector to a cluster based on the centroids (centers)
# Returns 1. the clusters (containing the assigned vectors)
#         2. the average distance each vector is from its cluster's center
def assign_clusters(vectors, centers):
    # Cycle through each vector and assign it to the cluster with the closest center
    clusters = [[] for i in range(len(centers))]
    avgDist = 0
    for vector in vectors:
        closest_center = 0
        closest_distance = calc_dist(vector[1], centers[0])
        for i in range(1, len(centers)):
            distance = calc_dist(vector[1], centers[i])
            if distance < closest_distance:
                closest_distance = distance
                closest_center = i
        clusters[closest_center].append(vector)
        avgDist += closest_distance

    avgDist /= len(vectors)
    return clusters, avgDist

# Calculates the Euclidean distance between two vectors
def calc_dist(vector1, vector2):
    distance = 0
    for i in range(len(vector1)):
        distance += (vector1[i] - vector2[i]) ** 2
    return math.sqrt(distance)

# Cleans a caption to remove punctuation and emojis
def clean_caption(caption):
    caption = caption.lower().replace("<\\br>", " ")

    newCaption = "" # Remove punctuation and emojis
    for char in caption:
        if util.is_letter(char):
            newCaption += char
        else:
            newCaption += " "
    return newCaption

def get_unique_words(captions):
    unique_words = {}
    for caption in captions:
        newCaption = clean_caption(caption)
        for word in newCaption.split(" "):
            if word not in unique_words and word not in COMMONWORDS:#len(word) >= 3:
                unique_words[word] = 1
            elif word in unique_words and word not in COMMONWORDS:#len(word) >= 3:
                unique_words[word] += 1
    return unique_words


# Create the vectors for each caption
# Vector in the form of (id, bag-of-words-array)
def make_vectors(examples, bagOfWords=BAGOFWORDS):
    vectors = []
    for ex in examples:
        vector = assign_vector(ex[1].lower(), bagOfWords)
        vectors.append((ex[0], vector))
    return vectors

# Assign vectors to a cluster sequentially
def setup_clusters(vectors, numClusters):
    clusters = []
    for i in range(numClusters):
        clusters.append([])
    # Generate a random number between [0, len(numClusters) - 1]
    for i in range(len(vectors)):
        randIdx = random.randint(0, numClusters - 1)
        clusters[randIdx].append(vectors[i]) #clusters[i % numClusters].append(vectors[i])
    return clusters

# Returns a list of clusters, each cluster being a list of size numVectors containing the ids of the vectors closest to the center
def thin_clusters(clusters, centers, numVectors):
    thinnedClusters = []
    for i in range(len(clusters)): # For each cluster
        thinnedCluser = []
        minDist = 0
        for n in range(numVectors): # Get numVectors vectors closest to the center
            if n > len(clusters[i]): # Break if we've gone through all the vectors in the cluster
                break
            closestDist = float("inf")
            closestVector = None
            for vector in clusters[i]: # Find the closest vector not already in list
                distance = calc_dist(vector[1], centers[i])
                if distance < closestDist and distance > minDist:
                    closestDist = distance
                    closestVector = vector
            thinnedCluser.append(closestVector[0])
            minDist = closestDist
        thinnedClusters.append(thinnedCluser)

    return thinnedClusters        

# dataset: list of tuples (id, string of words)
# numClusters: number of clusters to create
# bagOfWords: list of words to use as features
def train(dataset, numClusters=NUMCLUSTERS, bagOfWords=BAGOFWORDS):
    vectors = make_vectors(dataset, bagOfWords)
    clusters = setup_clusters(vectors, numClusters)
    
    # Train the clusters until convergence
    lastClusters = None

    iter = 0
    while True:
        centers = find_centers(clusters)
        clusters, lastAvgDist = assign_clusters(vectors, centers)
        if clusters == lastClusters:
            break
        lastClusters = clusters
        iter += 1
    
    print("Training took " + str(iter) + " iterations")
    print("Average distance: " + str(lastAvgDist))
    return clusters, centers

def print_clusters(clusters):
    for i in range(len(clusters)):
        print("Cluster " + str(i+1) + ":")
        for ex in clusters[i]:
            print(ex[0])
        print("")


# ex1 = "Today is a good day to clean up garbage and leave no trace #leavenotrace"
# ex2 = "This trail was covered in trash when I found it, but I'm going to leave it better! #leaveitbetter"
# ex3 = "I'm leaving my house today. #leave"
# ex4 = "I'm going to leave trash here, but I feel kind of bad about it"
# ex5 = "Leave nature in its natural state!"
# ex6 = "The state I found the national park in was just sad"

# cap0 = ("Caption 0", "I'm going to leave trash here, but I feel kind of bad about it.")
# cap1 = ("Caption 1", "Staying in! Here's Huey keepin it cozy!<\\br>.<\\br>Are you staying in today?! Let us know below!<\\br>.<\\br>Tag or DM us for a chance to be featured<\\br>.<\\br>#dogsofthecatskills #dogsofthecats #catskilldog #catskilllife #catskillpark #catskillmountains #ilovethecatskills #catskillny #catskills #visitcatskills #visitny #ilovenewyork #iloveny #nysparks #hiking #dog #hikingdog #dogsofinstagram #dogsofinsta #hikingwithdogs #exploringwithdogs #upstateny #pupstate #dogsonadventure #getoutside #optoutside #leavenotrace #catskill3500 #Catskill3500club #livelifeoffleash")
# cap2 = ("Caption 2", "Happy Impact Day! It was a beautiful afternoon last week to go out and do some good on one of the local trails. Always remember to leave no trace. Keep our trails beautiful. #wildkeeper #keepnaturewild #impactday #leavenotrace #dontbetrashy")
# cap3 = ("Caption 3", "New Year, new goals, more cleaning up our earth! 🌎 <\\br><\\br>Sharing my 3 goals for 2022 ✨<\\br><\\br>♻ Pick up 100 lbs (or more) of trash!<\\br><\\br>🥾 Explore as much of the northeast as possible once I move to NH!<\\br><\\br>🎒Try at least 2 new activities (backpacking being #1)<\\br><\\br>#keepnaturewild #wildkeepers #impactday #dontbetrashy #nurtureournature #dontlitter #packitinpackitout #keepitclean #beachcleanup #coastalcleanup #beachtrash #leaveitbetter  #littercleanup #leavenotrace #newyeargoals")
# cap4 = ("Caption 4", "Not gonna lie……the colors of this water make it VERY enticing to jump in 🤔<\\br><\\br>Here's your kind of fun but also sad fact of the day - this hot spring is called the “Morning Glory Pool” and the vibrant color comes from bacteria that thrives in the incredibly hot water. <\\br><\\br>Unfortunately, people throw shit down into the pool which clogs it up and makes it very difficult for the natural hot water to come up. This lowers the surface temperature of the water and kills the bacteria, thus reducing the vibrant colors that are shown off. <\\br><\\br>Because of this, it is drained and cleaned from time to time in order to restore its natural state.<\\br><\\br>So if you're in Yellowstone - DON'T THROW ANYTHING INTO THE POOLS! NOT EVEN NATURAL THINGS LIKE ROCKS!<\\br><\\br>#shotoniphone #cdt2021 #wyoming #yellowstonenationalpark #goingfarout #embracethebrutality #bravethecdt #LeaveNoTrace #optoutside")
# cap5 = ("Caption 5", "hanging out above the clouds <\\br>☁️🏔❄️ <\\br>To be completely honest, I have no idea how I captured this moment so perfectly. At this point I’m about 5 miles up and on the last mile of the hike. My legs are shaking, I can't stop for more than a couple min at a time because of the cold layer of sweat I'm carrying with me. I see the moment, grab my phone with my chunky, gloved hand, then point and shoot shakily! And this is the photo I ended up with! 🤯 <\\br>Moments like these can go by so quickly, live every moment of life with intention. And have fun! <\\br><\\br>#thegreatoutdoors #pnwonderland #views #summit #pnw #pnwlife #hiking #hikingadventures #mountains #washington #seattle #getoutside #leavenotrace #abovetheclouds #bluebird #earth #paradise #paradiseisnttropical")
# cap6 = ("Caption 6", "The longest January ever is finally over!! Here's to exciting times ahead!🥳🙏 @dylan.roberts.adventures #mountainmonday #newbeginnings #positivity #vanlife #vanlifeuk #homeonwheels #homeiswhereyouparkit #vanliving #projectvanlife #offgridliving #vanlifecommunity #vanlifeexplorers #vanlifers #leavenotrace #adventure #exploremore #travelcouple #adventurecouple #coupleswhotravel #hikemoreworryless #madetoroam #ontheroad #neverstopexploring #vanlifecouple #vanlifeculture #glencoe #scotland #scottishhighlands #visitscotland #mountaintherapy")
# cap7 = ("Caption 7", "Watching night turn to an amazing, beautiful day. And to think this happens Every. Single. Day.<\br>#hiking #dayhikes #adventure #optoutside #leavenotrace #saunter")

# # examples = [ex1, ex2, ex3, ex4, ex5, ex6]
# examples = [cap0, cap1, cap2, cap3, cap4, cap5, cap6, cap7]
# allWords = get_unique_words([x[1] for x in examples])
# # print(allWords)
# print(str(len(allWords.keys())) + " unique words")
# # print top 10 most frequent words
# # sortedWords = sorted(allWords.items(), key=lambda x: x[1], reverse=True)
# # print(sortedWords[:25])

# # exit()

# myClusters, _ = train(examples)
# print_clusters(myClusters)
