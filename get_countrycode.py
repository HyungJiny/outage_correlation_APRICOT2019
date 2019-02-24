from selenium import webdriver
from bs4 import BeautifulSoup
from multiprocessing import Process

import time
import requests
import sys
import json
import arrow


DEBUG=1
def deb( text ):
	if DEBUG==1:
		print(sys.stderr, text)

def get_data(area, country_code, start_time, end_time):
    APNIC_ECON_URL="http://data1.labs.apnic.net/ipv6-measurement/Economies/%s/%s.asns.json?m=1" % ( country_code, country_code )
    START=arrow.get( start_time )

    out = {
	    'meta': {},
        'isps': []
    } 

    out['meta']['country'] = country_code
    out['meta']['start'] = START.strftime("%Y-%m-%dT%H:%M:%S")
    out['meta']['stop'] = arrow.get( arrow.now() ).strftime("%Y-%m-%dT%H:%M:%S")

    r = requests.get( APNIC_ECON_URL )
    for thing in r.json():
        pct = thing['percent']
        asn = thing['as']
        name = thing['autnum']
        outages = []
        deb("processing %s" % name )
        deb("processing %s" % asn )
        ro = requests.get( "http://stat.ripe.net/data/prefix-count/data.json?resolution=8h&resource=AS%s&starttime=%s" % (asn, START.strftime("%Y-%m-%dT%H:%M:%S") ) )
        j = ro.json()
        v4_series = j['data']['ipv4']
        if v4_series[0]['prefixes'] == 0:
            v4_series = v4_series[1:]
        #if v4_series[-1]['prefixes'] == 0:
        # 	v4_series = v4_series[:-1]
        for idx,data in enumerate( v4_series ):
            # 50 {u'prefixes': 16, u'timestamp': u'2017-06-24T16:00:00', u'address-space': 141}
            if data['prefixes'] == 0:
        	    if len( v4_series ) > idx+1:
        		    outages.append( [data['timestamp'] , v4_series[idx+1]['timestamp']] )
        out['isps'].append({
            'asn': asn,
            'pct': pct,
            'name': name,
            'outages': outages
        })

    outputfile = open('./'+area+'/'+out['meta']['country']+'.json', 'w')
    outputfile.write(json.dumps(out, indent=2))
    outputfile.close()


driver = webdriver.Chrome('/Users/hyungjin/Documents/chromedriver')
driver.implicitly_wait(3)

countries = ['asia', 'america', 'africa', 'australia-and-oceania', 'europe']

for country in countries:
    driver.get('http://www.countryareacode.net/en/list-of-countries-according-to-continent/' + country)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    codes = soup.select('#countries > tbody > tr.odd > td:nth-child(2) > b')
    
    country_codes = open('./'+country+'_codes.txt', 'w')

    for code in codes:
        print('================= '+code.text.strip()+' ================')
        #p = Process(target=get_data, args=(country, code.text.strip(), '2018-01-01', '2019-01-01'))
        #p.start()
        #p.join()
        try:
            get_data(country, code.text.strip(), '2014-01-01', '2019-01-01')
        except ValueError:
            print('disconnected!!')
            continue
        print()
        country_codes.write(code.text.strip()+'\n')
    country_codes.close()
    time.sleep(3)

driver.close()