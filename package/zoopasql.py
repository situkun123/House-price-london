import pandas as pd
import time
import requests
import re ; import random
import sys
sys.path.append('situkun123/House-price-london')
import zoopapp
import numpy as np
import random 
import sqlite3
import datetime
import os


dailystats_col = ['postcode', 'search_time', 'no_list_property', 'min_price', 'max_price',  'avg_price', 'std',
                    'no_flat', 'flat_min_price', 'flat_max_price', 'flat_avg_price', 'flat_std',
                    'no_house', 'house_min_price', 'house_max_price', 'house_avg_price', 'house_std']
total_bed_col = ['postcode', 'search_time', 
                   'no_one', 'one_min_price', 'one_max_price',  'one_avg_price', 'one_std',
                    'no_two', 'two_min_price', 'two_max_price', 'two_avg_price', 'two_std',
                    'no_three', 'three_min_price', 'three_max_price', 'three_avg_price', 'three_std',
                    'no_four', 'four_min_price', 'four_max_price', 'four_avg_price', 'four_std',
                    'no_fivep', 'fivep_min_price', 'fivep_max_price', 'fivep_avg_price', 'fivep_std',]
dbpath = '/Users/work/Desktop/Oct/zoopanumber.db'

# Scraped housing data 
def data_entry_postcode(data, postcode): 
    '''Add table to sql database with scraped housing data
        FOR NEW TABLE ONLY'''   
    # search_time = datetime.datetime.today().strftime('%Y-%m-%d')
    conn = sqlite3.connect(dbpath)
    data.to_sql(f'{postcode}', con=conn, if_exists='fail')
    conn.close()
    print(f'Table name: {postcode} is sucessfully added to the database!')

def update_entry_postcode(data, postcode):
    '''Adds new scraped housing data into corresponding table!'''
    conn = sqlite3.connect(dbpath, timeout=10)
    c = conn.cursor()
    c.execute(f"SELECT property_id FROM {postcode}")
    old_property_id = [i[0] for i in c.fetchall()]
    new_property_id = data['property_id']
    diff_property_id = [i for i in new_property_id if i not in old_property_id]
    if len(diff_property_id) == 0:
        print('Nothing to update!')
    elif len(diff_property_id) != 0:
        newdata = data[data['property_id'].isin(diff_property_id)]
        newdata.to_sql(f'{postcode}', con=conn, if_exists='append')
        print(f"{len(diff_property_id)} is added to tabel {postcode}")
        print(f"These are the property_id: {diff_property_id}")
    conn.commit()
    c.close()
    conn.close()
    return len(diff_property_id)


# stats tables
def data_entry_dailystats(x):
    '''Add stats from house_data().get_stats to the TABLE: daily_stats'''
    assert len(x) == 17,  'The format of input data is not right!'
    conn = sqlite3.connect(dbpath, timeout=10)
    c = conn.cursor()
    # Clean this bloody mess
    c.execute('''INSERT INTO  daily_stats ('postcode', 'search_time', 'all_no', 'all_min_price', 
                                'all_max_price',  'all_avg_price', 'all_std', 'flat_no', 
                                'flat_min_price', 'flat_max_price', 'flat_avg_price', 'flat_std',
                                'house_no', 'house_min_price', 'house_max_price', 'house_avg_price', 
                                'house_std') 
                                VALUES(?, ?, ?, ?, 
                                        ?, ?, ?, ?, 
                                        ?, ?, ?, ?,
                                        ?, ?, ?, ?,
                                        ?)''', 
                                        (x[0], x[1], x[2], x[3],
                                         x[4], x[5], x[6], x[7],
                                         x[8], x[9], x[10], x[11],
                                         x[12], x[13], x[14], x[15],
                                         x[16])
                                         )
    conn.commit()
    c.close()
    conn.close()
    print('upload to table: ###daily stats### sucessfully!')

