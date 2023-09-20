import pandas as pd
import nltk
from nltk.corpus import stopwords
# nltk.download('punkt')
# nltk.download('stopwords')

STOP_WORDS = set(stopwords.words('english'))

def nltk_count_words(input_text:str, input_name:str, n_freq=10, text_magnify=100):

    # convert to lower and remove the name
    input_text = input_text.lower().replace(input_name.lower(), '')

    # get tokens
    tokens = [word for sent in nltk.sent_tokenize(input_text) for word in nltk.word_tokenize(sent)]

    # get only words from tokens
    words = [word for word in tokens if word.isalpha() and word not in STOP_WORDS]

    # count the frequencies and return as dataframe        
    fq = nltk.FreqDist(words)

    # construct the dataframe
    df = (
        pd.DataFrame(
            fq.most_common(n_freq), columns=['word', 'frequency']
        )
    )
    # get the text size for frequency
    df = (
        df
        .assign(text_size=(df['frequency'] / df.head(n_freq)['frequency'].sum()) * text_magnify).round(decimals=0)
        .drop(columns='frequency')
        .astype(
            {'text_size' : 'int8' }
        )
    )
    # clip upper and lower bounds
    df = (
        df
        .assign(text_size = df['text_size'].clip(upper=36, lower=12))
    )
    return df

# print(nltk_count_words(TEST_TEXT, 'Igor', text_magnify=120))