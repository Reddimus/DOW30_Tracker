'''
File:   DOW30_Tracker.py
By:     Kevin Martinez

Description/Goals:
Data structures & Algorithms project
- Grab new list of the DOW 30 companies
    - Overwrite less dynamic values in the database once
    - Overwrite more dynamic values in the database once then continiously every minute
    - Mulitthread getting new values for the database
- Have DOW_30_database.csv file as backup if wikipedia could not read the DOW 30 list
- Animate sorted bar graph of the DOW 30 companies `y` axis
    - `x` axis is the company ticker
    - `y` axis is category chosen
    - Sort by category chosen
    - Update every minute if within trading hours (9:30am - 4:00pm EST) and Monday - Friday
- Visualize brute force/bubble sort of the DOW 30 companies
'''

import yfinance
import pandas
import csv
import threading
import matplotlib
import matplotlib.animation
import matplotlib.pyplot
import matplotlib.ticker
import datetime
import pytz
import time

# Add this line to see all columns when printing a DataFrame
pandas.set_option('display.max_columns', None)

# Check to see if the DOW 30 list has changed
url = 'https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average'
tables = pandas.read_html(url)
dow30_table = tables[1] # This index might change depending on the structure of the Wikipedia page
dow30_table = dow30_table.drop(columns=['Date added', 'Notes']) # Removing unnecessary columns
# sort by Symbol column
dow30_table = dow30_table.sort_values(by=['Symbol'])

# Getting the company name, tickers, and index weights of the DOW 30 only once
dow30_companies = dow30_table['Company'].tolist()
dow30_tickers = dow30_table['Symbol'].tolist()
# idx_weights convert percent string to float
dow30_table['Index weighting'] = round(dow30_table['Index weighting'].str.rstrip('%').astype('float'), 4)
dow30_idx_weights = dow30_table['Index weighting'].tolist()

db_df = pandas.read_csv('DOW30_database.csv')

if len(dow30_tickers) == 30:
    db_df['Company'] = dow30_companies
    db_df['Symbol'] = dow30_tickers
    db_df['Index Weight'] = dow30_idx_weights
else:
    print('Error: DOW 30 list was not generated correctly')

del dow30_companies, dow30_tickers, dow30_idx_weights, dow30_table, tables, url

def get_stk_info(ticker: str, idx: int) -> None:
    stk = yfinance.Ticker(ticker)
    db_df.at[idx, 'Dividend Yield'] = round(stk.info.get('dividendYield', 0) * 100, 2)
    db_df.at[idx, 'Market Cap'] = stk.info.get('marketCap', 0)
    db_df.at[idx, '52 Week Change'] = round(stk.info.get('52WeekChange', 0) * 100, 2)

# update other less dynamic values in the database once (i.e. dividend yield, Market cap, etc.) using multithreading
stk_threads = []
for idx, row in db_df.iterrows():
    stk_thread = threading.Thread(target=get_stk_info, args=(row['Symbol'], idx))
    stk_threads.append(stk_thread)
    stk_thread.start()
# join threads and Write the updated DataFrame back to the CSV file
[stk_thread.join() for stk_thread in stk_threads]
db_df.to_csv('DOW30_database.csv', index=False)

# get the stock price and 1D % Growth of the DOW 30 companies
def get_stk_price(ticker: str, idx: int) -> None:
    stk = yfinance.Ticker(ticker)
    db_df.at[idx, 'Stock Price'] = round(stk.history(period="1d")['Close'][0], 2)
    db_df.at[idx, '1D % Growth'] = round(stk.history(period="2d")['Close'].pct_change().iloc[-1] * 100, 2)

# mulitthread getting new values for the database
def get_stk_prices() -> None:
    stk_threads = []
    for idx, row in db_df.iterrows():
        stk_thread = threading.Thread(target=get_stk_price, args=(row['Symbol'], idx))
        stk_threads.append(stk_thread)
        stk_thread.start()
    # join threads
    [stk_thread.join() for stk_thread in stk_threads]

# Initialize the stock price and 1D % Growth columns
get_stk_prices()
# Write the updated DataFrame back to the CSV file
db_df.to_csv('DOW30_database.csv', index=False)

