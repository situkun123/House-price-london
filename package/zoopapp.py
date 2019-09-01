import sys
sys.path.append('situkun123/House-price-london/package')
import os
import pickle
import pandas as pd
import time
from fake_useragent import UserAgent
import requests
from bs4 import BeautifulSoup
import re ; import random
import numpy as np
from tqdm import tqdm
import math
import random
import datetime
import zoopasql as zsql
from multiprocessing import Pool

# Need more customisation more checks needed
def _url(postcode):
    '''postcode: London Postcode only
    '''
    out_url = f"https://www.zoopla.co.uk/for-sale/property/london/{postcode}/?page_size=100"
    return out_url


# Get html content
def call_zoopla(url, display_header = True):
    ua = UserAgent()
    headers2 = {'User-Agent':str(ua.random)}
    content1 = requests.get(url, timeout = 100, headers= headers2).text
    soup = BeautifulSoup(content1, 'lxml')
    if display_header == True:
        print(headers2)
    else: pass
    return soup

# Data cleaning ######################
def price(i):
    # start from 3
    b = str(i)
    c = re.findall('\n+(.*)\n+', b)[0]
    if 'POA' in c[0] or 'Shared ownership' in b:
        return np.nan
    else:
        result = re.sub('\D', '', c)
        return result

def propertyid(i):
    purl = str(i)
    result = re.findall('href=".*/(\d+)\?', purl)[0]
    return result

def bed_no(i):
    bed = str(i)
    result = re.findall('>(.*)</a', bed)[0]
    nuresult = re.findall('\d+', result)
    if 'Studio' in result:
        return '1'
    elif 'Parking/garage' in result or len(nuresult) == 0:
        return np.nan
    else:
        return nuresult[0]

def property_type(i):
    ptype = str(i)
    result = re.findall('>(.*)</a>', ptype)[0]
    if (('flat' or 'duplex' or 'studio'or 'Studio'or 'maisonette') in result) == True:
        return 'flat'
    elif ('Parking/garage' or 'Room' in result) == True:
        return 'Other'
    else:
        return 'house'
    

def address(i):
    # start from 3
    address_no = str(i)
    result = re.findall('>(\w?.*)</a>', address_no)[0]
    return result.strip()

def list_time(i):
    agent_list_time_no = str(i)
    result =  re.findall('Listed on\s\n\s*(.*)\n{3}',agent_list_time_no)[0]
    return result

def agent(i):
    agent_list_time_no = str(i)
    result = re.findall('<span>(.*)<',agent_list_time_no)[0]
    return result

def cloest_station(i):
    station = str(i)
    result = re.findall('title="(.*)"', station)[0]
    return result


#########################################

def separate_data(soup):
    spdata2 = soup.findAll("h2", { "class" : "listing-results-attr" }) # No beds
    len_data = len(spdata2)
    spdata1= soup.findAll("a", { "class" : "listing-results-price text-price" })[-len_data:] # price, property_url
    spdata3 = soup.findAll("a", { "class" : "listing-results-address" })[-len_data:] # address
    spdata4 = soup.findAll("p", { "class" : "top-half listing-results-marketed" }) # Listed_time, agent
    spdata5 = soup.findAll("span", { "class" : "nearby_stations_schools_name"}) # 1st, 2nd nearest tube station
    print(len(spdata1), len(spdata2), len(spdata3), len(spdata4), len(spdata5))
    assert len(spdata1) == len(spdata2) == len(spdata3) == len(spdata4) == len(spdata5)/2, 'Something wrong with parsing!'
    return [spdata1, spdata2, spdata3, spdata4, spdata5]

def combine_data(data):
    first = []; second=[]
    for a, b in enumerate(data[4]):
        if a%2 == 0:
            first.append(b)
        else: 
            second.append(b)
    assert len(first) == len(second)
    df = []
    base_url = 'https://www.zoopla.co.uk/for-sale/details/'
    for a, b, c, d, e, f in zip(data[0], data[1], data[2], data[3], first, second):
        df.append( ( 
                    propertyid(a), price(a), bed_no(b), address(c), 
                    property_type(b), list_time(d), agent(d), 
                    cloest_station(e), cloest_station(f)
                    ) )
    return df



