import subprocess
import sys
import os
from pathlib import Path

from data_clean.reeddit_clean import filter_and_clean_reddit_csv

# Import the sentiment analysis main function
from modeling.twitter_RoBERTA import sentiment_main

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <tag>")
        sys.exit(1)
    tag = sys.argv[1]

    # 1. Call the social_fetcher script to fetch and save data
    fetcher_path = Path(__file__).parent / "data_gather" / "social_fetcher.py"
    subprocess.run([sys.executable, str(fetcher_path), "--tag", tag], check=True)

    # 2. Clean the Reddit CSV
    project_root = Path(__file__).parent
    raw_data_dir = project_root / "data" / "raw"
    cleaned_data_dir = project_root / "data" / "cleaned"
    os.makedirs(cleaned_data_dir, exist_ok=True)

    input_csv = raw_data_dir / f"social_data_{tag}.csv"
    output_csv = cleaned_data_dir / f"filtered_social_data_{tag}.csv"

    filter_and_clean_reddit_csv(str(input_csv), str(output_csv))
    print(f"Filtered CSV saved to {output_csv}")

    # 3. Perform sentiment analysis and print results
    print("Performing sentiment analysis...")
    sentiment_scores = sentiment_main(str(output_csv))
    print("Overall average sentiment scores:")
    for label, score in sentiment_scores.items():
        print(f"{label}: {score:.4f}")

if __name__ == "__main__":
    main()