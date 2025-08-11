import pandas as pd
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

def plot_wordcloud_from_csv(csv_path, text_column="text"):
    """
    Reads a CSV, extracts the specified text column, and returns a matplotlib figure with the word cloud.
    Filters out common English stopwords and custom words.
    """
    df = pd.read_csv(csv_path)
    text = " ".join(df[text_column].astype(str))
    stopwords = set(STOPWORDS)
    # Add custom stopwords
    stopwords.update(["subreddit", "reddit", "redditors"])
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        stopwords=stopwords
    ).generate(text)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    plt.tight_layout()
    return fig