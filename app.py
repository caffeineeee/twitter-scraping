from snscrape.modules import twitter
from nltk.corpus import stopwords
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
import pandas as pd
import matplotlib.pyplot as plt
import re
import os
from tidak_sesuai_kbbi import terimakasih, sapaan
from place_lists_here import more_stopwords, bank_names

max_results = 100  # if 'max_results' set to 0, number of tweets are unlimited
queries = [
    "bifast error"  # insert the main search keyword (without any filters) here, e.g. 'python'
]
more_search_filters = (
    ""  # insert the search filters here, e.g. 'lang:id', 'since: 2016-04-26'
)

"""
How to get the Twitter search query (by any filters, e.g. text, @username, #hashtag, etc.)?

1) Open Twitter.
2) Search your query using the Advanced Search option.
3) Look at the search bar query's result, e.g. ["python" since: 2016-04-26] (ignore the square brackets).
4) Copy the query's result main search keyword, e.g. "python", to 'queries' variable.
5) Copy the query's result main search keyword, e.g. "since: 2016-04-26", to 'more_search_filters' variable.
"""


tweets = []

stop_factory = StopWordRemoverFactory()

data = stop_factory.get_stop_words() + more_stopwords


def scrape_search(query):
    scraper = twitter.TwitterSearchScraper(query + more_search_filters)
    return scraper


# create the Sastrawi stemmer
factory = StemmerFactory()
stemmer = (
    factory.create_stemmer()
)  # Stemming is used to remove any kind of suffix from the word and return the root word, e.g. "cooking" => "cook", "memikirkan" => "pikir".


def clean_text(text):
    # Convert text to lowercase
    text = text.lower()

    # Remove URI
    text = re.sub(r"(http|https)://[^\s]+", "", text)

    # Remove #hashtags
    text = re.sub(r"[#][\w_-]+", "", text)

    # # Remove @usernames, and #hashtags
    # text = re.sub(r"[@#][\w_-]+", "", text)

    # Remove numbers, symbols
    text = re.sub(r"\d+|[^\w\s]", "", text)

    # Remove all characters except lowercase roman alphabet
    text = re.sub(r"[^a-z]", " ", text)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Remove '@' sign
    text = re.sub("@", "", text)

    # Remove stopwords
    text = " ".join(
        [
            word
            for word in text.split()
            if word not in stopwords.words("indonesian")
            and word not in stopwords.words("english")
            and word not in data
        ]
    )

    # Remove strings containing only one character
    text = re.sub(r"\b\w{1}\b", "", text)

    # Replace any word that is the same as in 'terimakasih' list, e.g. 'makasi' atau 'thx' menjadi 'terimakasih'
    # Then, remove 'terimakasih'
    for word in terimakasih:
        text = re.sub(r"\b" + word + r"\b", "terimakasih", text)
    text = re.sub("terimakasih", "", text)

    # Replace any word that is the same as in 'kakak' list, e.g. 'mimin' atau 'bro' menjadi 'kakak'
    # Then, remove 'kakak'
    for word in sapaan:
        text = re.sub(r"\b" + word + r"\b", "kakak", text)
    text = re.sub("kakak", "", text)

    # Replace 'bi fast" menjadi 'bifast'
    text = re.sub("bi fast", "bifast", text)

    # Replace 'eror' menjadi 'error'
    text = re.sub("eror", "error", text)

    # Replace all derivatives of any bank names into it's root's bank word, e.g. 'bankbni' menjadi 'bni', 'halobca' menjadi 'bca', 'bankbsi_id' menjadi 'bsi'

    pattern = "(" + "|".join(re.escape(name) for name in bank_names) + ")"
    matches = re.findall(pattern, text, re.IGNORECASE)

    for match in matches:
        text = re.sub(r"\S*" + match + r"\S*", match, text)

    #  Replace all occurrences of a repeated word with a single instance, e.g. "regex yeah yeah regex" menjadi "regex yeah"

    text = re.sub(r"\b(\w+)\b\s+\b\1\b", r"\1", text)

    return stemmer.stem(text)


for query in queries:
    output_filename = (
        query.lower().replace('"', "").replace("'", "").replace(" ", "_") + ".xlsx"
    )

    scraper = scrape_search(query)
    i = 0
    for i, tweet in enumerate(scraper.get_items(), start=1):
        raw_data = [
            # tweet.id, tweet.rawContent, tweet.user.username, tweet.likeCount, tweet.retweetCount
            # applying functions, i.e. str(), before fetching the data (before it's inserted into an excel file), i.e. tweet.date. It will be more prone to err if you apply the function/method after it's in an excel file.
            str(tweet.date),
            tweet.user.username,
            # applying methods, i.e. .lower(), before fetching the data (before it's inserted into an excel file), i.e. tweet.rawContent. It will be more prone to err if you apply the function/method after it's in an excel file.
            tweet.rawContent,  # includes numbers, symbols, @username, #hashtag; raw.
            clean_text(
                tweet.rawContent  # excludes numbers, symbols, @username, #hashtag; cleaned.
            ),
        ]

        tweets.append(raw_data)

        if max_results and i > max_results:
            break

tweet_df = pd.DataFrame(
    tweets,
    columns=[
        "Tanggal",
        "Username",
        "Tweet (raw)",
        "Tweet (cleaned)",
    ],
)

# drop row duplicates based on columns in 'subset'
tweet_df.drop_duplicates(inplace=True, subset=["Username", "Tweet (cleaned)"])

# if file with the same name exists, remove it
file_path = "./output/" + output_filename
if os.path.isfile(file_path):
    os.remove(file_path)


## Extract every single word from 'Tweet (cleaned)' column, then track their count  ##
# count words in 'Tweet (cleaned)' column
words_df = (
    tweet_df["Tweet (cleaned)"]
    .str.split(expand=True)
    .stack()
    .value_counts()
    .reset_index()
)
words_df.columns = ["Word", "Count"]

## Extract bank words only, e.g. "bni", "bri", "mandiri" ##
# count each bank name words
bank_names_only_df = words_df.copy(deep=True)
bank_names_only_df = pd.DataFrame(bank_names_only_df)

bank_names_only_df.drop(
    bank_names_only_df[~bank_names_only_df["Word"].isin(bank_names)].index,
    inplace=True,
    errors="ignore",
)

bank_names_only_df = bank_names_only_df.reset_index()

bank_names_only_df = bank_names_only_df.drop(columns="index")

bank_names_only_df.columns = ["Bank Name", "Count"]

# print("words_df: \n", words_df, "\n\n --------- \n\n")
# print("bank_names_only_df: \n", bank_names_only_df, "\n\n --------- \n\n")

# write dataframes to Excel file
with pd.ExcelWriter(file_path) as writer:
    tweet_df.to_excel(writer, sheet_name="Tweet", index=False)
    words_df.to_excel(writer, sheet_name="Word Counts", index=False)
    bank_names_only_df.to_excel(writer, sheet_name="Bank Name Only Counts", index=False)

# create a bar chart for the number of tweets per bank
bank_names_only_df.plot(kind="bar", x="Bank Names", y="Tweets Count", color="purple")

# set the title and axis labels
plt.title("Number of Tweets per Bank")
plt.xlabel("Bank Names")
plt.ylabel("Tweets Count")

# show the plot
plt.show()
