import networkx
from operator import itemgetter
import matplotlib.pyplot
import pandas as pd
from difflib import SequenceMatcher
import pandas as pd
import numpy as np
# Read the data from the amazon-books.txt;
# populate amazonProducts nested dicitonary;
# key = ASIN; value = MetaData associated with ASIN
fhr = open('./amazon-books.txt', 'r', encoding='utf-8', errors='ignore')
amazonBooks = {}
fhr.readline()
for line in fhr:
    cell = line.split('\t')
    MetaData = {}
    MetaData['Id'] = cell[0].strip() 
    ASIN = cell[1].strip()
    MetaData['Title'] = cell[2].strip()
    MetaData['Categories'] = cell[3].strip()
    MetaData['Group'] = cell[4].strip()
    MetaData['SalesRank'] = int(cell[5].strip())
    MetaData['TotalReviews'] = int(cell[6].strip())
    MetaData['AvgRating'] = float(cell[7].strip())
    MetaData['DegreeCentrality'] = int(cell[8].strip())
    MetaData['ClusteringCoeff'] = float(cell[9].strip())
    amazonBooks[ASIN] = MetaData
fhr.close()

# Read the data from amazon-books-copurchase.adjlist;
# assign it to copurchaseGraph weighted Graph;
# node = ASIN, edge= copurchase, edge weight = category similarity
fhr=open("amazon-books-copurchase.edgelist", 'rb')
copurchaseGraph=networkx.read_weighted_edgelist(fhr)
fhr.close()

# Now let's assume a person is considering buying the following book;
# what else can we recommend to them based on copurchase behavior 
# we've seen from other users?
print ("Looking for Recommendations for Customer Purchasing this Book:")
print ("--------------------------------------------------------------")
purchasedAsin = '0805047905'

# Let's first get some metadata associated with this book
print ("ASIN = ", purchasedAsin) 
print ("Title = ", amazonBooks[purchasedAsin]['Title'])
print ("SalesRank = ", amazonBooks[purchasedAsin]['SalesRank'])
print ("TotalReviews = ", amazonBooks[purchasedAsin]['TotalReviews'])
print ("AvgRating = ", amazonBooks[purchasedAsin]['AvgRating'])
print ("DegreeCentrality = ", amazonBooks[purchasedAsin]['DegreeCentrality'])
print ("ClusteringCoeff = ", amazonBooks[purchasedAsin]['ClusteringCoeff'])


# Now let's look at the ego network associated with purchasedAsin in the
# copurchaseGraph - which is esentially comprised of all the books 
# that have been copurchased with this book in the past
# (1) YOUR CODE HERE: 
#     Get the depth-1 ego network of purchasedAsin from copurchaseGraph,
#     and assign the resulting graph to purchasedAsinEgoGraph.
purchasedAsinEgoGraph = networkx.Graph()
purchasedAsinEgoGraph = networkx.ego_graph(copurchaseGraph,purchasedAsin,radius = 1)

# Next, recall that the edge weights in the copurchaseGraph is a measure of
# the similarity between the books connected by the edge. So we can use the 
# island method to only retain those books that are highly simialr to the 
# purchasedAsin
# (2) YOUR CODE HERE: 
#     Use the island method on purchasedAsinEgoGraph to only retain edges with 
#     threshold >= 0.5, and assign resulting graph to purchasedAsinEgoTrimGraph
threshold = 0.5
purchasedAsinEgoTrimGraph = networkx.Graph()
weightStore = []
for f, t, e in purchasedAsinEgoGraph.edges(data=True):
    if e['weight'] >= threshold:
        purchasedAsinEgoTrimGraph.add_edge(f,t,weight=e['weight'])   
        if f == purchasedAsin or t == purchasedAsin:
            weightStore.append((f,t,e['weight']))
            
# the purchasedAsinEgoTrimGraph you constructed above,we can get at the list of nodes connected to the purchasedAsin by a single 
# hop (called the neighbors of the purchasedAsin) 

