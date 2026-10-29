#Given a list of files and line numbers, extract them

import pandas as pd
import os.path
import zstandard as zstd
import io
import multiprocessing 
import sys
from multiprocessing import Pool
from pathlib import Path

def process_one_file(line_file, zip_file, output_file):
    relevant_lines = pd.read_csv(line_file, delimiter=",")

    relevant_lines["line"] = pd.to_numeric(relevant_lines["line"], errors="coerce")
    relevant_lines = relevant_lines.dropna(subset=["line"])
    relevant_lines["line"] = relevant_lines["line"].astype(int)

    relevant_lines = relevant_lines.drop_duplicates()

    relevant_lines = relevant_lines.sort_values(by=['line']).reset_index()

    #Avoid the same line number appearing twice
    relevant_lines = relevant_lines.groupby('line').first().reset_index()

    if disp == 1:
        print("There are " + str(len(relevant_lines)) + " relevant lines")
    
    rlc = 0

    fout = open(output_file, "w", encoding="utf-8")

    lc = 1
    foundAll = False

    try:
        with open(zip_file, 'rb') as fh:
            dctx = zstd.ZstdDecompressor()
            with dctx.stream_reader(fh) as reader:
                with io.TextIOWrapper(reader, encoding='utf-8') as text_file:
                    for line in text_file:
                        if lc == relevant_lines.at[rlc, 'line']:
                            # Extract the line
                            fout.write(str(lc) + ":" + line)

                            rlc += 1
                            if rlc >= len(relevant_lines):  # No more relevant lines
                                foundAll = True
                                break

                        lc += 1

                        if disp == 1:
                            if lc % 100000 == 0:
                                print(lc)
    except zstd.ZstdError as e:
        raise RuntimeError(
            f"ZSTD decompression failed for {zip_file}: {e}"
        ) from e
        
    fout.close()
    
    if disp == 1:
        print("Extracted " + str(rlc) + " lines")
    
drive_path = "/mnt/e/"
zipfile_dir = drive_path + "Postings/"
author_line_number_dir = drive_path + "Code/line_numbers/" 
output_dir = drive_path + "Code/output/"
isPosting = True

if (len(sys.argv) > 1):
    if (sys.argv[1] == "postings"):
        zipfile_dir = drive_path + "Postings/"
        print("Extracting from postings")
    else:
        zipfile_dir = drive_path + "Comments/"
        print("Extracting from comments")
        isPosting = False
else:
    print("Defaulting to extracting postings")

start_year = 2005
end_year = 2026

if any(Path(output_dir).iterdir()):
    raise RuntimeError(f"Output directory is not empty")
    
disp = 0

def process_one_file_wrapper(year, month):

    line_file = (
        author_line_number_dir +
        f"relevant_lines_{year}-{month:02d}.tsv"
    )

    if isPosting:
        zip_file = (
            zipfile_dir +
            f"{year}/RS_{year}-{month:02d}.zst"
        )
        out_file = (
            output_dir +
            f"/filteredRS_{year}-{month:02d}.tsv"
        )
    else:
        zip_file = (
            zipfile_dir +
            f"{year}/RC_{year}-{month:02d}.zst"
        )
        out_file = (
            output_dir +
            f"/filteredRC_{year}-{month:02d}.tsv"
        )

    if os.path.isfile(line_file) and os.path.isfile(zip_file):
        print(f"Started processing {year}-{month:02d}")
        process_one_file(line_file, zip_file, out_file)
    elif disp == 1:
        print(f"Skipped {year}-{month:02d}")
        
tasks = []

tasks = [
    (year, month)
    for year in range(start_year, end_year + 1)
    for month in range(1, 13)
]

if __name__ == "__main__":
    with Pool(processes=os.cpu_count()) as pool:
        pool.starmap(process_one_file_wrapper, tasks)