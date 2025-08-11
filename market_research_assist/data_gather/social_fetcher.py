import os
import sys
from typing import Any, Dict, List
import click
import praw
import tweepy
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
import csv

def fetch_reddit_data(
    tag: str, client_id: str, client_secret: str, user_agent: str, limit: int = 10
) -> List[Dict[str, Any]]:
    """Fetches posts from Reddit containing a specific tag, including top-level comments as separate rows."""
    console = Console()
    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
        )
        subreddit = reddit.subreddit("all")
        rows = []
        for post in subreddit.search(query=tag, limit=limit):
            post_id = post.id
            # Add the post itself
            rows.append({
                "source": "Reddit",
                "type": "post",
                "post_id": post_id,
                "author": f"u/{post.author.name}" if post.author else "[deleted]",
                "text": post.title,
                "url": post.url,
            })
            # Add top-level comments as separate rows
            post.comments.replace_more(limit=0)
            for comment in post.comments[:5]:
                rows.append({
                    "source": "Reddit",
                    "type": "comment",
                    "post_id": post_id,
                    "author": f"u/{comment.author.name}" if comment.author else "[deleted]",
                    "text": comment.body,
                    "url": post.url,
                })
        return rows
    except Exception as e:
        console.print(f"[bold red]Error fetching from Reddit: {e}[/bold red]")
        return []

def fetch_twitter_data(
    tag: str, bearer_token: str, limit: int = 10
) -> List[Dict[str, Any]]:
    """Fetches tweets from X (Twitter) containing a specific tag."""
    console = Console()
    try:
        api_limit = max(10, min(limit, 100))
        client = tweepy.Client(bearer_token)
        query = f"#{tag} -is:retweet"
        response = client.search_recent_tweets(
            query=query, max_results=api_limit, tweet_fields=["author_id", "created_at"]
        )
        tweets = []
        if response.data:
            for tweet in response.data:
                tweets.append(
                    {
                        "source": "X (Twitter)",
                        "type": "tweet",
                        "parent_id": "",
                        "post_id": tweet.id,
                        "author": f"id:{tweet.author_id}",
                        "text": tweet.text.strip(),
                        "url": f"https://twitter.com/anyuser/status/{tweet.id}",
                    }
                )
        return tweets
    except Exception as e:
        console.print(f"[bold red]Error fetching from X/Twitter: {e}[/bold red]")
        return []

def save_to_csv(data: List[Dict[str, Any]], filename: str = "social_data.csv"):
    """Save the collected social media data to a CSV file."""
    with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["source", "type",  "post_id", "author", "text", "url"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in data:
            writer.writerow(item)


@click.command()
@click.option("--tag", required=True, help="The tag/keyword to search for.")
@click.option("--limit", default=5, help="Items to fetch from each platform.")
def main(tag: str, limit: int):
    """A tool to fetch recent posts from X (Twitter) and Reddit based on a tag."""
    console = Console()
    load_dotenv()

    # Get credentials and validate
    creds = {
        "REDDIT_CLIENT_ID": os.getenv("REDDIT_CLIENT_ID"),
        "REDDIT_CLIENT_SECRET": os.getenv("REDDIT_CLIENT_SECRET"),
        "REDDIT_USER_AGENT": os.getenv("REDDIT_USER_AGENT"),
        "TWITTER_BEARER_TOKEN": os.getenv("TWITTER_BEARER_TOKEN"),
    }
    if any(value is None for value in creds.values()):
        console.print("[bold red]API credentials not found in .env file.[/bold red]")
        console.print("Please ensure all required keys are set.")
        sys.exit(1)

    all_data = []
    with console.status(f"[bold green]Fetching data for tag '{tag}'...[/bold green]"):
        reddit_data = fetch_reddit_data(
            tag,
            creds["REDDIT_CLIENT_ID"],
            creds["REDDIT_CLIENT_SECRET"],
            creds["REDDIT_USER_AGENT"],
            limit,
        )
        all_data.extend(reddit_data)
        # twitter_data = fetch_twitter_data(tag, creds["TWITTER_BEARER_TOKEN"], limit)
        # all_data.extend(twitter_data)

    if not all_data:
        console.print(f"No results found for tag '{tag}'.")
        return

    # --- Automated CSV path in data folder ---
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, "data/raw")
    os.makedirs(data_dir, exist_ok=True)
    csv_path = os.path.join(data_dir, f"social_data_{tag}.csv")
    save_to_csv(all_data, filename=csv_path)
    # ----------------------------------------

    # For Local testing
    # table = Table(title=f"Social Media Feed for Tag: #{tag}")
    # table.add_column("Source", style="cyan")
    # table.add_column("Author", style="magenta")
    # table.add_column("Content", style="green", overflow="fold")
    # table.add_column("Link", style="blue")

    # for item in all_data:
    #     comments_text = ""
    #     if item.get("comments"):
    #         comments_text = "\n".join(
    #             [f"{c['author']}: {c['text']}" for c in item["comments"]]
    #         )
    #     content = item["text"]
    #     if comments_text:
    #         content += f"\n[Comments:]\n{comments_text}"
    #     table.add_row(item["source"], item["author"], content, f"[link={item['url']}]link[/link]")
    # console.print(table)

if __name__ == "__main__":
    main()