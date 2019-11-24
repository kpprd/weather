#!/usr/bin/env python
# encoding: utf-8
from weather import Lazy, retrieve, url_search, weather_data, weather_update, testfunc

def extreme():
    """
    No arguments.
    Returns a formatted and presentable string containing information about the warmest and coldest place in Norway at the next occurence of 13:00
    (although not really, since to save time and bandwidth the weather_data function only fetches information from 100 links)
    """
    lazydata=Lazy(weather_data)
    namedict=lazydata('', 13, 0)
    warmest_temp=-100
    coldest_temp=100
    for name in namedict:
        if int(namedict[name]['temperature'])>warmest_temp:
            warmest_place=name
            warmest_temp=int(namedict[name]['temperature'])
        if int(namedict[name]['temperature'])<coldest_temp: 
            coldest_place=name
            coldest_temp=int(namedict[name]['temperature']) 
    outstring= u'Warmest: {0}, {1} degrees C\nColdest: {2}, {3} degrees C'.format(warmest_place, warmest_temp, coldest_place, coldest_temp)
    return outstring
    

print extreme()