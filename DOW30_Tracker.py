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
    - Sort by category chosen using buttons
    - Update every minute if within trading hours (9:30am - 4:00pm EST) and Monday - Friday
- Visualize brute force/bubble sort of the DOW 30 companies
'''

import pandas as pd
import requests
import matplotlib
import matplotlib.pyplot
import matplotlib.ticker
import matplotlib.animation
import matplotlib.widgets
import datetime
import pytz
import time
import yfinance
import threading

class Dow30Data:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.df = pd.read_csv(db_path)
        self.dow30_companies = []
        self.dow30_tickers = []
        self.dow30_idx_weights = []

    def fetch_from_wikipedia(self) -> None:
        # Implementation to fetch from Wikipedia
        url = 'https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average'
        tables = pd.read_html(url)
        dow30_table = tables[1] # This index might change depending on the structure of the Wikipedia page
        dow30_table = dow30_table.drop(columns=['Date added', 'Notes']) # Removing unnecessary columns
        # sort by Symbol column
        dow30_table = dow30_table.sort_values(by=['Symbol'])
        self.dow30_companies = dow30_table['Company'].tolist()
        self.dow30_tickers = dow30_table['Symbol'].tolist()
        # idx_weights convert percent string to float
        dow30_table['Index weighting'] = round(dow30_table['Index weighting'].str.rstrip('%').astype('float'), 4)
        self.dow30_idx_weights = dow30_table['Index weighting'].tolist()

    def update_database(self) -> None:
        # Implementation to update the database
        if len(self.dow30_tickers) == 30:
            self.df['Company'] = self.dow30_companies
            self.df['Symbol'] = self.dow30_tickers
            self.df['Index Weight'] = self.dow30_idx_weights
        else:
            print('Error: DOW 30 list was not generated correctly')

    def get_data(self) -> pd.DataFrame:
        return self.df

    def get_stock_info(self, ticker: str, idx: int) -> None:
        # logic to get stock info like dividend yield, market cap, etc.
        stk_info = yfinance.Ticker(ticker).info
        self.df.at[idx, 'Dividend Yield'] = round(stk_info.get('dividendYield', 0) * 100, 2)
        self.df.at[idx, 'Market Cap'] = stk_info.get('marketCap', 0)
        self.df.at[idx, '52 Week Change'] = round(stk_info.get('52WeekChange', 0) * 100, 2)

    def update_stock_info(self) -> None:
        # logic to update stock info using multithreading.
        stk_threads = []
        for idx, row in self.df.iterrows():
            stk_thread = threading.Thread(target=self.get_stock_info, args=(row['Symbol'], idx))
            stk_threads.append(stk_thread)
            stk_thread.start()
        # join threads and Write the updated DataFrame back to the CSV file
        [stk_thread.join() for stk_thread in stk_threads]
        self.df.to_csv('DOW30_database.csv', index=False)

    def get_stock_price(self, ticker: str, idx: int) -> None:
        # logic to get stock price and 1D % Growth.
        stk_hist = yfinance.Ticker(ticker).history(period="2d")['Close']
        self.df.at[idx, 'Stock Price'] = round(stk_hist.iloc[-1], 2)
        self.df.at[idx, '1D % Growth'] = round(stk_hist.iloc[-1] / stk_hist.iloc[-2] * 100 - 100, 2)

    def update_stock_prices(self) -> None:
        # logic to update stock prices using multithreading.
        stk_threads = []
        for idx, row in self.df.iterrows():
            stk_thread = threading.Thread(target=self.get_stock_price, args=(row['Symbol'], idx))
            stk_threads.append(stk_thread)
            stk_thread.start()
        # join threads
        [stk_thread.join() for stk_thread in stk_threads]

class Visualization:
    def __init__(self, dow_data: Dow30Data, sort_by: str, reverse: bool = False) -> None:
        self.data = dow_data.get_data()
        self.dow_data = dow_data
        self.sort_by = sort_by
        self.reverse = reverse
        self.fig, self.ax = matplotlib.pyplot.subplots(figsize=(16, 9))
        self.bars = None
        self.sorted = False
        self.l_ptr = 0
        self.r_ptr = 0
        self.start_time = time.time()
        self.eastern = pytz.timezone('US/Eastern')
        self.now = datetime.datetime.now(self.eastern)
        self.ani = None
        self.bttns_list = []    # Store all button objects here to prevent garbage collection

    # Methods related to sorting
    def get_ptrs(self) -> tuple:
        return (self.l_ptr, self.r_ptr)

    def brute_sort(self) -> None:
        # Implementing the bubble sort logic
        # T: O(n^2) S: O(1), where n is the number of elements in the list
        for l_idx in range(self.l_ptr, len(self.data) - 1):
            for r_idx in range(self.l_ptr + 1, len(self.data)):
                if l_idx < r_idx and self.data.at[l_idx, self.sort_by] > self.data.at[r_idx, self.sort_by] and not self.reverse:
                    self.data.loc[l_idx], self.data.loc[r_idx] = self.data.loc[r_idx], self.data.loc[l_idx]
                    self.l_ptr, self.r_ptr = l_idx, r_idx
                    return
                elif l_idx < r_idx and self.data.at[l_idx, self.sort_by] < self.data.at[r_idx, self.sort_by] and self.reverse:
                    self.data.loc[l_idx], self.data.loc[r_idx] = self.data.loc[r_idx], self.data.loc[l_idx]
                    self.l_ptr, self.r_ptr = l_idx, r_idx
                    return
        # if no swaps were made, then the list is sorted
        self.set_sorted(sorted_status=True, l_ptr=0, r_ptr=0)

    def is_sorted(self) -> bool:
        return self.sorted

    def set_sorted(self, sorted_status, l_ptr: int = 0, r_ptr: int = 0) -> None:
        self.sorted = sorted_status
        self.l_ptr, self.r_ptr = l_ptr, r_ptr

    # Methods related to visualization
    def animate(self, frame: int) -> None:
        elapsed_time = int(time.time() - self.start_time)
        # if within trading hours (9:30am - 4:00pm EST) and Monday - Friday
        if elapsed_time >= 60 and self.is_sorted() and self.now.weekday() < 5 and (9 <= self.now.hour <= 16):
            print("Updating database...")
            self.start_time = time.time()
            self.dow_data.update_stock_prices()    # update every minute
            self.update_all_bars()
            # print dataframe with only symbol and category selected
            print(self.data[['Symbol', self.sort_by]])
        elif not self.is_sorted():
            l, r = self.get_ptrs()
            self.bars[l].set_color('black')
            self.bars[r].set_color('black')
            self.brute_sort()
            if not self.is_sorted():
                l, r = self.get_ptrs()
                self.bars[l].set_height(self.data.at[l, self.sort_by])
                self.bars[r].set_height(self.data.at[r, self.sort_by])
                self.bars[l].set_color('red')
                self.bars[r].set_color('red')
                x_ticks = self.ax.get_xticklabels()
                x_ticks[l].set_text(self.data.at[l, 'Symbol'])
                x_ticks[r].set_text(self.data.at[r, 'Symbol'])
                self.ax.set_xticklabels(x_ticks)

    def update_all_bars(self) -> None:
        bottom_lim = 0
        min_cat_val = min(self.data[self.sort_by])
        if min_cat_val < 0:
            bottom_lim = -(abs(min_cat_val) * 1.1)
        self.ax.set_ylim(bottom_lim, max(self.data[self.sort_by]) * 1.1)
        for stk in range(len(self.data)):
            if self.bars[stk].get_facecolor() != 'black':
                self.bars[stk].set_color('black')
            self.bars[stk].set_height(self.data.at[stk, self.sort_by])
        self.ax.set_xticklabels(self.data['Symbol'])
        self.set_sorted(sorted_status=False, l_ptr=0, r_ptr=0)

    def bttn_cat_callback(self, event: matplotlib.backend_bases.MouseEvent) -> None:
        # get button's name
        bttn_name = event.inaxes.button_name
        # if button is already selected, then reverse the sort
        if bttn_name == self.sort_by:
            self.reverse = not self.reverse
        # else sort by the button's category
        else:
            self.sort_by = bttn_name
        # update title
        self.ax.set_title('DOW 30 Companies Sorted by ' + self.sort_by + '     Date: ' + self.now.strftime("%m/%d/%Y"))
        # Update new category data w/ xtick labels to bar graph all at once/ins5tantly
        self.update_all_bars()
        
    def category_button(self, x_pos: int, button_name: str = 'Dummy Button') -> None:
        # Define the button's location an dsize
        bttn_axs = matplotlib.pyplot.axes([x_pos, 0.04, 0.1, 0.04])  # x, y, width, height
        bttn_axs.button_name = button_name
        bttn = matplotlib.widgets.Button(ax=bttn_axs, label=button_name)
        bttn.on_clicked(self.bttn_cat_callback)
        self.bttns_list.append(bttn)    # append buttons to list to prevent garbage collection

    def init_buttons(self) -> None:
        # Logic to initialize all category buttons
        categories = [col for col in self.data.columns if col not in ['Symbol', 'Company']]
        equal_dist = (0.1 + 0.8) / len(categories)
        [self.category_button(0.1 + (idx * equal_dist), cat) for idx, cat in enumerate(categories)]

    def display(self, fullscreen: bool = False) -> None:
        # Logic to display the plot
        if fullscreen:
            # windowed fullscreen
            matplotlib.pyplot.get_current_fig_manager().window.state('zoomed')
        #matplotlib.pyplot.ion()  # Turn on interactive mode
        self.ani = matplotlib.animation.FuncAnimation(self.fig, self.animate, interval=75, cache_frame_data=True, frames=841, blit=False)
        self.init_buttons()
        matplotlib.pyplot.show()

    def record(self, filename: str = "DOW30_Tracker.gif", fps: int = 60, aspect_ratio: tuple = (16, 9)) -> None:
        self.fig.set_size_inches(aspect_ratio[0], aspect_ratio[1])
        # make 16:9 aspect ratio
        self.ani = matplotlib.animation.FuncAnimation(self.fig, self.animate, interval=75, cache_frame_data=True, frames=841)
        # saving the animation as a gif
        self.ani.save(filename, writer=matplotlib.animation.PillowWriter(fps=fps))

    def init_bar_graph(self) -> None:
        # Logic to create bars for the visualization
        self.bars = self.ax.bar(self.data['Symbol'], self.data[self.sort_by], color='black', edgecolor='blue')
        matplotlib.pyplot.ylim(0, max(self.data[self.sort_by]) * 1.1)
        matplotlib.pyplot.title('DOW 30 Companies Sorted by ' + self.sort_by + '     Date: ' + self.now.strftime("%m/%d/%Y"))
        self.ax.xaxis.set_major_locator(matplotlib.ticker.FixedLocator(range(len(self.data))))
        matplotlib.pyplot.tight_layout(rect=[0, 0.1, 1, 1])

# Main Execution Flow
if __name__ == "__main__":
    dow_data = Dow30Data("DOW30_database.csv")
    dow_data.fetch_from_wikipedia()
    dow_data.update_database()
    dow_data.update_stock_info()
    dow_data.update_stock_prices()
    dow_data.df.to_csv('DOW30_database.csv', index=False)

    viz = Visualization(dow_data, 'Stock Price')
    viz.init_bar_graph()
    #viz.record(filename="DOW30_Tracker.gif")
    viz.display(fullscreen=True)