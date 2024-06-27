#Given a list of files and line numbers, extract them

import pandas as pd
import os.path
import bz2
import io
import multiprocessing 

def process_one_file(line_file, zip_file, output_file):
    relevant_lines = pd.read_csv(line_file, delimiter=",")
    relevant_lines = relevant_lines.drop_duplicates()
    relevant_lines = relevant_lines.sort_values(by=['line']).reset_index()

    #Avoid the same line number appearing twice
    relevant_lines = relevant_lines.groupby('line').first().reset_index()

    rlc = 0

    fout = open(output_file, "w", encoding="utf-8")

    lc = 1
    foundAll = False

    with bz2.open(zip_file, 'rb') as f:
        with io.TextIOWrapper(f, encoding='utf-8') as text_file:
            for line in text_file:
                if (lc == relevant_lines.at[rlc, 'line']):
                    #Extract the line
                    fout.write(line)

                    rlc += 1
                    if (rlc >= len(relevant_lines)): #No more relevant lines
                        foundAll = True
                        break

                lc += 1
                if (disp == 1):
                    if (lc % 1e5 == 0):
                        print(lc)
    fout.close()


zipfile_dir = "<Directory of Reddit files>"
author_line_number_dir = "<Temporary output directory (the output of ExtractByLineNumbers)>" 
output_dir = "<Output directory>"

start_year = 2005
end_year = 2023

disp = 0

for year in range(start_year, end_year+1):
    print(year)
    processes = []
    for month in range(1, 9):
        line_file = author_line_number_dir + "relevant_lines_" + str(year) + "-" + '{:02d}'.format(month) + ".tsv"
        zip_file  = zipfile_dir + str(year) + "/RS_" + str(year) + "-" + '{:02d}'.format(month) + ".bz2"
        out_file  = output_dir + "/filteredRS_" + str(year) + "-" + '{:02d}'.format(month) + ".tsv"

        if os.path.isfile(line_file) & os.path.isfile(zip_file):
            p = multiprocessing.Process(target=process_one_file, args=(line_file, zip_file, out_file))
            processes.append(p)
            p.start()
            print("Started process for " + str(month))
        else:
            if (disp == 1):
                print(str(month) + ": " + str(os.path.isfile(line_file)) + ", " + str(os.path.isfile(zip_file)))

    for p in processes:
        p.join()

