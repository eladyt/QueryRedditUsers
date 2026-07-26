import json
import pandas as pd
import sys

def count_fields(file_path):
    field_counts = {}
    total_rows = 0
    skipped_rows = 0
    
    with open(file_path, 'r') as file:
        for line in file:
            fail = False
            
            try:
                record = json.loads(line)
            except:
                fail = True
                
            if fail:
                try:
                    record = json.loads(line[line.index('{'):])                
                    fail = False
                except:
                    fail = True
                    
            if fail == False:
                total_rows += 1
                for key, value in record.items():
                    if value is not None:
                        if key not in field_counts:
                            field_counts[key] = 0
                        field_counts[key] += 1
            else:
                skipped_rows += 1
                
    print("Found " + str(total_rows) + " rows and skipped " + str(skipped_rows) + " rows")
            
    return field_counts, total_rows
    
def filter_fields(file_path):
    fields_to_keep = {'author', 'created_utc', 'title', 'selftext', 'subreddit', 'permalink', 'author_flair_text'}
    
    filtered_data = []

    with open(file_path, 'r') as file:
        for line in file:
            fail = False
            
            try:
                record = json.loads(line)
            except:
                fail = True
                
            if fail:
                try:
                    record = json.loads(line[line.index('{'):])                
                    fail = False
                except:
                    fail = True
                    
            if fail == False:
                filtered_record = {key: value for key, value in record.items() if key in fields_to_keep}
                filtered_data.append(filtered_record)
    
    return filtered_data

if len(sys.argv) > 2:
    fn = sys.argv[1]
    outputFormat = sys.argv[2]
else:
    raise Exception("I need the output format (Excel/CSV/Parquet)")
    
#Load the data
df = pd.DataFrame(filter_fields(fn))

# Convert to an Excel sheet
match outputFormat:
    case "Excel":
        df.to_excel(
            fn + '.xlsx', 
            index=False, 
            engine='xlsxwriter', 
            engine_kwargs={'options': {'strings_to_urls': False}}
        )
    case "CSV":
        df.to_csv(fn + '.csv', index=False, sep = '\t',encoding="utf-8", escapechar='\\')
    case "Parquet":
        df = df.astype(str)
        df.to_parquet(fn + '.parquet', index=False)
    case _:
        raise Exception("I need the output format (Excel/CSV/Parquet)")
