#! /usr/bin/python

''' Command line tool to fetch stock prices from Yahoo Finance '''

import re,urllib2,sys,getopt,time
from BeautifulSoup import BeautifulSoup
from prettytable import PrettyTable 
import os

# This functions contains the usage instructions
def usage():
	print """
	Usage: yquote.py --stock <stock name> [--market <market type>] [--exchange <exchange name>]
		
		-h         - prints the help and usage instructions
		
		--stock    - A comma separate list of stocks to search
		
		--market   - Specify the type of market. Currently only two markets are supported,
		             US(US Market) and IN (Indian Market). If not specified defaults to IN.
		
		--exchange - Specify the name of the exchange you want to filter results on. If not specified
					results from all the exchanges are returned
		
		--watch    - Specify this switch to constantly refresh your stock data. 
	

	Example: yquote.py --stock google --market us
	
	Version: 0.3.0
	
	Author: Pradeep Nayak (pradeep1288@gmail.com)
				
	"""

# Main functions from where the arguments are processed and other subroutines are called	
def main():
	try:
		opts, args = getopt.getopt(sys.argv[1:],"h",["help", "stock=", "market=", "exchange=", "watch"])
		
		# if no options are specified, print the usage instructions and exit
		if len(sys.argv) == 1:
			usage()
			sys.exit()
		# It also excepts just plain arguments as stock names
		if sys.argv[1]:
			stocks_to_search = sys.argv[1].split(',')
	
	except getopt.GetoptError, error:
		print str(error)
		usage()
		sys.exit(2)

	stock = None
	# defaulting the market = indian and exchange = All
	market = "in"
	exchange = "All"
	watch = False
	for o, a in opts:
		if o == "--market":
			market = a
		elif o in ("-h", "--help"):
			usage()
			sys.exit()
		elif o == "--stock":
			# support multiple stocks at once per @swagatn suggestion
			stocks_to_search = a.split(',')
		elif o == "--exchange":
			exchange = a
		elif o == "--watch":
			watch = True
		else:
			assert False, "unhandled option"
			usage()
			sys.exit()
	while watch:
		try:
			stock_searcher(stocks_to_search, market, exchange)
			time.sleep(2)
			os.system('clear')
		except KeyboardInterrupt:
			sys.exit()
	if watch == False:
		stock_searcher(stocks_to_search, market, exchange)

#Method takes the stock to be searched as argument and returns the table of results
def stock_searcher(stocks_to_search,market,exchange):
	stocks_table = PrettyTable(["Stock Name", "Price", "Exchange"])
	for search_stock in stocks_to_search:
		url = "http://finance.yahoo.com/lookup?s="+search_stock+"&t=s&m="+market
		content = urllib2.urlopen(url)
		soup = BeautifulSoup(content)

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
				exchange_type = row_entry[5].renderContents().replace("NSI","NSE")
				if exchange_type == exchange:
					stocks_table.add_row([stock_name,stock_price,exchange_type])
				elif exchange == "All":
					stocks_table.add_row([stock_name,stock_price,exchange_type])
				else:
					pass
	
		except Exception, e:
			print "Sorry. Could not find any resutls for: "+search_stock.upper()
		else:
			pass
		finally:
			pass
		print stocks_table

if __name__ == "__main__":
    main()
