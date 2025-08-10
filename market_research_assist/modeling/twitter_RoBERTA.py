from transformers import AutoModelForSequenceClassification
from transformers import TFAutoModelForSequenceClassification
from transformers import AutoTokenizer, AutoConfig
import numpy as np
from scipy.special import softmax
import pandas as pd

# Preprocess text (username and link placeholders)
def preprocess(text):
    new_text = []
    for t in text.split(" "):
        t = '@user' if t.startswith('@') and len(t) > 1 else t
        t = 'http' if t.startswith('http') else t
        new_text.append(t)
    return " ".join(new_text)

def chunk_text(text, tokenizer, max_length=512):
    tokens = tokenizer.tokenize(text)
    chunks = [tokens[i:i+max_length-2] for i in range(0, len(tokens), max_length-2)]
    return [tokenizer.convert_tokens_to_string(chunk) for chunk in chunks]

def pred(df, model, tokenizer, config):
    all_avg_scores = []
    for post_id in df['post_id'].unique():
        text = preprocess(df[df['post_id'] == post_id]['text'].values[0])
        chunks = chunk_text(text, tokenizer)
        all_scores = []

        for chunk in chunks:
            encoded_input = tokenizer(chunk, return_tensors='pt', truncation=True, max_length=512)
            output = model(**encoded_input)
            scores = softmax(output[0][0].detach().numpy())
            all_scores.append(scores)
        
        avg_scores = np.mean(all_scores, axis=0)
        all_avg_scores.append(avg_scores)
    return np.array(all_avg_scores)
def sentiment_main(data_path):
    """
    Reads data from the given path, performs sentiment analysis,
    and returns the overall average sentiment scores.
    """
    MODEL = f"cardiffnlp/twitter-roberta-base-sentiment-latest"
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    config = AutoConfig.from_pretrained(MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL)

    df = pd.read_csv(data_path)
    all_avg_scores = pred(df, model, tokenizer, config)
    overall_avg = np.mean(all_avg_scores, axis=0)
    # Map to label for easier interpretation
    label_scores = {config.id2label[i]: float(overall_avg[i]) for i in range(len(overall_avg))}
    return label_scores
