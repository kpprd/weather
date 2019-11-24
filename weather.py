#!/usr/bin/env python
# encoding: utf-8
import urllib
import re
import time
import cPickle as pickle
import os.path
import sys

"""
OBS: NOTE THAT THIS PROGRAM WAS WRITTEN FOR PYTHON 2.7

TO RUN PY.TEST TESTS AND DOCTESTS: RUN THE SCRIPT weather_test.py LIKE AN ORDINARY PYTHON SCRIPT FROM THE COMMAND LINE.
Like this: python weather_test.py

"""


def retrieve(URL):
    """
    Arguments: URL (string)
    Returns: The html content of the URL (string)
    
    """
    try:
        response = urllib.urlopen(URL)
    except:
        print 'Error! The link could not be opened! Please check your internet connection.'
        sys.exit(1)
    html = response.read()
    response.close()

def url_search(location):
    """
    Arguments: location (string)
    Returns: list of links to weather data
    
    Fetches the contents of the file http://fil.nrk.no/yr/viktigestader/noreg.txt, which containt a list of links to weather data for various places in Norway,
    and searches for links matching location. The function first searches for matching Stadnamn; if none is found, it searches for matching Kommune; if none
    is found it searches for Fylke; if none is found it returns an empty list. The function accepts wildcards(*).
    
    Example DOCTEST
    -------
    >>> url_search('O*lo')
    [u'http://www.yr.no/place/Norway/Oslo/Oslo/Oslo/forecast.xml']
    
    """
    
    location=str(location)
    location=location.decode('utf-8')
    location=location.replace('*', '.*')
    if location=='':
        location='.*'
    liste=[]
    data=retrieve('http://fil.nrk.no/yr/viktigestader/noreg.txt')
    i=0
    while i<3 and len(liste)==0: # len(liste)==0 makes the program exit the loop if something found e.g. for Stadnamn
        if i==0:
            # search for Stadnamn:
            pattern=r'\d+\t'+location+r'\t-?\d+\t.+(http.+forecast\.xml)' 
        elif i==1:
            # search for Kommune:
            pattern= r'\d+\t[\w ]+\t-?\d+\t[\w ]+\t[\w ]+\t[\w ]+\t'+location+r'\t[\w ]+\t[\d.]+\t[\d.]+\t\thttp.+?xml\thttp.+?xml\t(http.+?forecast\.xml)' 
        elif i==2:
            # search for Fylke
            pattern= r'\d+\t[\w ]+\t-?\d+\t[\w ]+\t[\w ]+\t[\w ]+\t[\w ]+\t'+location+r'\t[\d.]+\t[\d.]+\t\thttp.+?xml\thttp.+?xml\t(http.+?forecast\.xml)' 
        liste=re.findall(pattern, data, re.IGNORECASE)
        i+=1
    liste=list(set(liste)) #remove duplicates
    if len(liste)==0:
        print u'Sorry, no matches found for {0}'.format(location)
        sys.exit(1)
    return liste
    


