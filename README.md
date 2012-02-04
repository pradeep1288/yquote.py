##What?
A command line tool written in Python to fetch stock prices from Yahoo Finance

##Dependencies
It needs to have the following python modules to function. The modules are:

* (Beautiful Soup)[http://www.crummy.com/software/BeautifulSoup/]
* (Pretty Table)[http://pypi.python.org/pypi/PrettyTable]

##Usage
	./yquote.py --stock google --market us
	Pradeeps-MacBook-Pro:pradeepnayak$ ./yquote.py --stock google --market us
	+-------------+--------+----------+
	|  Stock Name | Price  | Exchange |
	+-------------+--------+----------+
	| Google Inc. | 596.33 |   NMS    |
	+-------------+--------+----------+

##License