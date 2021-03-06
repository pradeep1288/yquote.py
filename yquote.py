#! /usr/bin/python
'''
App Name: yquote.py
Author: Pradeep Nayak
Version: 1.0.0
Description: A command line app built in python which gets you live stock prices and
helps manage your portfolio showing your gains. The app fetches prices from yahoo finance.
'''
import re,urllib2,sys,getopt,time
from BeautifulSoup import BeautifulSoup
from prettytable import PrettyTable 
from types import *
import os
import sqlite3

# This functions contains the usage instructions
def usage():
    print """
    Usage: yquote.py --stock <stock name> [--market <market type>] [--exchange <exchange name>]
        
        -h          - prints the help and usage instructions
        
        --stock     - A comma separate list of stocks to search
        
        --market    - Specify the type of market. Currently only two markets are supported,
                      US(US Market) and IN (Indian Market). If not specified defaults to IN.
        
        --exchange  - Specify the name of the exchange you want to filter results on. If not specified
                      results from all the exchanges are returned
        
        --watch     - Specify this switch to constantly refresh your stock data. 

        --portfolio - Use this switch to manage your portfolio. Specify various actions to manage your portfolio.
                      
                      create    - creates your portfolio for the first time
                      show      - displays your portfolio along with the gains
                      update    - Updates your portfolio and calculates your gain with the latest market prices
                      addstock  - add stocks to your portfolio
                      sellstock - sell stocks and update your portfolio
                      delete    - delete your entire portfolio
    

    Example: yquote.py --stock google --market us
    
    Version: 1.0.0
    
    Author: Pradeep Nayak (pradeep1288@gmail.com)
                
    """

# This class describes the basic stock object
class ystock:
    # Initializing basic ystock contructor
    def __init__(self,stock_id,stock_name,exchange,current_value):
        self.stock_id = stock_id
        self.stock_name = stock_name
        self.exchange = exchange
        self.current_value = current_value

# Highlight the gain based on loss/profit. loss is highlighted in red and profit in green
class highlight:
    def __init__(self, gain):
        self.gain = gain
    def get_str(self):
        if self.gain <= 0:
            return "\033[91m"+str(self.gain)+"\033[0m"
        else: 
            return "\033[92m"+"+"+str(self.gain)+"\033[0m"

# This class decsribeds the porfolio object and supported functions with the portfolio
class portfolio:
    def __init__(self, database):
        self.database = database
    
    #update: Updates your portfolio databases with the latest stock prices and the gains you made
    def update(self):
        try:
            print "Updating ....."
            conn = sqlite3.connect(self.database)
            c = conn.cursor()
            d = conn.cursor()
            c.execute('select * from portfolio')
            for row in c:
                url = "http://finance.yahoo.com/lookup?s="+row[0]+"&t=s&m=in"
                content = urllib2.urlopen(url)
                soup = BeautifulSoup(content)   
                yfi_results = soup.find('div',id="yfi_sym_results")
                yfi_table_entries = yfi_results.find('table').find('tbody').findAll('tr')
                latesval = float(yfi_table_entries[0].findAll('td')[2].renderContents())
                d.execute('update portfolio set cval=%f where sid="%s"' %(latesval,row[0]))
            conn.commit()                       
        except urllib2.URLError:
            print "You are currently not connected to the internet. Please check your network connection"
        except KeyboardInterrupt:
            sys.exit()
        except Exception, e:
            raise e
    
    #create: This function creates the portfolio database 
    def create(self):
        try:
            conn = sqlite3.connect(self.database)
            c = conn.cursor()
            c.execute('''create table portfolio
            (sid text UNIQUE, sname text, qty int, cval real, amntin real, mktval real, gain real)
            ''')
            conn.commit()
            c.close()
        except sqlite3.OperationalError:
            print "Sorry, portfolio already exists for you.\nHint: To view your portfolion do: yquote --portfolio show"
    
    #show: Displays your current portfolio
    def show(self):
        try:
            stocks_table = PrettyTable(["Stock ID", "Stock Name", "Qty", "Current Value", "Amount Invested", "Market Value","Gain"])
            conn = sqlite3.connect('portfolio.db')
            c = conn.cursor()
            d = conn.cursor()
            c.execute('select * from portfolio')
            for row in c:
                mktval = row[2]*row[3]
                gain = row[5]-row[4]
                d.execute('update portfolio set gain=%f,mktval=%f where sid="%s"' %(gain,mktval,row[0]))
            conn.commit()
            c.execute('select * from portfolio')
            for row in c:
                stocks_table.add_row([row[0],row[1],row[2],row[3],row[4],row[5],highlight(row[6]).get_str()])
            print stocks_table
        except sqlite3.OperationalError:
            print "You don't have a portfolio yet!\nHint: Create your portfolio : yquote --portfolio create"


    # addstock: This function is used  for adding stocks to the database
    def addstock(self):
        add_more = "y"
        try:
            conn = sqlite3.connect(self.database)
            stocks_to_search = raw_input("Enter the stock to search:")
            stock_array = get_stocks(stocks_to_search)
            sid = raw_input("Enter the Stock ID to add:")
            pval = raw_input("Enter the purchase price:")
            qty = raw_input("Enter number of stocks:")
            c = conn.cursor()
            for obj in stock_array:
                if obj.stock_id == sid:
                    amntin = float(pval)*int(qty)
                    mktval = int(qty)*float(obj.current_value)
                    c.execute('insert into portfolio values("%s","%s",%d,%f,%f,%f,%f)' %(obj.stock_id,obj.stock_name,int(qty),float(obj.current_value),amntin,mktval,0))
                    break
            conn.commit()
            add_more = raw_input("Continue adding more(y/n): ")
            if (add_more == "y"):
                c.close()
                conn.close()
                self.addstock()
            else:
                sys.exit()
        except sqlite3.IntegrityError: 
            print "%s already exists in your portfolio."%(sid)
            update_existing = raw_input("Update the %s in your portfolio with the entered values(y/n):"%(sid))
            if update_existing == "y":
                d = conn.cursor()
                result = d.execute('select amntin,qty from portfolio where sid="%s"'%(sid))
                row = result.fetchone()
                amntin = row[0] + int(qty)*float(pval)
                new_qty = int(qty) + row[1]
                c.execute('update portfolio set amntin=%f,qty=%d where sid="%s"'%(amntin,new_qty,sid))
                conn.commit()
            else:
                conn.close()
                self.addstock()
        except urllib2.URLError:
            print "You are currently not connected to the internet. Please check your network connection"
        except KeyboardInterrupt:
            sys.exit()
        except Exception, e:
            raise e

    #delstock: delete stocks from your portfolio
    def sellstock(self):
        sell_more = "y"
        self.show()
        try:
            while sell_more == "y":
                conn = sqlite3.connect(self.database)
                stock_to_sell = raw_input("Enter the Stock ID to sell:")
                qty_sell = raw_input("Enter total stocks to sell: ")
                c = conn.cursor()
                d = conn.cursor()
                qty_result = c.execute('select qty,amntin,cval from portfolio where sid ="%s"' %(stock_to_sell))
                qty_old = qty_result.fetchone()
                if type(qty_old) is NoneType:
                    print "Stock ID not found :(. Please enter a valid Stock ID"
                else:
                    if int(qty_old[0]) == int(qty_sell):
                        d.execute('delete from portfolio where sid="%s"'%(stock_to_sell))
                        conn.commit()
                        c.close()
                        d.close()
                    elif int(qty_sell) < int(qty_old[0]):
                        amntin = float(qty_old[1]) - (int(qty_sell)*float(qty_old[2]))
                        d.execute('update portfolio set qty = %d,amntin=%f where sid = "%s" ' %((int(qty_old[0]) - int(qty_sell)),amntin,stock_to_sell))
                        conn.commit()
                        c.close()
                        d.close()
                    else:
                        print "You only have %d stocks with you"%(qty_old[0])
                conn.close() 
                sell_more = raw_input("Continue selling more(y/n): ")
        except KeyboardInterrupt:
            sys.exit()
        except Exception, e:
            raise e 
    
    #delete : remove your entire portfolio database
    def delete(self):
        try:
            os.stat(self.database)
            del_opt = raw_input("Are you sure?(y/n): ")
            if del_opt == "y":
                os.unlink(self.database)
                print "Deleted your portfolio successfully!"
                sys.exit()
            else:
                pass
        except OSError:
            print "No portfolio exists for you!"        

