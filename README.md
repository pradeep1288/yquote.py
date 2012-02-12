##Yquote.py
A command line app built in python which gets you live stock prices and helps manage your portfolio showing your gains. The app fetches prices from Yahoo Finance [Yahoo Finance](http://finance.yahoo.com/)

##Dependencies
For this tool to function correctly, you need to have the following modules installed.

* [Beautiful Soup](http://www.crummy.com/software/BeautifulSoup/)
* [Pretty Table](http://pypi.python.org/pypi/PrettyTable)
* [SQLite3](http://www.sqlite.org/)

##Usage
	Pradeeps-MacBook-Pro:pradeepnayak$ ./yquote.py --stock google --market us
	+-------------+--------+----------+
	|  Stock Name | Price  | Exchange |
	+-------------+--------+----------+
	| Google Inc. | 596.33 |   NMS    |
	+-------------+--------+----------+

	For more help, do ./yquote.py --help

## Version
1.0.0 beta

##License

[Creative Commons](http://creativecommons.org/licenses/by-nc-sa/3.0/)
