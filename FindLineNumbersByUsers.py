#Given a list of author names, find the files and line numbers where they have entries

import pandas as pd
import os.path
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

def process_month(year, month, keep_authors):

    if isPosting:
        file = f"{author2file_dir}{year}/RS_{year}-{month:02d}_index.tsv.zst"
    else:
        file = f"{author2file_dir}{year}/RC_{year}-{month:02d}_index.tsv.zst"

    out_file = f"{author_line_number_dir}relevant_lines_{year}-{month:02d}.tsv"

    if not os.path.isfile(file):
        return f"Skipped {file}"

    try:
        # Define the chunk size (e.g., 500,000 rows at a time)
        chunk_size = 500_000 
        
        # Create an iterator
        reader = pd.read_csv(
            file,
            compression="zstd",
            delimiter=r":|\t",
            engine="python",
            header=None,
            names=["line", "author"],
            chunksize=chunk_size
        )

        first_chunk = True
        for chunk in reader:
            # Filter the chunk
            filtered_chunk = chunk[chunk["author"].isin(keep_authors)]
            
            if not filtered_chunk.empty:
                # Write to CSV: use 'a' (append) mode
                # Only write the header for the very first chunk that has data
                filtered_chunk.to_csv(
                    out_file, 
                    mode='a', 
                    index=False, 
                    header=first_chunk
                )
                first_chunk = False
            #else:
            #    print(f"Empty chunk in {year}-{month:02d}") 
                
        return f"Processed {year}-{month:02d}"
        
    except Exception as e:
        return f"Error {file}: {e}"

drive_path = "/mnt/f/"
author2file_dir = drive_path + "Posting_authors/"
author_list = drive_path + "Code/post_and_comment_authors.xlsx"
author_line_number_dir = drive_path + "Code/line_numbers/"
isPosting = True

if (len(sys.argv) > 1):
    if (sys.argv[1] == "postings"):
        author2file_dir = drive_path + "Posting_authors/"
        print("Extracting from postings")
    else:
        author2file_dir = drive_path + "Comment_authors/"
        print("Extracting from comments")
        isPosting = False
else:
    print("Defaulting to extracting postings")

start_year = 2005
end_year = 2026

if any(Path(author_line_number_dir).iterdir()):
    raise RuntimeError(f"Line number directory is not empty")
    
keep_authors = set(pd.read_excel(author_list)["author"])

tasks = [
    (year, month)
    for year in range(start_year, end_year + 1)
    for month in range(1, 13)
]

with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:

    futures = [
        executor.submit(process_month, year, month, keep_authors)
        for year, month in tasks
    ]

    for future in as_completed(futures):
        print(future.result())
            