# url detection and generation/ data processing
def url_generator(postcode):
    page_1 = _url(postcode)
    first_page = call_zoopla(page_1, display_header=False)
    search_no = str(first_page.findAll("span", {"class":"listing-results-utils-count"}))
    # patched recently, now deal with , in 1,000
    search_result = re.findall('(\d+,?\d+)', search_no)[0]
    search_result = int(search_result.replace(',',''))
    pagenumber= math.ceil(search_result/100)
    suburl = first_page.findAll("div", {"class":"paginate bg-muted"})
    suburlone = re.findall('href="(.*)"', str(suburl))[0][0:-1]
    base_url = "https://www.zoopla.co.uk"
    urls = [f"{base_url}{suburlone}{i}&amp;page_size=100" for i in range(1,pagenumber+1)]
    return [urls, search_result]

# testing Design for manchester
def url_generator2():
    page_1 = 'https://www.zoopla.co.uk/for-sale/property/manchester-city-centre/?page_size=100&pn=1'
    first_page = call_zoopla(page_1, display_header=False)
    search_no = str(first_page.findAll("span", {"class":"listing-results-utils-count"}))
    # print(search_no)
    # patched recently, now deal with , in 1,000
    search_result = re.findall('(\d+,?\d+)</span>', search_no)[0]
    search_result = int(search_result.replace(',',''))
    # print(search_result)
    pagenumber= math.ceil(search_result/100)
    suburl = first_page.findAll("div", {"class":"paginate bg-muted"})
    suburlone = re.findall('href="(.*)"', str(suburl))[0][0:-1]
    base_url = "https://www.zoopla.co.uk/for-sale/property/manchester-city-centre/?page_size=100&pn="
    urls = [f"{base_url}{i}" for i in range(1,pagenumber+1)]
    return [urls, search_result]


def process_data(url):
    ''' This function will conduct the whole process and produce a dataframe
    '''
    webpage = call_zoopla(url)
    sep_data = separate_data(webpage)
    comb_data = combine_data(sep_data)
    return comb_data

#multiprocessing
def _compile_data(urls=None):
    '''Multiprocess for getting data '''
    data = []
    if not urls:
        print('No data found!, Something is wrong')
    elif len(urls) == 1:
        data = process_data(urls[0])
    elif type(urls) is str:
        # used for single string url
        data = process_data(urls)
    elif len(urls) > 1 and type(urls) is not str:
        start = time.time()
        pool = Pool(6)
        data = list(pool.imap(process_data, urls))
        data = [item for sublist in data for item in sublist]
        # time.sleep(round(random.uniform(1, 3),1))
        pool.close()
        print(f"Time taken: {round(time.time()-start, 2)} s")
    return data

#single process
def compile_data(urls=None):
    ''' urls = [] or url = 'https://.....'
    '''
    data = []
    if not urls:
        print('No data found!, Something is wrong')
    elif len(urls) == 1:
        data = process_data(urls[0])
    elif type(urls) is str:
        data = process_data(urls)
    elif len(urls) > 1 and type(urls) is not str:
        for i in tqdm(urls):
            data.extend(process_data(i))
            time.sleep(round(random.uniform(1, 3),1))
    return data
# stats caluculation 
################################################
# Calculation need to be refine, it is reading the null value
def daily_stats(data, postcode): 
    # search_time = datetime.datetime.utcnow().date().strftime('%Y-%m-%d %H:%M:%S')
    search_time = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    data = data.dropna(subset=['price', 'bed_no'])
    data = data[data['price'] > 100000]
    no_list_property = len(data['property_id'])
    max_price = max(data['price'])
    min_price = min(data['price'])
    avg_price = round(np.mean(data['price']),0)
    std_price = round(np.std(data['price']), 3)
    flat = data[data['property_type'] == 'flat']['price']
    house = data[data['property_type'] == 'house']['price']
    if len(flat) == 0:
        flat =[0]
    if len(house) == 0:
        house = [0]
    return(postcode,search_time, no_list_property, min_price, max_price, avg_price,std_price, 
          len(flat), min(flat), max(flat), round(np.mean(flat),0), round(np.std(flat),0),
          len(house), min(house), max(house), round(np.mean(house),0), round(np.std(house),0))

