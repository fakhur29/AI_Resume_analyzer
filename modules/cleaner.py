import re
import nltk
from nltk.corpus import stopwords

# Download stopwords if not already present
try:
    stopwords.words("english")
except LookupError:
    nltk.download("stopwords")

STOP_WORDS = set(stopwords.words("english"))


def clean_text(text):
    
    # remove URLs first (http/https links and bare domains like x.com/y)
    text = re.sub(r"http\S+|www\.\S+|\S+\.(com|io|org|net)\S*", " ", text)

    # lowercase
    text = text.lower()

    # remove special characters/punctuation, keep letters, numbers, spaces
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # remove stopwords
    words = text.split()
    words = [word for word in words if word not in STOP_WORDS]

    return " ".join(words)