# Main functions from where the arguments are processed and other subroutines are called    
def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:],"h",["help", "stock=", "market=", "exchange=", "watch", "portfolio="])
        
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
    # defaulting the market = indian and exchange = All and watch = False and action = None
    market = "in"
    exchange = "All"
    watch = False
    action = "None"
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
        elif o == "--portfolio":
            action = a
            manage_portfolio(action)
            sys.exit()
        elif o == "--action":
            action = a
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


def manage_portfolio(action):
    try:
        if action == "show":
            pobj = portfolio("portfolio.db")
            pobj.show()
        elif action == "create":
            pobj = portfolio("portfolio.db")
            pobj.create()
        elif action == "update":
            pobj = portfolio("portfolio.db")
            pobj.update()
            pobj.show()
        elif action == "addstock":
            pobj = portfolio("portfolio.db")
            pobj.addstock()
        elif action == "sellstock":
            pobj = portfolio("portfolio.db")
            pobj.sellstock()
        elif action == "delete":
            pobj = portfolio("portfolio.db")
            pobj.delete()
        else:
            pass
    except Exception, e:
        raise e

# prints and return an array of stock objects.
def get_stocks(stocks_to_search):
    url = "http://finance.yahoo.com/lookup?s="+stocks_to_search+"&t=s&m=in"
    content = urllib2.urlopen(url)
    soup = BeautifulSoup(content)
    stock_array = []
    stocks_table = PrettyTable(["Stock ID","Stock Name","Exchange", "Currrent Value"])
    angular_tag_pattern = "<a href=(.*)>(.*)</a>"
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
            stock_id = re.match(angular_tag_pattern, row_entry[0].renderContents()).group(2)
            stock_name = row_entry[1].renderContents()
            stock_price = float(row_entry[2].renderContents().replace(",",""))
            exchange_type = row_entry[5].renderContents().replace("NSI","NSE")
            stock_obj = ystock(stock_id,stock_name,exchange_type,stock_price)
            stock_array.append(stock_obj)   
    except Exception, e:
        print e
        print "Sorry. Could not find any resutls for: "+stocks_to_search.upper()
    for obj in stock_array:
        stocks_table.add_row([obj.stock_id,obj.stock_name,obj.exchange,obj.current_value])
    print stocks_table
    return stock_array
                

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
    print stocks_table

if __name__ == "__main__":
    main()
