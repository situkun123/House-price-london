sys.path.append('situkun123/House-price-london')
import pandas as pd
import time
import requests
import re ; import random
import sys
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

#### Get the disrable postcode ready ###########
district_postcode = [
    ('Hackney', 'E8'), ('E-head', 'E1'), ('Bethal green', 'E2'), 
    ('EC-head', 'EC1'), 
    ('Bishopsgate', 'EC2'),
    ('French chruch street', 'EC3'), ('Fleet strett', 'EC4'), 
    ('N-head', 'N1'),  
    ('Highbury', 'N5'), ('Highgate', 'N6'), 
    ('Finsbury park', 'N4'),
    ('NW-head', 'NW1'),('Cricklewood', 'NW2'), ('Hampstead', 'NW3'), ('Kentish town', 'NW5'),
    ('Kilburn', 'NW6'), 
    ('St John wood', 'NW8'),('SE-Head', 'SE1'),
    ('Greenwich', 'SE10'), 
    ('SW-Head', 'SW1'),  
    ('Chelsea', 'SW3'),
    ('Clapham', 'SW4'), ('Earls court', 'SW5'),('Fulham', 'SW6'),
    ('South kensington', 'SW7'), 
    ('South lambeth', 'SW8'), ('Stockwell', 'SW9'),
    ('West Brompton', 'SW10'),('SW-head2', 'SW11'),('Paddington','W2'),
    ('North Kensington', 'W10'), 
    ('Notting hill', 'W11'), 
    ('West Kensington', 'W14'),
    ('WC-head', 'WC1'), 
    ('Strand', 'WC2'),
    ('Manchester city centre', 'M1')
    ]

district_postcode_dict = dict(district_postcode)
inver_district_postcode_dict = {b:a for a, b in district_postcode_dict.items()}
first_run = list(district_postcode_dict.values())
part1 = first_run[0:int(len(first_run)/3)]
part2 = first_run[int(len(first_run)/3):int(len(first_run)*2/3)]
part3 = first_run[int(len(first_run)*2/3):]
testpart=first_run[:3]

##################Postcode in borough##########
postcode_in_borough = {
    'Hackney': ['E8', 'N1', 'N4'],
    'Tower Hamlets':['E1', 'E2'],
    'Camden':['EC1', 'N6', 'NW1', 'NW2', 'NW3', 'NW5', 'NW6', 'NW8', 'WC1'],
    'City of London': ['EC2', 'EC3', 'EC4', 'WC1'],
    'Islington': ['N5',],
    'Lambeth' : ['SE1', 'SW4','SW8', 'SW9'],
    'Greenwich': ['SE10'],
    'Kensington and Chelsea':['SW1', 'SW3', 'SW5', 'SW7'],
    'Hammersmith and Fulham': ['SW10', 'W14'],
    'Wandsworth':['SW11', ],
    'Westminster':['W2', 'W10', 'W11', 'WC2'],
}
#############################################

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
        print(f"{len(diff_property_id)} is added to table {postcode}")
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

## a function for changing station name in the database
def data_correct_station_name(postcode, old_value, new_value):
    conn = sqlite3.connect(dbpath, timeout=10)
    c = conn.cursor()
    c.execute(f'''UPDATE {postcode}
                SET first_station = "{new_value}" WHERE first_station = "{old_value}"
                ''')
    c.execute(f'''UPDATE {postcode}
                SET second_station = "{new_value}" WHERE second_station = "{old_value}"
                ''')
    conn.commit()
    c.close()
    conn.close()
    
