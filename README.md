# Recommender-System
Amazon Book Recommender System

#Problem Definition
In this Assignment, I'm going to use Amazon Product Co-purchase data to make Book Recommendations using Network Analysis. This project has three objectives:
•	Apply Python concepts to read and manipulate data and get it ready for analysis
•	Apply Network Analysis concepts to Build and Analyze Graphs
•	Apply concepts in Text Processing, Network Analysis and Recommendation Systems to make a product recommendation
-----------------------------
Details about Dataset -

This data set is comprised of product and review metdata on 548,552 different products. The data was collected in 2006 by crawling the Amazon website. You can view the data by double-clicking on the file amazon-meta.txt that’s been included in NetworkAnalysis.zip. The following information is available for each product in this dataset:
•	Id: Product id (number 0, ..., 548551)
•	ASIN: Amazon Standard Identification Number. 
The Amazon Standard Identification Number (ASIN) is a 10-character alphanumeric unique identifier assigned by Amazon.com for product identification. You can lookup products by ASIN using following link: https://www.amazon.com/product-reviews/<ASIN> 
•	title: Name/title of the product
•	group: Product group. The product group can be Book, DVD, Video or Music.
•	salesrank: Amazon Salesrank
The Amazon sales rank represents how a product is selling in comparison to other products in its primary category. The lower the rank, the better a product is selling. 
•	similar: ASINs of co-purchased products (people who buy X also buy Y)
•	categories: Location in product category hierarchy to which the product belongs (separated by |, category id in [])
•	reviews: Product review information: total number of reviews, average rating, as well as individual customer review information including time, user id, rating, total number of votes on the review, total number of helpfulness votes (how many people found the review to be helpful)

 Steps performed -->
The first step we have to perform is read, preprocess, and format this data for further analysis.  PreprocessAmazonBooks.py script takes the “amazon-meta.txt” file as input, and performs the following steps:

•	Parses the amazon-meta.txt file
•	Preprocesses the metadata for all ASINs, and writes out the following fields into the amazonProducts Nested Dictionary (key = ASIN and value = MetaData Dictionary associated with ASIN):
    o	Id: same as “Id” in amazon-meta.txt
    o	ASIN: same as “ASIN” in amazon -meta.txt
    o	Title: same as “title” in amazon-meta.txt
    o	Categories: a transformed version of “categories” in amazon-meta.txt. Essentially, all categories associated with the ASIN are     concatenated, and are then subject to the following Text Preprocessing steps: lowercase, stemming, remove digit/punctuation, remove stop words, retain only unique words. The resulting list of words is then placed into “Categories”.
    o	Copurchased: a transformed version of “similar” in amazon-meta.txt. Essentially, the copurchased ASINs in the “similar” field are filtered down to only those ASINs that have metadata associated with it. The resulting list of ASINs is then placed into “Copurchased”.
    o	SalesRank: same as “salesrank” in amazon-meta.txt
    o	TotalReviews: same as total number of reviews under “reviews” in amazon-meta.txt
    o	AvgRating: same as average rating under “reviews” in amazon-meta.txt
•	Filters amazonProducts Dictionary down to only Group=Book, and write filtered data to amazonBooks Dictionary
•	Uses the co-purchase data in amazonBooks Dictionary to create the copurchaseGraph Structure as follows:
    o	Nodes: the ASINs are Nodes in the Graph
    o	Edges: an Edge exists between two Nodes (ASINs) if the two ASINs were co-purchased
    o	Edge Weight (based on Category Similarity): since we are attempting to make book recommendations based on co-purchase information, it would be nice to have some measure of Similarity for each ASIN (Node) pair that was co-purchased (existence of Edge between the Nodes). We can then use the Similarity measure as the Edge Weight between the Node pair that was co-purchased. We can potentially create such a Similarity measure by using the “Categories” data, where the Similarity measure between any two ASINs that were co-purchased is calculated as follows:
    Similarity = (Number of words that are common between Categories of connected Nodes)/
        (Total Number of words in both Categories of connected Nodes)
    The Similarity ranges from 0 (most dissimilar) to 1 (most similar).
•	Adds the following graph-related measures for each ASIN to the amazonBooks Dictionary:
    o	DegreeCentrality: associated with each Node (ASIN)
    o	ClusteringCoeff: associated with each Node (ASIN)
•	Writes out the amazonBooks data to the amazon-books.txt file (all except copurchase data – because that data is now in the copurchase graph)
•	Writes out the copurchaseGraph data to the amazon-books-copurchase.edgelist file

The next step is to use this transformed data to make Book Recommendations. “Amazon_recommender_System.py” takes the “amazon-books.txt” and “amazon-books-copurchase.adjlist” files as input, and performs the following steps -

•	Read amazon-books.txt data into the amazonBooks Dictionary
•	Read amazon-books-copurchase.edgelist into the copurchaseGraph Structure
•	We then assume a User has purchased a Book with ASIN=0805047905. The question then is, how do we make other Book Recommendations to this User, based on the Book copurchase data that we have? 
I took the below steps to make the recommendation for the book and considered all the paramteres - 
Step 1: Drop duplicates
In order to tackle duplicates, we used SequenceMatcher to identify the percentage of match in given two strings. For AsinID = ‘0805047905’, out of the 31 rows of data, 3 titles have 100% match in their data which indicates as duplicates and 2 of them have 80% match due to the difference of spaces. Therefore, in order to avoid recommending same books to the user, we dropped the books with the similarity greater than 80% in their titles among all neighbors.

Step 2: Filter by weights
The idea behind filter by weights is to identify the closest ties to the user’s book to bring in similarity and relevance in picture. Out of the 31 ties, top 15 with the strongest ties are picked in this step.  
To bring weights into consideration before “total reviews” or “sales ranking” is because a book can be ranked as 1 but the relevance to the user’s book may not be there. In order to avoid a completely random recommendation we are sorting based on weights to consider the most similar books for recommendation.

Step 3: Sort by production of average rating and total reviews 
Consider the situation where book “A” has a rating of 5 and total number of people who gave reviews are 1 and book “B” has a rating of 4.7 and total reviews are 50. In this case “B” should be preferred over “A” even though “A” has a higher rating because the number of people who reviewed are more. In order to bring this into the picture we multiplied column (TotalReviews) with column(AvgRating) and displayed it as rate_review.
Out of the top15 from step2, we are picking the top10 in this step.

Step 4: based on Rank filter top 5
The final step is to recommend the best ranked books to the user. Among the top 10 books from step 3, we sorted the books by their sales ranking and picked the top 5 books as recommendation. Since the lowest value of ranking represents a higher position in the chart, the top 5 recommendations would hold the smallest number of rankings.
