
# Updates the IFDB ratings for current ifcomp games.
import datetime
import time

import pandas

import ifdb

filled_data = pandas.read_csv('data_2022.tsv', sep='\t', index_col=None)
new_rows = []

end_date = datetime.datetime(2022, 11, 15)

for i, row in filled_data.iterrows():
    new_row = row.copy()
    title = row['title']
    print(i, title)
    ifdb_id = row['ifdb_id']
    print(ifdb_id)
    print('old ratings: {0} {1}'.format(row['ifdb_rating'], row['ifdb_rating_count']))
    try:
        rating, count = ifdb.get_ratings(ifdb_id, end_date)
        if count >= row['ifdb_rating_count']:
            new_row['ifdb_rating'] = rating
            new_row['ifdb_rating_count'] = count
            print('new ratings: {0} {1}'.format(rating, count))
            time.sleep(0.5)
    except:
        pass
    new_rows.append(new_row)

df = pandas.DataFrame(new_rows)
df.to_csv('data_2022.tsv', sep='\t', index=None) 