## an excution function for changing station name in the database
class correction(object):
    def __init__(self):
        self.station_name_change_value = [
     ('Caledonian Road &amp; Barnsbury','Caledonian Road & Barnsbury'), 
     ('Edgware Road Bakerloo', 'Edgware Road'),
     ('Edgware Road Circle', 'Edgware Road'), ('Elephant &amp; Castle', 'Elephant & Castle'), 
     ('Finchley Road &amp; Frognal', 'Finchley Road & Frognal'), ('Hammersmith (D &amp; P)', 'Hammersmith'),
     ('Highbury &amp; Islington', 'Highbury & Islington'), ('Kensington Olympia', 'Kensington (Olympia)'),
     ('London Kings Cross', 'London Kings Cross & St Pancras International'),
     ('London St Pancras (Intl)','London Kings Cross & St Pancras International'),
     ('London St Pancras International', 'London Kings Cross & St Pancras International'), 
     ("King's Cross St. Pancras", 'London Kings Cross & St Pancras International'),
     ('Queens Park (London)', 'London Queens Park'),
     ("Shepherd's Bush Hammersmith &amp; City", "Shepherd's Bush"), ('St Johns (London)', 'London St Johns')
     ]
        self.dbpostcode = [i[1] for i in district_postcode]
    
    def correct_all_station_name(self):
        for i in self.dbpostcode:
            for b in self.station_name_change_value:
                data_correct_station_name(i, b[0], b[1])
        print('Update Station Names Sucessfully!')

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
        '''Get one table and store as df
            - postal_area col added
        '''
        script = f"SELECT * FROM {table_name.upper()}"
        df = pd.read_sql_query(script, clf.conn)
        df['postal_area'] = [table_name.upper() for i in range(len(df))]
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
        '''get a combined historical property records 
            - no postal_area col 
        '''
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
    def allpropertyTable_borough(clf):
        '''Returns a df that contains all property data with borough.
            - postal_area col added
        '''
        borough_area_key = [i.upper() for i in postcode_in_borough.keys()]
        borough_area_value = postcode_in_borough.values()
        dflist = []
        for a,b in enumerate(list(borough_area_value)):
            dfpc = pd.DataFrame()
            for i in b:
                dfpc = dfpc.append(clf.onetable2df(i))
            dfpc['borough'] = [borough_area_key[a] for _ in range(len(dfpc))]
            dflist.append(dfpc)
        df = pd.concat(dflist, axis=0)
        return df
        
    @classmethod
    def downloadCSV(clf, table_name):
        '''download a tabele as a csv file
            :: if table_name = 'all', all property data will be downloaded
        '''
        timenow = datetime.datetime.today().strftime('%Y_%m_%d_%H_%M_%S')
        df = pd.DataFrame()
        if table_name == 'all':
            df = clf.allpropertyTable()
        else:
            df = clf.onetable2df(table_name)
        csvname = f"{table_name}_{timenow}.csv"
        df.to_csv(csvname)
        print(f"{csvname} is created in {os.getcwd()}")

    @classmethod
    def property_id2stats(clf, propertyID, postcode):
        squery = f"select * from {postcode} where property_id = {propertyID}"
        df = pd.read_sql(squery, clf.conn)
        return df.values.tolist()

    @classmethod
    def any_sql_query(clf, script):
        df = pd.read_sql_query(script, clf.conn)
        return df


