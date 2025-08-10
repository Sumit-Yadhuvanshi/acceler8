import pandas as pd
import re

def remove_urls(text):
    return re.sub(r'http\S+|www\.\S+|https?://\S+|\S+\.(jpg|jpeg|png|gif|webp)', '', str(text))

def filter_and_clean_reddit_csv(input_path: str, output_path: str):
    """
    Reads a CSV file, keeps only 'type', 'post_id', and 'text' columns,
    removes URLs from 'text', groups by 'post_id' (joining texts), and writes to a new CSV.
    """
    df = pd.read_csv(input_path)
    filtered = df[['type', 'post_id', 'text']]
    filtered['text'] = filtered['text'].apply(remove_urls)
    grouped = filtered.groupby(['post_id'])['text'].apply(lambda texts: ' '.join(texts)).reset_index()
    grouped.to_csv(output_path, index=False)