class sort_artist:
    def __init__(self, df: pandas.DataFrame, sort_by: str, reverse: bool = False) -> None:
        self.df = df
        self.sort_by = sort_by
        self.reverse = reverse
        self.l_idx = 0
        self.r_idx = 0
        self.sorted = False
    
    def get_ptrs(self) -> tuple:
        return (self.l_idx, self.r_idx)

    # Bubble Sort 1 pair at a time to visualize the sorting process
    # T: O(r^2) M: O(1), where r is row length of the DataFrame
    def brute_sort(self) -> None:
        for l_idx in range(self.l_idx, len(self.df) - 1):
            for r_idx in range(self.l_idx + 1, len(self.df)):
                if l_idx < r_idx and self.df.at[l_idx, self.sort_by] > self.df.at[r_idx, self.sort_by] and not self.reverse:
                    #print("l_ele (", self.df.at[l_idx, 'Symbol'], ") = df.at[", l_idx, ", ", self.sort_by, "] = ", self.df.at[l_idx, self.sort_by], " >  r_ele (", self.df.at[r_idx, 'Symbol'], ") = df.at[", r_idx, ", ", self.sort_by, "] = ", self.df.at[r_idx, self.sort_by])
                    # swap rows
                    self.df.loc[l_idx], self.df.loc[r_idx] = self.df.loc[r_idx], self.df.loc[l_idx]
                    self.l_idx, self.r_idx = l_idx, r_idx
                    # print(l_idx, r_idx)
                    # print()
                    return
                elif l_idx < r_idx and self.df.at[l_idx, self.sort_by] < self.df.at[r_idx, self.sort_by] and self.reverse:
                    print("reverse")
                    self.df.loc[l_idx], self.df.loc[r_idx] = self.df.loc[r_idx], self.df.loc[l_idx]
                    self.l_idx, self.r_idx = l_idx, r_idx
                    # print(l_idx, r_idx)
                    # print()
                    return
        # if no swaps were made, then the list is sorted
        print("sorted")
        self.set_Sorted(True)
        return
    
    def is_Sorted(self) -> bool:
        return self.sorted

    def set_Sorted(self, sorted: bool, l_idx: int = 0, r_idx: int = 0) -> None:
        self.sorted = sorted
        self.l_idx, self.r_idx = 0, 0

artist_data = sort_artist(db_df, 'Stock Price')

# Print the updated database to bar graph from matplotlib
x_axis, y_axis = 'Symbol', 'Stock Price'
fig, ax = matplotlib.pyplot.subplots()
bars = ax.bar(artist_data.df[x_axis], artist_data.df[y_axis], color='black', edgecolor='blue')
matplotlib.pyplot.title('DOW 30 Companies Sorted by' + y_axis)
ax.xaxis.set_major_locator(matplotlib.ticker.FixedLocator(range(len(artist_data.df))))
start_time = time.time()
eastern = pytz.timezone('US/Eastern')
now = datetime.datetime.now(eastern)

# Animate the sorted bar graph of the DOW 30 companies `y` axis
def animate(frame):
    global start_time
    elapsed_time = int(time.time() - start_time)
    # if within trading hours (9:30am - 4:00pm EST) and Monday - Friday
    if elapsed_time >= 60 and artist_data.is_Sorted() and now.weekday() < 5 and (9 <= now.hour <= 16):
        print("Updating database...")
        start_time = time.time()
        get_stk_prices()    # update every minute
        artist_data.set_Sorted(False)
        # print dataframe with only symbol and stock price columns
        print(artist_data.df[['Symbol', 'Stock Price']])
    elif artist_data.is_Sorted() == False:
        l, r = artist_data.get_ptrs()
        bars[l].set_color('black')
        bars[r].set_color('black')
        artist_data.brute_sort()
        # check again after sorting
        if artist_data.is_Sorted() == False:
            # grab swapped values, and only update swapped values on the bar graph
            l, r = artist_data.get_ptrs()
            bars[l].set_height(artist_data.df.at[l, 'Stock Price'])
            bars[r].set_height(artist_data.df.at[r, 'Stock Price'])
            bars[l].set_color('red')
            bars[r].set_color('red')
            x_ticks = ax.get_xticklabels()
            x_ticks[l].set_text(artist_data.df.at[l, 'Symbol'])
            x_ticks[r].set_text(artist_data.df.at[r, 'Symbol'])
            ax.set_xticklabels(x_ticks)

ani = matplotlib.animation.FuncAnimation(fig, animate, interval=100, cache_frame_data=False)
matplotlib.pyplot.tight_layout()
matplotlib.pyplot.get_current_fig_manager().window.state('zoomed')
matplotlib.pyplot.show()
