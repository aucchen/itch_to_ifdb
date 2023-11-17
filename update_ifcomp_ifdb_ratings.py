
# Updates the IFDB ratings for current ifcomp games.
import datetime
import time

import pandas

import ifdb

filled_data = pandas.read_csv('data_2023.tsv', sep='\t', index_col=None)
new_rows = []

end_date = datetime.datetime(2023, 11, 15)
end_date = None

games = ifdb.get_rankings('IFComp 2023')
rankings = {}
for i, g in enumerate(games):
    rankings[g] = i+1
    if ':' in g:
        rankings[g.split(':')[0]] = i+1

for i, row in filled_data.iterrows():
    new_row = row.copy()
    title = row['title']
    print(i, title)
    ifdb_id = row['ifdb_id']
    print(ifdb_id)
    print('old ratings: {0} {1}'.format(row['ifdb_rating'], row['ifdb_rating_count']))
    #rating, count = ifdb.get_ratings(ifdb_id, end_date)
    # get ratings using the api instead.
    rating, count = ifdb.get_ratings_api(ifdb_id)
    if count >= row['ifdb_rating_count']:
        new_row['ifdb_rating'] = rating
        new_row['ifdb_rating_count'] = count
    print('new ratings: {0} {1}'.format(rating, count))
    new_row['Ranking'] = rankings[title]
    time.sleep(0.5)
    new_rows.append(new_row)

# get rankings


df = pandas.DataFrame(new_rows)
df.to_csv('data_2023.tsv', sep='\t', index=None) 
