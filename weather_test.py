#!/usr/bin/env python
# encoding: utf-8

"""
TO RUN TESTS: JUST RUN THIS SCRIPT LIKE AN ORDINARY PYTHON SCRIPT FROM THE COMMAND LINE.
Like this: python weather_test.py

"""

from weather import retrieve, url_search, weather_data, weather_update, Lazy
import re
import py.test
def test_retrieve_islost():
    """
    checks that the retrieve function gives the right output for http://www.islostarepeat.com
    """
    
    assert retrieve('http://www.islostarepeat.com') == """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
	<head>
		<title>Is Lost a Repeat?</title>
		<style type="text/css">
			body {
 			  font-size: x-large;
			  font-family:"Helvetica Neue Light", "Helvetica Neue", Helvetica, Arial, sans-serif;
			  margin-left: 2em;
			}
			h1 {
			  color: red;
			  position: absolute;
			  top: 47%;
			  left: 42%
			}
			h3 {
			  color: white
			}
			h4 {
			  position: absolute;
			  top: 75%;
			  left: 41%
			}
			A:link {text-decoration: none; color: red}
			A:visited {text-decoration: none; color: red}
			A:active {text-decoration: none; color: red}
			A:hover {text-decoration: underline; color: red;}			
		</style>
		<link rel="alternate" type="application/rss+xml" title="RSS 2.0" href="http://islostarepeat.com/feed.rss" />
		<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
		<meta http-equiv="Content-Language" content="en-us" />
		<meta name="object.type" content="tvShows" />
		<meta name="tvShow.title" content="Lost" />
		<meta name="tvShow.starring" content="Matthew Fox, Evangeline Lilly, Terry O'Quinn, Josh Holloway, Dominic Monaghan" />
		<meta name="tvShow.link" content="http://bit.ly/ilar" />
		<meta name="tvShow.image" content="http://ecx.images-amazon.com/images/I/61vBJVMWSKL._SL500_AA240_.jpg" />
		<meta name="tvShow.description" content="From J.J. Abrams, the creator of Alias, comes the action-packed adventure that became a worldwide television event." />
		<meta name="tvShow.tags" content="interconnectedness,love,suffering,plane crash,island adventure" />
	</head>
	<body>
		<div>
			<h1><a href="http://bit.ly/ilarff">FOREVER</a></h1>
		</div>
		<script type="text/javascript">
    		var GoSquared={};
    		GoSquared.acct = "GSN-558662-K";
    			(function(w){
        			function gs(){
            			w._gstc_lt=+(new Date); var d=document;
            			var g = d.createElement("script"); g.type = "text/javascript"; g.async = true; g.src = "//d1l6p2sc9645hc.cloudfront.net/tracker.js";
            			var s = d.getElementsByTagName("script")[0]; s.parentNode.insertBefore(g, s);
        				}
        			w.addEventListener?w.addEventListener("load",gs,false):w.attachEvent("onload",gs);
    			})(window);
		</script>
		<script src="http://www.google-analytics.com/urchin.js" type="text/javascript"></script>
		<script type="text/javascript">
		_uacct = "UA-393103-1";
		urchinTracker();
        </script>
        <script type="text/javascript">
        //<![CDATA[
        document.write('<scr'+'ipt src="http://crazyegg.com/pages/scripts/8797.js?'+(new Date()).getTime()+'" type="text/javascript"></scr'+'ipt>');
        //]]>
        </script>
	<!-- Start Quantcast tag -->
		<script type="text/javascript" src="http://edge.quantserve.com/quant.js"></script>
		<script type="text/javascript">
		_qacct="p-b9IS_X1L8U09c";quantserve();</script>
		<noscript>
		<img src="http://pixel.quantserve.com/pixel/p-b9IS_X1L8U09c.gif" style="display: none" height="1" width="1" alt="Quantcast"/></noscript>
	<!-- End Quantcast tag -->
	</body>
</html>
"""

def test_url_search_Hannestad(): 
    """
    tests whether an url_search for Hannestad yields the correct link
    """
    assert url_search("Hannestad") == [u'http://www.yr.no/place/Norway/Østfold/Sarpsborg/Hannestad/forecast.xml']

def test_weather_data_temp():
    """
    checks that the weather_data function gives a temperature in Hannestad between -55 and 55 
    """
    assert -55<int(weather_data('Hannestad')['Hannestad']['temperature'])<55

def test_weather_update_temp():
    """
    checks that the weather_update function gives a temperature in Hannestad between -55 and 55 
    """
    pattern=r'temp:([-\d.]+)'
    match=re.search(pattern, weather_update('Hannestad'))
    if match:
        temp=int(match.group(1))
    assert -55<temp<55

    
def _doctest():
    """
    Doctests for class Lazy and function url_search
    """
    import doctest, weather
    return doctest.testmod(weather)
    
print 'PY.TEST TESTS:'
py.test.cmdline.main(["-v", 'weather_test.py'])
print 'DOCTEST TESTS:'
if _doctest()[0]==0: #_doctest()[0] gives the number of failed tests. There's only two doctest in the module, so _doctest()[0]==0 means they both passed. If one or both of the tests failed, doctest will automatically print out a message with more details
    print 'Doctest Lazy and Doctest url_search passed!'


