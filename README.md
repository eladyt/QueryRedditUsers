# QueryRedditUsers
This code is intended to be an efficient way to extract all postings made by a list of Reddit users.

Reddit data is stored in compressed bz2 files. It is assumed that the directory structure is main_directory/year/RS_year_month.bz2

The main idea of the code is to store a list of the author names for each line of the compressed bz2 files. Given an Excel table with a list of author names, we find which lines need to be pulled from each file, and a second process does this.

# Steps to execute:
1. Each bz2 file needs to be indexed. This is done once using a command such as:
   bzgrep -oPHn '(?<="author": ")[^"]*' RS_2024-01.bz2 > RS_2024-01_index.tsv
   The results should be stored in a directory with the structure main_directory/year/file
3. Given a list of author IDs, run the file ExtractByLineNumbers.py. Once it finishes, run FindLineNumbersMultiprocess.py or (if your machine doesn't support multithreading), FindLineNumbers.py.