#     Now let's find the list of neighbors of the purchasedAsin in the 
#     purchasedAsinEgoTrimGraph, and assign it to purchasedAsinNeighbors
purchasedAsinNeighbors = [i for i in purchasedAsinEgoTrimGraph.neighbors(purchasedAsin)]
print("step 3 -----------------------",purchasedAsinNeighbors)

# Next, let's pick the Top Five book recommendations from among the 
# purchasedAsinNeighbors based on one or more of the following data of the 
# neighboring nodes: SalesRank, AvgRating, TotalReviews, DegreeCentrality, 
# and ClusteringCoeff

# I'm  adding the weight column for each of the asin received after step 3
lst = []
for i in range(len(purchasedAsinNeighbors)):
    if weightStore[i][0] == purchasedAsin:
        lst.append([weightStore[i][1],weightStore[i][2]])
    else:
        lst.append([weightStore[i][0],weightStore[i][2]])


df = pd.DataFrame(data = lst) 
df.rename(columns={0:"Asin",1:"Weight"},inplace=True)
df.set_index('Asin',inplace=True)

a = {}
for i in purchasedAsinNeighbors:
    a[i] = [i , amazonBooks[i]['Title'], amazonBooks[i]['SalesRank'],amazonBooks[i]['TotalReviews'], amazonBooks[i]['AvgRating']]

df1 = pd.DataFrame(data = a)
df1 = df1.transpose()
df1.reset_index(inplace = True, drop = True)
df1.rename(columns={0:"Asin",1:"Title",2:"SalesRank",3:"TotalReviews",4:"AvgRatings"},inplace=True)
df1.set_index('Asin',inplace=True)

#I've dropped the books with the similarity greater than 80% in their titles among all neighbors as all the other parameters are same apart from the sales rank 
 
lst=[]
for idx,i in df1['Title'].iteritems():
    for jdx,j in df1['Title'].iteritems():
        if(idx != jdx):
            m=0
            m=SequenceMatcher(None,i,j)
            if (m.ratio() >= .80) & (m.ratio()< 1):
                if df1['SalesRank'][jdx] > df1['SalesRank'][idx]:
                    lst.append(jdx)
            elif m.ratio()==1:
                if df1['SalesRank'][jdx] > df1['SalesRank'][idx]:
                    lst.append(jdx)
x_1 = set(lst)
y_1 = list(x_1)
                    
for i in range(len(y_1)):
    df1.drop(index = (y_1[i]),inplace=True)

#Merging the weight column with the dataframe having all the other parameters 
fullForm = pd.merge(df, df1, how ='inner', on = 'Asin')

#sorting on the basis of weight
fullForm = fullForm.sort_values(['Weight'], axis = 0, ascending = False)

#after sorting on the basis of weight, considering only top 15 books
top_15 = fullForm.iloc[:15,:]

#taking a product of Total Reviews and Average Ratings and then sorting it based on this new column
top_15['rate_review'] = top_15['TotalReviews'] * top_15['AvgRatings']

top_15 = top_15.sort_values(['rate_review'], axis = 0, ascending = False)

#taking top 10 books from above result
top_10 = top_15.iloc[:10,:]

#Now sorting the remaining books based on SalesRank and considering the top 10 books
top_10 = top_10.sort_values(['SalesRank'], axis = 0, ascending = True)

# Print Top 5 recommendations (ASIN, and associated Title, Sales Rank, 
# TotalReviews, AvgRating, DegreeCentrality, ClusteringCoeff) 
print ("Top 5 recommendations")
print ("--------------------------------------------------------------")

top_5 = top_10.iloc[:5,:]       #printing the top 5 books from the list obtained in the previous step

x = []
y = []
for i in top_5.index:
    
    x.append((amazonBooks[i]['ClusteringCoeff']))
    y.append((amazonBooks[i]['DegreeCentrality']))
top_5['Clustering_Coeff'] = x
top_5['Degree_Centrality'] = y

top_5.drop('Weight', axis = 1, inplace = True)

print(top_5)