class further_calculation(object):
    def __init__(self):
        return None
        
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
    def cumlative_PriceCAL(clf, postcode, ptype='all',last_6=False):
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
        elif ptype in ['1','2','3','4']:
            listedTime = df3[df3.bed_no == int(ptype)]['listed_time']
            df3 = df3[df3.bed_no==int(ptype)]
        elif ptype == '5':
            listedTime = df3[df3.bed_no >= int(ptype)]['listed_time']
            df3 = df3[df3.bed_no>=int(ptype)]
        else:
            print('This property type do not exist!')
        
        for i in listedTime:
            clum_price.append(df3[df3['listed_time']<= i]['price'].mean())
        df3['cuml_price'] = clum_price
        # just last 6 month of data
        if last_6 == True:
            last_6_date = datetime.datetime.now()
            last_6_date += datetime.timedelta(-6*30)
            df3=df3[df3.listed_time >= last_6_date]
            return df3
        else:
            return df3


    @classmethod
    def monthly_volume(clf, postcode):
        if postcode == 'all':
            df = zoopdatabase.allpropertyTable()
        else:
            df = zoopdatabase.onetable2df(postcode)
        df['listed_time'] = df['listed_time'].apply(lambda x: x[:7], 1)
        df['bed_no'] = df['bed_no'].apply(lambda x: 5.0 if x >= 5.0 else x, 1)
        # only looking at after Aug 2018
        dfvol1 = df[pd.to_datetime(df['listed_time']) >= pd.to_datetime('2018-08')]
        dfvol2 = dfvol1.groupby(['listed_time','bed_no'], as_index=False)['property_id'].count()
        dfvol2.rename(columns={'property_id': 'count'}, inplace=True)
        #find how many month in the df
        start = pd.to_datetime(dfvol2['listed_time'][0])
        end = pd.to_datetime(dfvol2['listed_time'][len(dfvol2)-1])
        month_diff = (end.year - start.year) * 12 + (end.month - start.month)
        dfvol2 = dfvol2.sort_values(by=['bed_no', 'listed_time'])
        sliceall = [i*(month_diff+1) for i in range(0,month_diff+1)]
        slice1 = sliceall[0:-1]
        slice2 = sliceall[1:]
        #print(slice1); print(slice2)
        dfvol3 = [dfvol2.iloc[a:b] for a, b in zip(slice1,slice2)]
        dfvol4 = dfvol3[0]
        for i in range(1,5):
            dfvol4 = dfvol4.merge(dfvol3[i], on='listed_time')
        dfvol4.drop([i for i in dfvol4.columns if 'bed_no' in i], axis=1, inplace=True)
        dfvol4_col_name =  [f'{i} bedroom_volume' for i in range(1,6)]
        dfvol4_col_name.insert(0, 'listed_time')
        dfvol4.columns = dfvol4_col_name
        dfvol4['total_volume'] = dfvol4.apply(lambda x: x[1]+x[2]+x[3]+x[4]+x[5], 1)
        dfvol4['listed_time'] = pd.to_datetime(dfvol4['listed_time'])
        return dfvol4

    @classmethod
    def lower_upper_quantile(clf, postcode):
        '''precentile calculation 25%, 50%, 75%
        '''
        df = zoopdatabase.onetable2df(postcode)
    
        quntilelist = [['25%', '50%', '75%']]
        for i in range(1,6):
            if i != 5:
                tup = df[df['bed_no'] == i]['price'].quantile([0.25, 0.5, 0.75])
        
                quntilelist.append(list(map(int, tup)))
            else:
                tup = df[df['bed_no'] >= i]['price'].quantile([0.25, 0.5, 0.75])
                try:
                    quntilelist.append(list(map(int, tup)))
                except ValueError:
                    pass
    
        return quntilelist

################ Machine learning processing ##########
class machine_learning(object):
    def __init__(self, postcode):
        #postcode == 'all' means all data
        self.postcode = postcode
        if postcode == 'all':
            self.df = zoopdatabase.allpropertyTable()
        else:
            self.df = zoopdatabase.onetable2df(self.postcode)
    
    @classmethod
    def median_fillna(clf, df):
        '''Fillna by using median vaule of the number of bedroom 
            :: For example: NaN value in 1 bed property will be filled in with median of 1 bed property
        '''
        for i in range(1,6):
            if i != 5:
                median = df[df['bed_no']==i]['price'].median()
                df['price'] = df['price'].mask((df['price'].isnull()) & (df['bed_no']==i), 
                                                median)
            else:
                median = df[df['bed_no']>=i]['price'].median()
                df['price'] = df['price'].mask((df['price'].isnull()) & (df['bed_no']>=i),
                                                 median)
        return df
    
    def preprocessed_df(self, split_date =True):
        ''' Preprocess df to be ready for machine leaarning
            :: Sort property date by listed time
            :: Rearrange datetime into YEAR, MONTH, DAY
            :: One hot encoding 'first_station', 'second_station', 'property_type' columns
        '''
        df=self.df
        df=df.sort_values(by='listed_time')
        df.drop(['index', 'property_id', 'address', 'agent'], axis=1, inplace=True)
        subset = [i for i in df.columns if i !='price']
        df.dropna(subset=subset, inplace=True)
        df = self.median_fillna(df)
        df_numerical = df.drop(['property_type','first_station', 'second_station'], axis=1)
        df_dummy1 = pd.get_dummies(df['first_station'], prefix='first_station')
        df_dummy2 = pd.get_dummies(df['second_station'], prefix='second_station')
        df_dummy3 = pd.get_dummies(df['property_type'], prefix='property_type')
        df = pd.concat([df_numerical, df_dummy3,df_dummy1,df_dummy2], axis=1)
        if split_date == True:
            df.insert(0, 'year', pd.DatetimeIndex(df['listed_time']).year)
            df.insert(1, 'month',pd.DatetimeIndex(df['listed_time']).month)
            df.insert(2, 'day', pd.DatetimeIndex(df['listed_time']).day)
            df.drop('listed_time', axis=1, inplace=True)
        else: pass
        return df
    


