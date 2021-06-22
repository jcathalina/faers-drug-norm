import pandas as pd
import numpy as np
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import csr_matrix
from scipy.sparse import rand
from sparse_dot_topn import awesome_cossim_topn

data = pd.read_csv("../data/FAERS_DEV_SET.csv", low_memory=False)
df = data["drugname"]


def ngrams(string, n=3):
    string = re.sub(r'[,-./]|\sBD', r'', string)
    ngrams = zip(*[string[i:] for i in range(n)])
    return [''.join(ngram) for ngram in ngrams]


def get_matches_df(sparse_matrix, name_vector, top=100):
    non_zeros = sparse_matrix.nonzero()

    sparserows = non_zeros[0]
    sparsecols = non_zeros[1]

    if top:
        nr_matches = top
    else:
        nr_matches = sparsecols.size

    left_side = np.empty([nr_matches], dtype=object)
    right_side = np.empty([nr_matches], dtype=object)
    similairity = np.zeros(nr_matches)

    for index in range(0, nr_matches):
        left_side[index] = name_vector[sparserows[index]]
        right_side[index] = name_vector[sparsecols[index]]
        similairity[index] = sparse_matrix.data[index]

    return pd.DataFrame({'left_side': left_side,
                         'right_side': right_side,
                         'similairity': similairity})


vectorizer = TfidfVectorizer(min_df=1, analyzer=ngrams)
matrix = vectorizer.fit_transform(df)

matches = awesome_cossim_topn(matrix, matrix.transpose(), 10, 0.8)

matches_df = get_matches_df(matches, df, top=200)
matches_df = matches_df[matches_df['similairity'] < 0.99999]  # For removing all exact matches
x = matches_df.sample(10)
x.to_csv("../results/temp.csv", index=False)