def data_entry_bedroomstats(x):
    '''Add stats from house_data().get_stats to the TABLE: bedroom_stats'''
    assert len(x) == 27, 'The format of input data is not right!'
    conn = sqlite3.connect(dbpath, timeout=10)
    c= conn.cursor()
    c.execute('''INSERT INTO bedroom_stats ('postcode', 'search_time', 
                   'one_no', 'one_min_price', 'one_max_price',  'one_avg_price', 'one_std',
                    'two_no', 'two_min_price', 'two_max_price', 'two_avg_price', 'two_std',
                    'three_no', 'three_min_price', 'three_max_price', 'three_avg_price', 'three_std',
                    'four_no', 'four_min_price', 'four_max_price', 'four_avg_price', 'four_std',
                    'fivep_no', 'fivep_min_price', 'fivep_max_price', 'fivep_avg_price', 'fivep_std') 
                                VALUES(?, ?, 
                                        ?, ?, ?, ?, ?,
                                        ?, ?, ?, ?, ?,
                                        ?, ?, ?, ?, ?,
                                        ?, ?, ?, ?, ?,
                                        ?, ?, ?, ?, ?
                                        )''', 
                                        (x[0], x[1], 
                                         x[2], x[3],x[4], x[5], x[6],
                                         x[7], x[8], x[9], x[10], x[11],
                                         x[12], x[13], x[14], x[15],x[16], 
                                         x[17], x[18], x[19], x[20], x[21],
                                         x[22], x[23], x[24], x[25], x[26], 
                                         ))
    conn.commit()
    c.close()
    conn.close()
    print('upload to table:###bedroom stats###  sucessfully!')

# update time log tables.
def insert_newLogs(table_name, description, search_time):
    conn = sqlite3.connect(dbpath, timeout=10)
    c= conn.cursor()
    c.execute("INSERT INTO update_logs (table_name, description, last_updated) VALUES(?, ?, ?)",(table_name, description, search_time))
    conn.commit()
    c.close()
    conn.close()
    

def update_logs(table_name, search_time):    
    conn = sqlite3.connect(dbpath, timeout=10)
    c = conn.cursor()
    sentence = f"UPDATE update_logs SET last_updated = '{search_time}' WHERE table_name = '{table_name}'"
    c.execute(sentence)
    conn.commit()
    c.close()
    conn.close()

#### Get the disrable postcode ready ###########
district_postcode = [
    ('Hackney', 'E8'), ('E-head', 'E1'), ('Bethal green', 'E2'), ('EC-head', 'EC1'), 
    ('Bishopsgate', 'EC2'),('French chruch street', 'EC3'), ('Fleet strett', 'EC4'), 
    ('N-head', 'N1'),  ('Highbury', 'N5'), ('Highgate', 'N6'), ('Finsbury park', 'N4'),
     ('NW-head', 'NW1'),('Cricklewood', 'NW2'), ('Hampstead', 'NW3'), ('Kentish town', 'NW5'),
       ('Kilburn', 'NW6'), ('St John wood', 'NW8'),('SE-Head', 'SE1'),
      ('Greenwich', 'SE10'), ('SW-Head', 'SW1'), ('Chelsea', 'SW3'),
       ('Clapham', 'SW4'), ('Earls court', 'SW5'),('Fulham', 'SW6'),
       ('South kensington', 'SW7'), ('South lambeth', 'SW8'), ('Stockwell', 'SW9'),
        ('West Brompton', 'SW10'), ('SW-head', 'SW11'), ('Paddington','W2'),
      ('North Kensington', 'W10'), ('Notting hill', 'W11'), ('West Kensington', 'W14'),
       ('WC-head', 'WC1'), ('Strand', 'WC2')
      ]
district_postcode_dict = dict(district_postcode)
first_run = list(district_postcode_dict.values())
part1 = first_run[0:int(len(first_run)/3)]
part2 = first_run[int(len(first_run)/3):int(len(first_run)*2/3)]
part3 = first_run[int(len(first_run)*2/3):]
#############################################
# Class to get tables from sql database

