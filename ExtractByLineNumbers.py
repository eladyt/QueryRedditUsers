#Given a list of author names, find the files and line numbers where they have entries

import pandas as pd
import os.path

author2file_dir = "<Directory to author index (which you generated with the bzgrep command)>"
author_list = "<Excel file with author list>"
author_line_number_dir = "<Temporary output directory>"

start_year = 2005
end_year = 2024

keep_authors = pd.read_excel(author_list)

for year in range(start_year, end_year+1):
    print(year)
    for month in range(1, 13):
        file = author2file_dir + str(year) + "/RS_" + str(year) + "-" + '{:02d}'.format(month) + "_index.tsv"
        if os.path.isfile(file):
            data = pd.read_csv(file, delimiter=":", header=None, names=['line', 'author'], usecols=[1,2])
            data = pd.merge(data, keep_authors, on='author', how='inner')
            data = data.reindex()
            if len(data) > 0:
                data.to_csv(author_line_number_dir + "relevant_lines_" + str(year) + "-" + '{:02d}'.format(month) + ".tsv", index=False)