def bed_no_stats(data, postcode):
    data = data.dropna(subset=['price', 'bed_no'])
    data = data[data['price'] > 100000]
    search_time = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    # search_time = datetime.datetime.utcnow().date().strftime('%Y-%m-%d %H:%M:%S')
    one = []; onec = 0
    two = []; twoc =0
    three = []; threec = 0
    four = []; fourc = 0
    fiveplus = []; fiveplusc = 0
    for a, b in zip(data['bed_no'], data['price']):
        if pd.isnull(b) == False:
            if a == 1.0:
                one.append(b); onec+=1
            elif a == 2.0:
                two.append(b); twoc+=1
            elif a ==3.0:
                three.append(b); threec+=1
            elif a == 4.0:
                four.append(b); fourc+=1
            elif a >= 5.0:
                fiveplus.append(b); fiveplusc+=1

        oneavg = round( (sum(one)/onec) if onec != 0 else 0, 0 )
        twoavg = round( (sum(two)/twoc) if twoc != 0 else 0, 0 )  
        threeavg = round( (sum(three)/threec) if threec != 0 else 0, 0 )
        fouravg = round( (sum(four)/fourc) if fourc != 0 else 0, 0 )
        fiveplusavg = round( (sum(fiveplus)/fiveplusc) if fiveplusc != 0 else 0, 0 )

    if len(one) == 0: one.append(0)
    if len(two) == 0: two.append(0)
    if len(three) == 0: three.append(0)
    if len(four) == 0: four.append(0)
    if len(fiveplus) == 0: fiveplus.append(0)
    # count, min, max, avg, std (1 bed, 2 bed, 3 bed, 4 bed, 5 and above)
    return(postcode, search_time, 
           onec, min(one), max(one), oneavg, round(np.std(one),3),
           twoc, min(two), max(two), twoavg, round(np.std(two),3),
           threec, min(three), max(three), threeavg, round(np.std(three),3),
           fourc, min(four), max(four), fouravg, round(np.std(four),3), 
           fiveplusc, min(fiveplus), max(fiveplus), fiveplusavg, round(np.std(fiveplus),3))