def weather_data(place, hour=None, minute=None):
    """
    Arguments: place (string), hour (int; optional), minute (int; optional)
    Returns: A dictionary of dictionaries containing weather data. 
        Structure: (all times in epoch time) {<name of mathcing place>: {'time_from': <the time from which the data is valid>, 'temperature': <temperature>, 'wind': <wind speed>, 'time_to': <the time to which the data is valid>, 'expires': <the time as which the buffer expires (not the same as time_to if the data fetched from a future time period)>, 'rain': <amount of rain in mm>, 'summary': <short weather summary>}}
    
    If no arguments are given for hour and minute, the time is set to current time.
    """
    urls=url_search(place) # urls mathing place (see docstring for url_search for details)
    current_H = int(time.strftime('%H')) # current hour
    current_M = int(time.strftime('%M')) # current minute
    current_D =  int(time.strftime('%d')) # current day of month
    search_D = current_D # the day which will be used for searching later
    search_D_add=0
    namepattern=r'<name>(.+?)<\/name>'
    expirepattern=r'<tabular> \s+?<time from.+?to="([\d\-:T]+)"'
    if hour is None:
        hour=current_H # set hour to current hour if no argument is given
    if minute is None:
        minute=current_M # set minute to current minute if no argument is given
    if not 0<=hour<=23:
        print 'Error! hour must be a number from 0 to 23!'
        sys.exit(1)
    if not 0<=minute<=59:
        print 'Error! minute must be a number from 0 to 59'
        sys.exit(1)
    """
    The following demands some explanation.
    
    The xml files contains weather data divided into time periods: 00-06, 06-12, 12-18, and 18-00 (rumour has it a few files do not conform to this pattern, but I choose to ignore that for simplicity. I'm pretty sure they won't crash the program if they exist)
    
    The program uses "time to" in the xml file as key to finding the right set of data (see 'datapattern' below). Therefore the search_H (H for hour) and search_D (D for day) strings (which will be used in the regex search)
    must match the hour and day at the end of the proper time period. A complication is that yr.no updates the files every hour so that the current hour is not included in the time period. This is not a problem in this context
    (as we are searching for the 'time to' not the 'time from') unless the current time is in the last hour of a time period. A simple solution would be to set search_H to 6 if argument hour is between 0 and 6, and to 12 if argument
    hour is between 6 and 12, etc, but this causes problems if current hour is 5, 11, 17 or 23, since in these cases the data from the current period is deleted, so that setting search_H to 6, 12, 18 and 23, respectively, will cause
    an error. I have solved this problem by making search_H match the end of the following period instead (hence the and/not/or statements below)
    """
    if (0<=hour<6 and not (hour==current_H==5 and minute>=current_M)) or (hour==current_H==23 and minute>=current_M):
        search_H='06'
        if current_H==23:
            search_D_add = search_D_add + 86400 # adds one day (=86400 seconds) to the day search (one cannot just add 1 to search_D, as it would cause problems on the last day of the month)
    elif (6<=hour<12 and not (hour==current_H==11 and minute>=current_M)) or (hour==current_H==5 and minute>=current_M):
        search_H='12'
    elif (12<=hour<18 and not (hour==current_H==17 and minute>=current_M)) or (hour==current_H==11 and minute>=current_M):
        search_H='18'
    elif 18<=hour<24 or (hour==current_H==17 and minute>=current_M):
        search_H='00'
        search_D_add=search_D_add+86400 # sets search_H to 00, so the day must be updated accordingly (see comment below)
    if hour<=current_H and minute<current_M: # this adds 86400 seconds (= one day) to the search for current day, so that the program searches for tomorrow if the given time has passed.
        search_D_add=search_D_add+86400
    search_D=time.strftime('%d', time.localtime(time.mktime(time.localtime())+search_D_add))
    """
    The following pattern will be used to extract time from, time to, weather summary, precipitaion value, wind speed and temperature. 
    Note that 'search_D and search_H is inserted in the pattern within the 'time to' group, so that the pattern only matches when 
    'time to' correspond to these values. Also note that I have used [\s\S] (all non-space characters + all space-characters = all characters) 
    instead of . , as . doesn't match newlines. I know I can make . match newlines by passing re.S, but I kind of like to keep . as a 
    'everything but newline'-marker. I have also used ?P<something>, which enables me to extract the various groups with match.group('something'). 
    Other than that I think the pattern is pretty straightforward.
    
    """
    datapattern=r'<time from="(?P<from>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})" to="(?P<to>\d{4}-\d{2}-'+ str(search_D)+'T'+ str(search_H) +r':\d{2}:\d{2})" period[\s\S]+?<symbol[\s\S]+?name="(?P<summary>[\w\s]+?)"[\s\S]+?precipitation value="(?P<rain>[\d.]+)"[\s\S]*?windSpeed mps="(?P<wind>[\d.]+)"[\s\S]*?temperature[\s\S]*?value="(?P<temp>[-\d.]+)"'
    timepattern = '%Y-%m-%dT%H:%M:%S'
    namedict={}
    for url in urls[:100]: # in order to save time and bandwidth we're only fetching information from the first 100 links
        url=url.encode('utf-8')
        url_cont=retrieve(url)  
        errorpattern=r'<head>\s+?<title>Fant ikke[\s\S]+\/(.*?)\/forecast.xml'
        errormatch=re.search(errorpattern, url_cont) # search for error messages. matches errorpattern if link is broken
        if errormatch:
            print 'Link for {0} weather data does not work!'.format(errormatch.group(1))
        else:        
            match=re.search(namepattern, url_cont) # extracts name
            if match:
                name=match.group(1)
                expirepattern = r'<tabular>\s+?<time from.+?to="([\d\-:T]+)"'
                expirematch = re.search(expirepattern, url_cont) # extracts expire time, which will be used in the buffer. The buffer should be updated every time a new time period kicks in (as even forecasts for later times might be updated as time passes), so the expire time is the same as the 'time to' in the first data block in the file (the file says <tabular> before the first occurence, hence the <tabular> in 'expirepattern').
                if expirematch:
                    expire=int(time.mktime(time.strptime(expirematch.group(1), '%Y-%m-%dT%H:%M:%S')))
                #exctract data and store in dictionary
                datamatch=re.search(datapattern, url_cont)
                if datamatch:
                    datadict=dict(expires= expire, time_from=int(time.mktime(time.strptime(datamatch.group('from'), '%Y-%m-%dT%H:%M:%S'))), time_to=int(time.mktime(time.strptime(datamatch.group('to'), '%Y-%m-%dT%H:%M:%S'))),summary=datamatch.group('summary'), rain=datamatch.group('rain'), wind=datamatch.group('wind'), temperature=datamatch.group('temp'))
                    # store datadict in 'namedict', with name as key.
                    namedict[name]=datadict
    if len(namedict)==0: # prints error message and exits if no data is found
        print 'No functional links found. Please try a different search.'
        sys.exit(1)
    return namedict