class zoopdatabase(object):
    '''Class to get tables from sql database '''
    conn =sqlite3.connect(dbpath, timeout=10)
    def __init__(self,):
        self.c = self.conn.cursor()
        
    @property     
    def get_tableName(self,):
        res = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table';") # Get table name
        table_name = [i[0] for i in res]
        return table_name
    
    @classmethod
    def onetable2df(clf, table_name, displayHead =False):
        '''
        Get one table and store as df
        '''
        script = f"SELECT * FROM {table_name.upper()}"
        df = pd.read_sql_query(script, clf.conn)
        name = clf.conn.execute(script) 
        namelist = list(map(lambda x: x[0], name.description))
        datecol = ['search_time', 'listed_time']
        for i in datecol:
            try:
                df[i]=pd.to_datetime(df[i])
            except:
                pass
        if displayHead == False:
            pass
        elif displayHead == True:
            print(f"The names for table cols: {namelist}")
        return df

    @classmethod
    def PostcodeDailySTATS(clf, postcode):
        ''' Get historical mean & median stats table for a post code address
        '''
        df = clf.onetable2df(postcode.upper())
        def df_mean_med(para, df):
            if para == 'all':
                df = df.groupby('listed_time').price.agg(['mean', 'median'])
                df.columns = [f'{para}_mean', f'{para}_median']
            elif para in ['house', 'flat']:
                df = df[df['property_type']==para].groupby('listed_time').price.agg(['mean', 'median'])
                df.columns = [f'{para}_mean', f'{para}_median']
            elif para in [1, 2, 3, 4]:
                df = df[df['bed_no']==para].groupby('listed_time').price.agg(['mean', 'median'])
                df.columns = [f'{para}bed_mean', f'{para}bed_median']
            elif para == 5:
                df = df[df['bed_no']>=para].groupby('listed_time').price.agg(['mean', 'median'])
                df.columns = [f'{para}plusbed_mean', f'{para}plusbed_median']
            return df
        dfall = df_mean_med('all', df); dfflat = df_mean_med('flat', df)
        dfhouse = df_mean_med('house', df); dfone = df_mean_med(1, df)
        dftwo = df_mean_med(2, df); dfthree = df_mean_med(3, df)
        dffour = df_mean_med(4, df); dffiveplus = df_mean_med(5, df)
        dft = dfall.join([dfflat, dfhouse, dfone, dftwo, dfthree, dffour, dffiveplus], how='outer')
        return dft

    @classmethod
    def allpropertyTable(clf,):
        '''get a combined historical property records '''
        name = [i for i in list(clf().get_tableName) if 'stats' not in i \
                                                and 'log' not in i] # no stats table
        sqlscr = ''
        for a,b in enumerate(name):
            if a != len(name)-1:
                sqlscr += f"SELECT * FROM {b} UNION ALL "
            else:
                sqlscr +=f"SELECT * FROM {b}"
        df = pd.read_sql_query(sqlscr, clf().conn)
        return df
        
    @classmethod
    def downloadCSV(clf, table_name):
        '''download a tabele as a csv file '''
        timenow = datetime.datetime.today().strftime('%Y_%m_%d_%H_%M_%S')
        df = clf.onetable2df(table_name)
        csvname = f"{table_name}_{timenow}.csv"
        df.to_csv(csvname)
        print(f"{csvname} is created in {os.getcwd()}")


class further_calculation(object):
    @classmethod
    def bedroom_stats_diff(clf, combine=True):
        data = zoopdatabase.onetable2df('bedroom_stats')
        data['search_time']=data['search_time'].apply(lambda x: str(x)[:10])
        data = data.groupby(['postcode','search_time']).mean()
        data = data[[i for i in data.columns if 'avg' in i]]
        datadiff = data.diff()
        datadiff.columns = [i+'_diff' for i in data.columns]
        if combine == True:
            datadiff = data.merge(datadiff, on =['postcode','search_time'])
            return datadiff
        else:
            return datadiff, data
    @classmethod
    def get_growth(clf, postcode):
        data = further_calculation.bedroom_stats_diff(combine=True)
        name =[]
        for i in data.columns:
            if 'diff' in i:
                list1 = data[i][1:].tolist()
                list1.append(np.nan)
                data[i] = list1
            else:
                name.append(i)
        name = [i[0:-10] for i in name]
        def growth_calc(x, i):
            if x[i+5] == 0 or x[i] == 0:
                return 0
            else:
                return round(x[i+5]/x[i]*100, 2)

            return round(x[i+5]/x[i]*100, 2)
        for i in range(5):
            data[f'{name[i]}_growth'] = data.apply(lambda x: growth_calc(x, i), 1)
        data = data.reset_index()
        data = data[data['postcode']==postcode.upper()]
        data.iloc[-1:, 7:] = np.nan
        return data
    @classmethod
    def cumlative_PriceCAL(clf, postcode, ptype='all'):
        '''ptype = {'all', '1', '2', 
                '3', '4', '5'}'''
        df = zoopdatabase.onetable2df(str(postcode).upper())
        df2 = df.sort_values(by='listed_time')[['property_id', 'price', 'bed_no', 'listed_time']]
        df3 = df2.groupby(['listed_time', 'bed_no'], as_index=False).mean()
        df3['listed_time'] = pd.to_datetime(df3['listed_time'])
        # selction for different property type
        clum_price = []
        listedTime = df3['listed_time']
        if ptype == 'all':
            pass
        elif ptype in [1,2,3,4]:
            listedTime = df3[df3.bed_no == ptype]['listed_time']
            df3 = df3[df3.bed_no==ptype]
        elif ptype == 5:
            listedTime = df3[df3.bed_no >= ptype]['listed_time']
            df3 = df3[df3.bed_no>=ptype]
        else:
            print('This property type do not exist!')
        for i in listedTime:
            clum_price.append(df3[df3['listed_time']<= i]['price'].mean())
        df3['cuml_price'] = clum_price
        return df3