################################################
class house_data(object):
    datadf = None
    dailys = None
    bed_nos = None
    col_name = ['property_id','price', 'bed_no', 'address', 
                        'property_type', 'listed_time', 'agent', 
                                'first_station', 'second_station']
    def __init__(self, postcode):
        self.postcode = postcode.upper()
        if self.postcode == 'M1': # This is for manchester
            _url_gen = url_generator2()
        else: 
            _url_gen = url_generator(postcode)
        self.urls = _url_gen[0]
        self.listnumber = _url_gen[1]
        self.districtName = [i[0] for i in zsql.district_postcode if i[1] == postcode][0]
        print(f"Currently updating {postcode}")

    @classmethod
    def singleURL2data(clf, url=None):
        ''' urls = [] or url = 'https://.....'
        '''
        data = compile_data(urls=url)
        return pd.DataFrame(data, columns=clf.col_name)
    
    

    def get_data(self,as_pandas =True):
        '''get a combine dataset for a postcode area'''
        data = _compile_data(urls = self.urls)
        if as_pandas == False:
            return data
        elif as_pandas == True:
            df = pd.DataFrame(data, columns=self.col_name)
            df = df.sort_values(by='price',ascending=False)
            df['listed_time'] = pd.to_datetime(df['listed_time'])
            df['price'] = pd.to_numeric(df['price'])
            df['bed_no'] = pd.to_numeric(df['bed_no'])
            self.datadf = df
            return df

    def get_stats(self):
        '''Need to run  get_data first'''
        # phase 1, need to be improved a lot
        a = daily_stats(self.datadf, self.postcode)
        b = bed_no_stats(self.datadf, self.postcode)
        self.dailys = a; self.bed_nos = b
        return [a, b]

    def create_data(self,):
        '''dependent on get_data for new table'''
        # search_time = datetime.datetime.utcnow().date().strftime('%Y-%m-%d %H:%M:%S')
        search_time = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        zsql.data_entry_postcode(self.datadf, self.postcode)
        # add new log info to log table
        zsql.insert_newLogs(self.postcode, self.districtName, search_time)
        print(f'Table name: ###{self.postcode}--{self.districtName}\
                            ### is sucessfully updated to the database')

    def update_postcode_table(self):
        # # 
        search_time = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        # search_time = datetime.datetime.utcnow().date().strftime('%Y-%m-%d %H:%M:%S')
        # update log info
        zsql.update_logs(self.postcode, search_time)
        print(f"Update table: {self.postcode}--{self.districtName}\
                               ### sucessfully {'#'*20}")
        return zsql.update_entry_postcode(self.datadf, self.postcode)

    def upload_stats(self,):
        # 4 dependent on get_stats
        # search_time = datetime.datetime.utcnow().date().strftime('%Y-%m-%d %H:%M:%S')
        search_time = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        zsql.data_entry_dailystats(self.dailys)
        zsql.data_entry_bedroomstats(self.bed_nos)
        zsql.update_logs('daily_stats', search_time)
        zsql.update_logs('bedroom_stats', search_time)
        print(f'Table name: ### {self.postcode}--{self.districtName} ### is sucessfully updated to the daily_stats and bedroom_stats')

    @classmethod
    def zoop_stats(clf, postcode):
        ''' returns 4 stats of a postal area:
        1.average price paid
        2.current price 
        3.number of sale
        4.price change
        '''
        ua = UserAgent()
        headers2 = {'User-Agent':str(ua.random)}
        url = f'https://www.zoopla.co.uk/house-prices/browse/london/{postcode}'
        content = requests.get(url, headers=headers2, timeout=100).content
        soup = BeautifulSoup(content, 'lxml')

        #sub-function for formating 
        def zoop_stats_format(content):
            '''Use regex to format zoopla stats data from its analysis
            '''
            avg_price = re.findall('>(.*)</span>', str(content))[0]
            avg_price = avg_price.replace(',','')
            avg_price = avg_price.replace('£', '')
            avg_price = int(avg_price)
            return avg_price
        
        zoop_avg_paid = soup.find_all("span", {"class": "market-panel-stat-element-value js-market-stats-average-price"})
        zoop_avg_paid = zoop_stats_format(zoop_avg_paid)

        zoop_avg_current = soup.find_all("span", {"class": "market-panel-stat-element-value js-market-stats-average-value"})
        zoop_avg_current = zoop_stats_format(zoop_avg_current)

        zoop_sale = soup.find_all("span", {"class": "market-panel-stat-element-value js-market-stats-num-sales"})
        zoop_sale = zoop_stats_format(zoop_sale)

        zoop_change = soup.find_all("span", {"class": "market-panel-stat-element-value js-market-stats-value-change market-panel-stat-value-change-up"})
        if len(zoop_change)==0:
            zoop_change = soup.find_all("span", {"class": "market-panel-stat-element-value js-market-stats-value-change market-panel-stat-value-change-down"})

        zoop_change = zoop_stats_format(zoop_change)
    
        return [zoop_avg_paid, zoop_avg_current, zoop_sale, zoop_change]

    ####### OFFLINE MODE##### USE FOR AWS Lambda ##########
    def get_property_difference(self, as_pickle=True):  
        '''save df contains the new property as pkl'''
        data = self.datadf
        search_time = datetime.datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
        old_property_id = list(pd.read_pickle('./pickle/property_id_all.pkl'))
        new_property_id = list(data['property_id'])
        diff_property_id = [i for i in new_property_id if i not in old_property_id]
        diffdf = data[data['property_id'].isin(diff_property_id)]
        if as_pickle == True:
            path = f"./pickle/{self.postcode}.pkl"
            if os.path.exists(path) == True:
                diffdfold = pd.read_pickle(path)
                diffdfnew = pd.concat([diffdfold, diffdf]).drop_duplicates().reset_index(drop=True)
                diffdfnew.to_pickle(f"./pickle/{self.postcode}.pkl")
            else:
                diffdf.to_pickle(f"./pickle/{self.postcode}.pkl")
        else:
            pass
        f = open("./pickle/update_time.txt", 'w')
        f.write(f'Last {self.postcode} updated: {search_time}')
        f.close()

    
# A utility class
class utl(object):
    def __init__(self):
        self.timenow = datetime.datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
        
    def get_latest_property_id(self):
        '''This will get all property id from the database and 
            save as pickle file in  
            - USE BEFORE OFFLINE UPDATES
            - mainly used for machine learning modules'''
        property_id_all = zsql.zoopdatabase.allpropertyTable()['property_id']
        property_id_all.to_pickle("./pickle/property_id_all.pkl")
        f = open("./pickle/update_time.txt", 'w')
        f.write(f'Last property ID updated: {self.timenow}')
        f.close()
        print(f'file is saved in ./pickle/property_id_all.pkl at {self.timenow}')