def weather_update(place, hour=None, minute=None):
    """
    Arguments: place (string), hour (int; optional), minute (int; optional)
    Returns: a formatted and presentable weather forecast (string) for the given place at the next occurrence of the given time (i.e. the next day if the time has already passed the current day)
    
    If no arguments are given for hour and minute, these are set to the current time by default. I have chosen to structure the program so that most of the work is done in the weather_data function.
    
    The data is buffered, so that the function fetches data from a buffer file instead of from internet if a search matches a previous search and the buffer file is not obsolete (see docstring for class Lazy for more info)
    
    Example: weather_update('Oslo', 9, 5) # weather update for Oslo five past nine
    """
    lazydata=Lazy(weather_data)
    namedict=lazydata(place, hour, minute)
    outstring = ''
    
    """
    The following calculates the timestring, i.e. the part of the string that will give the time in the output.
    """
    Y= time.strftime('%Y') # current year
    m= time.strftime('%m') # current month
    d= time.strftime('%d') # current day
    current_H = int(time.strftime('%H'))
    current_M = int(time.strftime('%M'))
    if hour is None:
        hour=current_H
    if minute is None:
        minute=current_M
    print_epoch = int(time.mktime(time.strptime(d + '/' + m + ' ' + Y + ' ' + str(hour) + ':' + str(minute), '%d/%m %Y %H:%M'))) # calculates the time in epoch time (needed if adjustments must be made)
    if hour<current_H or (hour<=current_H and minute<current_M):
        print_epoch=print_epoch+ 86400 # adds one day (=86400 seconds) to epoch time if time has already passed the current day
    timestring = time.strftime("%d.%m.%y %H:%M", time.localtime(print_epoch)) #converts to a readable string
    if hour==current_H and minute>=current_M: # this, again, adresses the problem with yr updating their files so that the current hour is not included. Here the timestring is set to the next whole hour if the user gives arguments corresponding to a time later than the current minute in the current hour. If the next whole hour is midnight, the time is instead set to 23:59 for simplicity
        pattern=r'\d{2}:\d{2}'
        if current_H<23:
            timestring = re.sub(pattern, '{0}:00'.format(current_H+1), timestring)
        elif current_H==23:
            timestring = re.sub(pattern, '23:59', timestring)
    for name in namedict: # formats the part of the string containing the weather data
        outstring=outstring + u'\n{0}: {1}, rain:{2} mm, wind:{3} mps, temp:{4} deg C'.format(name, namedict[name]['summary'], namedict[name]['rain'], namedict[name]['wind'], namedict[name]['temperature'])
    outstring = timestring + outstring
    return outstring      

