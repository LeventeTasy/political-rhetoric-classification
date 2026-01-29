import os
import pandas as pd
from newspaper import Article, ArticleException



def get_existing_urls(csv_file: str) -> set:
    """Reads the CSV file and returns a set of URLs that are already saved."""
    if os.path.exists(csv_file) and os.path.getsize(csv_file) > 0:
        try:
            # We only read the 'url' column to save memory
            df = pd.read_csv(csv_file, usecols=['url'])
            return set(df['url'].tolist())
        except Exception as e:
            print(f"Warning: Could not read existing CSV ({e}). Starting fresh.")
    return set()


def clean_source_file(source_file: str, urls_to_remove: list):
    """Removes specific URLs (e.g., 403 Forbidden) from the source text file."""
    if not urls_to_remove:
        return

    print(f"\nCleaning up source file: Removing {len(urls_to_remove)} broken URLs...")

    try:
        with open(source_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        remove_set = set(urls_to_remove)

        with open(source_file, "w", encoding="utf-8") as f:
            for line in lines:
                if line.strip() not in remove_set:
                    f.write(line)
        print("Source file updated successfully.")
    except Exception as e:
        print(f"Error updating source file: {e}")


def process_articles(source_file: str, label: int, output_csv: str = "../../data/articles.csv"):
    """
    Reads URLs from a text file, downloads the articles, saves them to CSV,
    and removes broken links (403 Forbidden) from the source file.
    """
    print(f"\n=== STARTING PROCESS: {source_file} ===")

    # 1. Load Source URLs
    if not os.path.exists(source_file):
        print(f"Error: Source file not found: {source_file}")
        return

    with open(source_file, "r", encoding="utf-8") as f:
        source_urls = set(line.strip() for line in f if line.strip())

    # 2. Load Existing URLs (to avoid duplicates)
    existing_urls = get_existing_urls(output_csv)
    print(f"Total in source: {len(source_urls)} | Already in CSV: {len(existing_urls)}")

    # 3. Filter URLs to process
    urls_to_process = list(source_urls - existing_urls)
    print(f"Articles to download: {len(urls_to_process)}")
    print("-" * 40)

    if not urls_to_process:
        print("No new articles to process.")
        return

    # 4. Download and Parse
    new_data = []
    broken_urls_403 = []
    success_count = 0
    error_count = 0

    for url in urls_to_process:
        try:
            article = Article(url)
            article.download()
            article.parse()

            # Optional: Minimal content check
            if not article.text:
                print(f"Warning: Empty text extracted from {url}")

            new_data.append({
                "url": url,
                "title": article.title,
                "text": article.text,
                "label": label
            })

            print(f"Success: {url}")
            success_count += 1

        except Exception as e:
            error_msg = str(e)
            print(f"Error ({url}): {error_msg}")
            error_count += 1

            # Detect 403 Forbidden errors to remove them later
            if "403" in error_msg:
                print(f"--> 403 FORBIDDEN detected. Marking for deletion.")
                broken_urls_403.append(url)

    # 5. Save to CSV
    if new_data:
        df_new = pd.DataFrame(new_data)
        # Check if we need to write the header (only if file doesn't exist)
        write_header = not os.path.exists(output_csv)

        df_new.to_csv(output_csv, mode='a', index=False, header=write_header, encoding='utf-8')
        print(f"\nSaved {len(new_data)} new articles to {output_csv}.")

    # 6. Clean up broken links from source file
    if broken_urls_403:
        clean_source_file(source_file, broken_urls_403)

    print(f"\nSUMMARY: {success_count} succeeded, {error_count} failed ({len(broken_urls_403)} removed due to 403).")


if __name__ == "__main__":
    # Ensure the output directory exists
    os.makedirs("../../data", exist_ok=True)

    # Process Independent Articles (Label 0)
    process_articles(source_file="../../data/0urls.txt", label=0)

    # Process Propaganda/Gov Articles (Label 1)
    process_articles(source_file="../../data/1urls.txt", label=1)