#! /usr/bin/python

''' Command line tool to fetch stock prices from Yahoo Finance '''

import re,urllib2,sys,getopt
from BeautifulSoup import BeautifulSoup
from prettytable import PrettyTable 


# This functions contains the usage instructions
def usage():
	print """
	Usage: yquote.py --stock <stock name> [--market <market type>]
		
		-h       - prints the help and usage instructions
		
		--stock  - Specify the name of the stock of which you want to know the price
		
		--market - Specify the type of market. Currently only two markets are supported,
		           US(US Market) and IN (Indian Market). If not specified defaults to IN.
	

	Example: yquote.py --stock google --market us
	
	Version: 0.1.0
	
	Author: Pradeep Nayak (pradeep1288@gmail.com)
				
	"""


# Main functions from where the arguments are processed and other subroutines are called	
def main():
	try:
		opts, args = getopt.getopt(sys.argv[1:],"h",["help", "stock=", "market="])
		
		# if no options are specified, print the usage instructions and exit
		if len(sys.argv) == 1:
			usage()
			sys.exit()
	
	except getopt.GetoptError, error:
		print str(error)
		usage()
		sys.exit(2)
	stock = None
	# defaulting the market type to be indian
	market = "in"
	verbose = False
	for o, a in opts:
		if o == "--market":
			market = a
		elif o in ("-h", "--help"):
			usage()
			sys.exit()
		elif o == "--stock":
			search_stock = a
		else:
			assert False, "unhandled option"
	stock_searcher(search_stock,market)


#Method takes the stock to be searched as argument and returns the table of results
def stock_searcher(search_stock,market):
	url = "http://finance.yahoo.com/lookup?s="+search_stock+"&t=s&m="+market
	content = urllib2.urlopen(url)
	soup = BeautifulSoup(content)
	stocks_table = PrettyTable(["Stock Name", "Price", "Exchange"])

	# All the results are present in a <div id ="yfi_sym_results"></div>
	yfi_results = soup.find('div',id="yfi_sym_results")

	try:
		# get individual table entries
		yfi_table_entries = yfi_results.find('table').find('tbody').findAll('tr')
		for j in range(len(yfi_table_entries)):	
			row_entry = yfi_table_entries[j].findAll('td')
			# Yahoo finance lists some old resutls which are not valid, eliminating them
			if row_entry[0].renderContents().find('_a') != -1:
				continue
			stock_name = row_entry[1].renderContents()
			stock_price = row_entry[2].renderContents()
			exchange_type = row_entry[5].renderContents()
			stocks_table.add_row([stock_name,stock_price,exchange_type])
		print stocks_table
	
	except Exception, e:
		print "Sorry. Could not find your stock"
	else:
		pass
	finally:
		pass
		
if __name__ == "__main__":
	main()