class Lazy:
    """
    This class handles the buffer. It saves a buffer of the retrieved weather data to disc, so that it can be fetched if a search is repeated for the same time period.
    If a new time period (00-06, 06-12, 12-18 and 18-00) kicks in, the old buffer is deleted, and new data is fetched from internet.
    
    The buffer is structured as a <weather data> dictionary, inside a <place name> dictionary, inside a <search> dictionary, inside an <expire time> dictionary.
    There are a couple of drawbacks associated with structuring the buffer this way. Firstly, since each search is stored individually, a search first for 'Oslo' and then
    later for 'Os*o' will store the same <weather data> for the same <place name> (Oslo) (some additional place names will also be found in the latter case) twice in the <search> dictionary, 
    once under 'Oslo' and once under 'Osl*'. Therefore, since the <search> is used for testing whether a new search is already in the buffer, the second search (e.g. 'O*lo') will 
    not be recognised and fetched from the buffer if the argument for the first search (e.g. 'Oslo') is not identical, even if the two searches yielded identical or overlapping results for <place name>. I personally consider
    this a relatively minor drawback, at least compared to what I see as the alternatives (e.g. doing regex searches on all the place names in the buffer, which could potentially risk
    fetching incomplete results and would not work when searching after Kommune, Fylke etc unless these are also included in the buffer, making the whole operation unweildily messy and complicated)
    
    Secondly, the buffer only stores data for one time period per place name. E.g. if the user passes weather_update('Oslo', 13, 0) followed by weather_update('Oslo', 23, 0), the data from
    the second search will overwrite the data from the first search, so that if the user later again passes weather_update('Oslo', 13, 0) the corresponding data will no longer be 
    stored in the buffer. (The same search twice within the same period or different searches within the same or different time periods  is of course fine, e.g. if weather_update('Oslo', 13, 0) is followed by 
    weather_update('Oslo, 14, 15) or weather_update('Bergen', 9, 0) is followed by weather_data('Trimsø', 23, 0) or weather_data('Ber*n',15, 0) the data will be
    fetched from the buffer.) I also consider this a relatively minor issue, although one I think it would be possible to solve without to much hassle in a differently structured buffer (but then
    again that buffer might cause problems of its own, etc...)
    
    The function testfunc (not belonging to this class) can be used to check whether the program fetches from the buffer or from the internet, as it will print out 'FETCHES FROM THE INTERNET!'
    in the latter case. See the example below (which also functions as a doctest). The optional timestamp argument in the constructor can be used to create expired buffer files for testing purposes (
    but note that the timestamp will only be saved to the buffer if the old buffer is obsolete or empty, which can be achieved by removing the old buffer file first, like in the example below).
    
    Example DOCTEST
    -------
    >>> if os.path.isfile('testfunc_buffer.txt'):
    ...     os.remove('testfunc_buffer.txt')
    >>> lazytest_expired=Lazy(testfunc, timestamp=10) # expired January 1st 1970 (ten seconds past midnight)
    >>> lazytest_not_expired=Lazy(testfunc, timestamp=time.mktime(time.localtime())+86400) # expires one day from now
    >>> a = lazytest_expired('Oslo', 13, 0)
    FETCHES FROM THE INTERNET!
    >>> b = lazytest_expired('Oslo', 13, 0) # expired buffer is deleted. Fetches from the internet
    FETCHES FROM THE INTERNET!
    >>> c = lazytest_not_expired('Oslo', 13, 0) # expired buffer (from previous search) is deleted. Fetches from internet
    FETCHES FROM THE INTERNET!
    >>> d = lazytest_not_expired('Oslo', 13, 0) # non-expired buffer is not deleted. Fetches from buffer
    >>>                                         # no print = success!
    """
    def __init__(self, func, timestamp=None):
        """
        Arguments: self, func (a function), timestamp (epoch time; optional)
        """
        self.func = func
        self.filename = func.__name__ + '_buffer.txt'
        if not os.path.isfile(self.filename): # creates a buffer file with an empty dictionary if buffer file does not exist
            bufferfil=open(self.filename, 'w')
            pickle.dump({}, bufferfil)
            bufferfil.close()
        self.timestamp=timestamp
    
    def __call__(self, search, hour, minute):
        """
        Arguments: self, search (string), hour (int), minute (hour)
        """
        current_Hour = int(time.strftime('%H')) # current hour
        current_Minute = int(time.strftime('%M')) # current minute
        if hour is None:
            hour=current_Hour
        if minute is None:
            minute=current_Minute
        if not 0<=hour<=23:
            print 'Error! hour must be a number from 0 to 23!'
            sys.exit(1)
        if not 0<=minute<=59:
            print 'Error! minute must be a number from 0 to 59'
            sys.exit(1)
        bufferfil=open(self.filename, 'r')
        self.buffer=pickle.load(bufferfil) # loads buffer
        bufferfil.close()
        if len(self.buffer)>0:
            current_time = time.mktime(time.localtime())
            expire_time = self.buffer.keys()[0]
            if expire_time<current_time:
                del self.buffer[expire_time] # delete buffer if obsolete
        outdict={}
        good=False
        current_Y = str(time.strftime('%Y')) # current year
        current_M = str(time.strftime('%m')) # current month
        current_D = str(time.strftime('%d')) # current day of month
        search_add=0
        for expire_time in self.buffer:
            for buffered_search in self.buffer[expire_time]:
                if search==buffered_search: # testes if current search matches a search (in the <search> dictionary) in the buffer
                    search_hour=hour
                    search_minute=minute
                    if (search_hour<current_Hour) or (search_hour<=current_Hour and search_minute<current_Minute):
                        #The next occurence of given time is tomorrow
                        search_add = search_add + 86400
                        # Adds 86400 seconds (=one day) to the epoch time (to be calculated below) since the next occurence is tomorrow
                    else:
                        #The next occurence of given time is today
                        if search_hour==current_Hour and search_minute>=current_Minute: #Fixes the ever-present problem of yr.no not including current hour in their  data files
                            if search_hour<23:
                                search_hour=search_hour+1
                                search_minute='00'
                            elif search_hour==23:
                                search_hour='23'
                                search_minute='59'
                                searc_add=search_add + 60 
                    search_time = int(time.mktime(time.strptime(current_Y+'-'+current_M+'-'+current_D+'T'+str(search_hour)+':'+str(search_minute)+':00', '%Y-%m-%dT%H:%M:%S'))) + search_add # converts to epoch time
                    # The following if test looks menacing, but it only extracts the time_from and time_to times (between which the data is valid) from the buffer and checks if search_time lies within this interval. (The [self.buffer[expire_time][buffered_search].keys()[0]] part just finds the first (<place name>) key in the <search> dictionary, as they (unless yr's been making a mess of it) all contain the same time stamps anyway.
                    if self.buffer[expire_time][buffered_search][self.buffer[expire_time][buffered_search].keys()[0]]['time_from'] <= search_time <= self.buffer[expire_time][buffered_search][self.buffer[expire_time][buffered_search].keys()[0]]['time_to']:
                        # Search is found in buffer and the time arguments matches the stored serach. Returns from buffer:'
                        good=True 
                        return self.buffer[expire_time][search]
        
        if not good:
            # Search is not stored in buffer, or buffer is obsolete. Fetches from internet:
            retval = self.func(search, hour, minute)
            if self.timestamp is None:
                expires = retval[retval.keys()[0]]['expires'] # extract expire time to be used as key in the expire dictionary
            else:
                expires = self.timestamp # set expire time according to the time stamp argument if this is given
            searchdict={search: retval} # places the new <place name> dictionary in the <search> dictionary
            expiredict={expires:searchdict} # places the new <search dictionary> in the <expire time> dictionary
            bufferfil=open(self.filename, 'r')
            self.buffer=pickle.load(bufferfil) # loads existing buffer
            bufferfil.close()
            if expires in self.buffer.keys():
                    self.buffer[expires]=dict(self.buffer[expires].items() + expiredict[expires].items()) # merges the new <expire time> with the old buffer
            else: # if the old buffer is empty, make the new <expire time> dictionary the new buffer (if the new expire time is not a key in the buffer, it means the buffer is empty (as buffers with obsolete epxire time stamp would have been deleted earlier on), unless someone has been messing with the timestamp argument, in which case refreshing the whole buffer is probably a good idea anyway)
                self.buffer=expiredict
            bufferfil=open(self.filename, 'w')
            pickle.dump(self.buffer, bufferfil) # save new buffer
            bufferfil.close()
            return retval




def testfunc(name, hour, minute):
    """
    A function used for testing (in combination with Lazy) that the buffer works. Prints out the message 'FETCHES FROM THE INTERNET!' and sends the arguments to the weather_data
    function if called. See the Lazy class docstring for an example. 
    """
    print 'FETCHES FROM THE INTERNET!'
    return weather_data(name, hour, minute)


if __name__ == '__main__':
    # Example of usage. Prints weather forecast for Oslo at next occurence of ten past 18
    print weather_update('Oslo', 18, 10)







