##Yquote.py
A command line tool written in Python to fetch stock prices from [Yahoo Finance](http://finance.yahoo.com/)

##Dependencies
For this tool to function correctly, you need to have the following modules installed.

* [Beautiful Soup](http://www.crummy.com/software/BeautifulSoup/)
* [Pretty Table](http://pypi.python.org/pypi/PrettyTable)

##Usage
	Pradeeps-MacBook-Pro:pradeepnayak$ ./yquote.py --stock google --market us
	+-------------+--------+----------+
	|  Stock Name | Price  | Exchange |
	+-------------+--------+----------+
	| Google Inc. | 596.33 |   NMS    |
	+-------------+--------+----------+

	For more help, do ./yquote.py --help

## Version
0.2.0

##License

[Creative Commons](http://creativecommons.org/licenses/by-nc-sa/3.0/)
