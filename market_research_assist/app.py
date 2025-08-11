import streamlit as st
from pathlib import Path
import subprocess
import sys
import os

from modeling.world_cloud import plot_wordcloud_from_csv
from modeling.twitter_RoBERTA import sentiment_main
from data_clean.reeddit_clean import filter_and_clean_reddit_csv

# Emoji icons for sentiment
SENTIMENT_ICONS = {
    "positive": "😊",
    "negative": "😞",
    "neutral": "😐"
}

st.title("Social Data Sentiment Analysis Pipeline")

tag = st.text_input("Enter tag for data fetching (e.g., 'gpt-5'):")

if st.button("Run Full Pipeline"):
    if not tag:
        st.warning("Please enter a tag.")
    else:
        # Fetching data
        with st.spinner("Fetching social data..."):
            fetcher_path = Path(__file__).parent / "data_gather" / "social_fetcher.py"
            result = subprocess.run(
                [sys.executable, str(fetcher_path), "--tag", tag],
                capture_output=True, text=True
            )
        if result.returncode != 0:
            st.error(f"Fetcher error: {result.stderr}")
        else:
            st.success("Data fetched successfully.")

            # Define paths
            project_root = Path(__file__).parent
            raw_data_dir = project_root / "data" / "raw"
            cleaned_data_dir = project_root / "data" / "cleaned"
            os.makedirs(cleaned_data_dir, exist_ok=True)

            input_csv = raw_data_dir / f"social_data_{tag}.csv"
            output_csv = cleaned_data_dir / f"filtered_social_data_{tag}.csv"

            # Cleaning data
            with st.spinner("Cleaning data..."):
                filter_and_clean_reddit_csv(str(input_csv), str(output_csv))
            st.success(f"Filtered CSV saved to {output_csv}")

            # Sentiment analysis
            with st.spinner("Performing sentiment analysis..."):
                sentiment_scores = sentiment_main(str(output_csv))
            st.subheader("Sentiment Scores")
            for label, score in sentiment_scores.items():
                icon = SENTIMENT_ICONS.get(label.lower(), "")
                st.write(f"{icon} **{label.capitalize()}**: {score:.4f}")

            # Word cloud
            with st.spinner("Generating word cloud..."):
                fig = plot_wordcloud_from_csv(str(output_csv), text_column="text")
            st.pyplot(fig)