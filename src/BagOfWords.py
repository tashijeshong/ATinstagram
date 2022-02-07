# Assign vectors
# Randomly assign clusters
# Find centers
# Reassign clusters to data points closest to centers
# Repeat until little-to-no change

import math
import Utilities as util
import random

SPARSEBAG = ['leave no trace', 'leave no', 'plan', 'visit', 'dispose', 'recycle', "don't take", 'respect', 'minimize', 'wildlife', 'considerate', 'protect', 'leave it better', 'leaveitbetter', 'pick up', 'trash']
BAGOFWORDS = ['leaveitbetter', 'better', 'leavenotrace', 'leav', 'not leav', 'no', 'trace', 'plan', 'dispose', 'damage', 'fire', 'respect', 'conserv', 'wild', 'considerate', 'trail', 'clean', 'up', 'cleanup', 'good', 'bad', 'sad', 'better', 'total', 'recycle', 'trash', 'garbage', 'goal', 'natural', 'mess', 'ethic']
COMMONWORDS = ["the", "and", "for", "are", "of", "an", "to", "a", "in", "is", "it", "you", "that", "with", "as", "was", "he", "be", "on", "at", "by", "this", "have", "from", "or", "but", "his", "not", "they", "which", "one", "had", "word", "what", "all", "were", "we", "when", "your", "can", "said", "there", "use", "each", "", "i", "up", "my", "so", "more", "us", "go", "if", "no", "our", "into", "like", "im", "out", "see", "him", "been", "had", "them", "some", "time", "they", "may", "did", "who", "oil", "now", "get", "come", "just", "know", "take", "people", "into", "year", "your", "good", "some", "could", "them", "then", "only", "those", "very", "she", "well", "were", "need", "any", "these", "also", "over", "think", "also", "back", "after", "use", "two", "how", "way", "our", "work", "first", "well", "well", "these", "went", "made", "were", "well", "being", "through", "where", "much", "before", "want", "because", "those", "those", "while", "those", "again", "where", "how", "well", "being", "through", "where", "much", "before", "want", "because", "those", "those", "while", "those", "again", "where", "how", "well", "being", "through", "where", "much", "before", "want", "because", "those", "those", "while", "those", "again", "where", "how", "well", "being", "through", "where", "much", "before", "want", "because", "those", "those", "while", "those", "again", "where", "how", "well", "being", "through", "where", "much", "before", "want", "because", "those", "those", "while", "those", "again", "where", "how", "well", "being", "through", "where", "much", "before", "want", "because", "those", "those", "while", "those", "again", "where", "how", "well", "being", "through", "where", "much", "before", "want", "because", "those", "those", "while", "those", "again", "where", "how", "well", "being", "through", "where", "much", "about", "before", "again", "has", "around", "many", "com", "it's", "even", "would"]
NUMCLUSTERS = 3

# Return a vector from a caption representing which words from the bagOfWords are present in the caption
def assign_vector(text, bagOfWords=BAGOFWORDS):
    text = clean_caption(text)
    vector = [0] * len(bagOfWords)
    for word in bagOfWords:
        if word in text:
            vector[bagOfWords.index(word)] = 1
    return vector

def find_centers(clusters, bagOfWords=BAGOFWORDS):
    # Find the center of each cluster
    centers = []
    for cluster in clusters:
        center = [0] * len(bagOfWords)
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
    caption = caption.lower().replace("<\\br>", " ").replace("&nbsp;", " ")

    newCaption = "" # Remove punctuation and emojis
    for char in caption:
        if util.is_letter(char) or char == "'":
            newCaption += char
        else:
            newCaption += " "
    return newCaption

def get_unique_words(captions):
    unique_words = {}
    for caption in captions:
        newCaption = clean_caption(caption)
        for word in newCaption.split(" "):
            if word not in unique_words and word not in COMMONWORDS and len(word) >= 3:
                unique_words[word] = 1
            elif word in unique_words and word not in COMMONWORDS and len(word) >= 3:
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
        centers = find_centers(clusters, bagOfWords)
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
