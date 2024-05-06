import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import load_npz
from scipy.sparse import csr_matrix

path = "data\keywords.csv"
def read_data(path):
    data = pd.read_csv(path)
    return data

def vectorize(data):
    tfidf = TfidfVectorizer(analyzer = 'word',
                            min_df=3,
                            max_df = 0.6,
                            stop_words="english",
                            encoding = 'utf-8')
    tfidf_encoding = tfidf.fit_transform(data["keywords"])
    return tfidf_encoding

def return_similarity(tfidf_matrix):
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    return cosine_sim

data = read_data(path)
tfidf_encoding = vectorize(data)
#cosine_sim = return_similarity(tfidf_encoding)

indices = pd.Series(data['Name'])

# Load the sparse matrix
cosine_sim_file="cosine_sim_sparse2.npz"
cosine_sim_sparse = load_npz(cosine_sim_file)

def myrecommend(title, n = 5, cosine_sim_sparse = cosine_sim_sparse):
    cosine_sim_sparse = load_npz(cosine_sim_file)
    #if given a title not in database
    if title not in indices.values:
        #split the given title and search with pieces in db until you find a match
        ls = title.split(' ')
        m = len(ls)
        search = [' '.join(ls[:i]) for i in range(m, 0, -1)] 
        for s in search:
            newtitle = data.loc[data['Name'].str.lower().str.contains(s)][0:1]['Name']
            if len(newtitle) != 0:
                break
        else:
            return "Book not found"
        title = newtitle.values[0]
        
    recommended_books = []
    idx = indices[indices == title].index[0] # to get the index of book name matching the input book_name
    # Use sparse matrix multiplication to compute cosine similarities efficiently
    sim_scores = cosine_sim_sparse[idx].toarray().flatten()

    # Get indices of top similar books
    top_indices = sim_scores.argsort()[::-1][1:n+1]
    # [1:n+1] to exclude 0 (index 0 is the input book itself)

    for i in top_indices: # to append the titles of top 10 similar booksto the recommended_books list
        recommended_books.append(list(data['Name'])[i])

    return recommended_books

if __name__ == '__main__':
    book_name = 'harry potter'
    print(myrecommend(book_name))
