'''
File: DOW_30_Tracker.py
By: Kevin Martinez

Description/Goals:
Data structures & Algorithms project
• Independently built a Python script to collect and analyze stock market data for the top 30 US companies based
on market cap in the United States.
• Visually demonstrated sorting algorithms and key stock data of each company using Matplotlib.
• Web scraped real-time data of stock prices using Urllib.
• Improved latency by 300% using Multithreading from the Threading library to access multiple websites at once
'''

from matplotlib import animation as animation, pyplot as plt 	#visualizer
from urllib.error import HTTPError	
import urllib.request 				 # Urllib package is the URL handling module for python.
import threading # load urls faster	 # It is used to fetch URLs. It uses the urlopen function
									# and is able to fetch URLs using a variety of different
									# protocols. if unable to import Urllib simply install it
									# using "pip install urllib" in your Command prompt 

class sort_artist:
	def __init__(self, arr, y_idx, ptrs, reverse = False):
		self.arr = arr
		self.y_idx = y_idx
		self.ptrs = ptrs
		self.reverse = reverse

	def My_Sort(self):  #Time complexity: O(n * (n-1)) = O(n^2)
		arr = self.arr  #Space complexity: O(1)
		y_idx = self.y_idx  # sort by this input category
		x_idx, x_pls_n_idx = self.ptrs
		reverse = self.reverse
		#print('Starting pointers =', [x_idx, x_pls_n_idx])
		for x_idx in range(x_idx, len(arr)):
			#print(x_idx, x_pls_n_idx)
			if(x_pls_n_idx <= x_idx + 1) or (x_pls_n_idx >= len(arr) - 1):
				n = x_idx + 1
				x_pls_n_idx = n
			for x_pls_n_idx in range(x_pls_n_idx, len(arr)):
				#print(x_idx, x_pls_n_idx)

				# Translate data to word(str) or number(float)
				x_data = sort_artist.data_translation(arr[x_idx][y_idx])
				x_pls_n_data = sort_artist.data_translation(arr[x_pls_n_idx][y_idx])

				# If condition met then swap places
				if ((reverse == False) and (x_data > x_pls_n_data)) or ((reverse == True) and (x_data < x_pls_n_data)):
					arr[x_idx], arr[x_pls_n_idx] = arr[x_pls_n_idx], arr[x_idx]
					#print('Ending pointers =', [x_idx, x_pls_n_idx])
					return arr, [x_idx, x_pls_n_idx]	# 1 step/index swap at a time
		# return arr, [x_idx, x_pls_n_idx]	# Completely sorted


	def data_translation(data):
		if(isinstance(data, float) == True) or (isinstance(data, int) == True):
			data = data

		elif data == '-':	# if data is undefined set data to 0
			data = 0

		elif data[-1] == ')':	# if category is "Today's change"
			temp_perc = ""
			# Find the start and end of the percentage value
			start_idx = data.index('(') + 1
			end_idx = data.index('%')
			# Extract the percentage value from the data string
			temp_perc = data[start_idx:end_idx]
			data = float(temp_perc)

		else: # if data is a string try translating it to float if it is a number or keep as string if it is a word
			Temp_data = ""
			str_count = 0
			# iterate through each character in the string
			for idx in range(len(data)):
				#save float Key data characters
				if (data[idx] == '.') or (data[idx] == '-'):
					Temp_data += data[idx]
				else:
					try: #if str can be converted to float append to Temp_x_float_str
						float(data[idx])
						Temp_data += data[idx]
					except:
						str_count += 1   # detected a non-number/ character

			if(str_count / len(data)) < (0.5):   # if most of the string consists of floats make the string into a number
				Mult = 1    # multiplier
				#mult_dict = {'M': 1_000_000, 'B': 1_000_000_000, 'T': 1_000_000_000_000}
				#mult = mult_dict[data[-1]]
				if(data[-1] == 'M'):    # if float is in million, billion, or trillion recalculate
					Mult = 1_000_000
				elif(data[-1] == 'B'):
					Mult = 1_000_000_000
				elif(data[-1] == 'T'):
					Mult = 1_000_000_000_000
				data = float(Temp_data) * Mult

			else:
				data = str(data)    # Keep data as a word not a number
		return data

class Web_Scrape:
	def sim_score(str_0: str, str_1: str):
		if str_0[0] == str_1[0]:
			total = sim_char = score = 1
			idx = 1
		else:
			return 0

		# find shortest str
		if len(str_0) < len(str_1):
			shortest = len(str_0)
		else:
			shortest = len(str_1)

		# string similarity score algorithm
		while idx < shortest:
			if str_0[idx] == str_1[idx]:
				total += 1
				sim_char += 1
				score = sim_char/total
			else:
				total += 1
				score = sim_char/total
			idx += 1
		return score

	# T: O(n), M: O(n)
	def linear_search(src_code: str, srch_str: str, end_char: str, init_idx: int = 75_000) -> tuple[str, int]:
		data = ""
		for src_idx in range(init_idx, len(src_code)):						# iterate through entire source code, start_idx skips unimportant parts of the source code
			curr_str = src_code[src_idx:src_idx + len(srch_str)]
			#if src_code[src_idx:src_idx + len(srch_str)] == srch_str:			# slicing, compare search_str indexes to source code indexes
			if Web_Scrape.sim_score(curr_str, srch_str) >= .7 and curr_str[-1] == srch_str[-1]:
				src_idx += len(srch_str) 											# if search_str is found in source code copy data from the last recorded source code index + 1 and onward
				while src_code[src_idx] != end_char: 								# search_str is the HTML code right next the data we want
					data += src_code[src_idx]
					src_idx += 1
				data = Web_Scrape.web_translation(data)
				return data, src_idx 	# return scraped data and the last recorded index

	def web_translation(data):
		# Dictionary mapping HTML character codes to their corresponding characters
		translations = {
			"&amp;": 			"&",  	# ampersand
			"&#x27;": 			"'",  	# apostrophe
			"\\xe2\\x80\\x94": 	"-"  	# hyphen
		}
		result = ""
		idx = 0
		while idx < len(data):								# Iterate through data string
			for key, char_value in translations.items():	# Check if the current substring matches any of the keys in the translations dictionary
				if data[idx:idx + len(key)] == key:
					result += char_value
					idx += len(key)
					break
			else:											# no translation dictionary matches, append to result and iterate
				result += data[idx]
				idx += 1
		return result

	def open_url(Thread_num, str_url_list):
		#print("Started Thread_num", Thread_num)
		indiv_stock_source_code = ""
		while(len(indiv_stock_source_code) < 150_000): # Reload url if all the source code is not loaded
			try: 
				Open_Individual_url = urllib.request.urlopen(url_list[Thread_num])
				content = Open_Individual_url.read()
			except HTTPError as e: # Error 500 Could not load website
				content = e.read()
			indiv_stock_source_code = str(content)
		#print(indiv_stock_source_code.decode('utf-8'))
		str_url_list[Thread_num] = indiv_stock_source_code

	def scrape_main(list_len):
		try:
			str_url_list = [None] * list_len
			url_thread = []
			for idx in range(list_len):
				url_thread.append(threading.Thread(target = Web_Scrape.open_url, args=(idx, str_url_list)))
				url_thread[idx].start()
			for idx in range(list_len):
				url_thread[idx].join()

			Skipheader = 75_000
			Categories = {
			"Company name": 			"<h1 class=\"css-15ltlny\">",
			"Current Stock Price": 		"class=\"css-vx2wje\"><span class=\"css-w8p71j\">", 
			#"Today's change": 			"\"secondary_value\":{\"main\":{\"value\":\"",
			"Market cap": 				"Market cap</span><div class=\"css-1slfsms\"></div><span class=\"css-y3z1hq\">",
			"Price-Earnings ratio": 	"Price-Earnings ratio</span><div class=\"css-1slfsms\"></div><span class=\"css-y3z1hq\">",
			"Dividend yield": 			"Dividend yield</span><div class=\"css-1slfsms\"></div><span class=\"css-y3z1hq\">",
			"High today": 				"High today</span><div class=\"css-1slfsms\"></div><span class=\"css-y3z1hq\">",
			"Low today": 				"Low today</span><div class=\"css-1slfsms\"></div><span class=\"css-y3z1hq\">",
			"Open price": 				"Open price</span><div class=\"css-1slfsms\"></div><span class=\"css-y3z1hq\">",
			"Volume": 					"Volume</span><div class=\"css-1slfsms\"></div><span class=\"css-y3z1hq\">",
			"52 wk high": 				"52 Week high</span><div class=\"css-1slfsms\"></div><span class=\"css-y3z1hq\">",
			"52 wk low": 				"52 Week low</span><div class=\"css-1slfsms\"></div><span class=\"css-y3z1hq\">",
			}
			dataset = []
			#print("start for loop:")
			for idx in range(list_len):
				Indiv_stock_data = []
				Indiv_stock_data.append(symb_arr[idx])

				url_str = str_url_list[idx]
				prev_idx = Skipheader	# intialize start_idx
				for key, web_val in Categories.items():
					if(key != "Today's change"):
						data, prev_idx = Web_Scrape.linear_search(init_idx = prev_idx, src_code = url_str, srch_str = web_val, end_char = "<")
						prev_idx = Skipheader
					else:
						data, prev_idx = Web_Scrape.linear_search(init_idx = prev_idx, src_code = url_str, srch_str = web_val, end_char = "\"")
						prev_idx = Skipheader
					Indiv_stock_data.append(data)

				dataset.append(Indiv_stock_data)
		except:
			pass
		return dataset

def animate(frame, dataset, prev_ptrs, in_category):
	New_dataset = dataset
	y_idx = in_category
	if(frame <= 0):
		# initialize ptrs
		ptrs = [0, 0]
	else:
		ptrs = [None, None]
		ptrs[0] = prev_ptrs[0]
		ptrs[1] = prev_ptrs[1]
	try:
		# Sort
		New_dataset, ptrs = sort_artist(New_dataset, in_category, ptrs, reverse = True).My_Sort()
		x_ptr0, x_ptr1 = ptrs
		# update table
		for y in range(len(New_dataset[0])):
			table.get_celld()[x_ptr0 + 1, y].set_text_props(text = New_dataset[x_ptr0][y])
			table.get_celld()[x_ptr1 + 1, y].set_text_props(text = New_dataset[x_ptr1][y])
		# update bar chart
		bars[x_ptr0].set_height(sort_artist.data_translation(New_dataset[x_ptr0][y_idx]))
		bars[x_ptr1].set_height(sort_artist.data_translation(New_dataset[x_ptr1][y_idx]))
		# update xticklabels
		x_ticks = axs[0].get_xticklabels()	# copy previous xticklabel data
		x_ticks[x_ptr0] = New_dataset[x_ptr0][0]	# update shifts
		x_ticks[x_ptr1] = New_dataset[x_ptr1][0]
		axs[0].set_xticklabels(x_ticks)
		# save ptrs outside of function
		prev_ptrs[0] = ptrs[0]
		prev_ptrs[1] = ptrs[1]

	except:
		# restart when done sorting or when error occurs
		prev_ptrs[0] = 0
		prev_ptrs[1] = 0
		New_dataset = Web_Scrape.scrape_main(list_len)
		for idx in range(list_len):
			print(New_dataset[idx])

# Search on the web for the list of companies in the dow-30
Dow_30_list_url = "https://www.cnbc.com/dow-30/"
Dow_30_request_url = urllib.request.urlopen(Dow_30_list_url)
Dow_30_Source_code = str(Dow_30_request_url.read())
list_len = 30
# Scan through source code to find the symbols that represent these companies and scrape that data onto symb_arr
symb_arr = []
prev_i = 100_000
for stock in range(list_len):
	temp_arr, prev_i = Web_Scrape.linear_search(init_idx = prev_i, src_code = Dow_30_Source_code, srch_str = "{\"symbol\":\"", end_char = "\"")
	symb_arr.append(temp_arr)
# Search on the web for more information about these companies by using their symbol
url_list = []
for idx in range(list_len):
	Indivdual_stock_data_url = "https://robinhood.com/stocks/" + symb_arr[idx] + "/"
	url_list.append(Indivdual_stock_data_url)
# Gather all DOW30 data
dataset = Web_Scrape.scrape_main(list_len)
for idx in range(len(dataset)):
	print(dataset[idx])

Array_categories = ['Stock symbol', 'Company name', '1D Stock Price', '1D Percent', 'Market cap', 'Price-Earnings ratio',  'Dividend yield', 'High today', 'Low today', 'Open price', 'Volume', '52 week high',  '52 week low']
#collabel = ('Symb', 'Cmpny', 'Price', 'Change', 'Mkt cap', 'PE ratio',  'Dvd', 'High 1D', 'Low 1D', 'Open $', 'Vol', '52 wk high',  '52 wk low')
collabel = ('Symb', 'Cmpny', 'Price', 'Mkt cap', 'PE ratio',  'Dvd', 'High 1D', 'Low 1D', 'Open $', 'Vol', '52 wk high',  '52 wk low')
rowlabel = [i for i in range(1, 31)] 
in_category = 6 	#default category is in idx 2 which is stock price
#Selected_Vector = dataset[in_category]
Sort_by = Array_categories[in_category]

key_data_list = []
for x_idx in range(len(dataset)):
	key_data_list.append(sort_artist.data_translation(dataset[x_idx][in_category]))

default_x_list = []

for idx in range (len(dataset)):
	default_x_list.append(dataset[idx][0])

fig, axs = plt.subplots(2, 1)
bars = axs[0].bar(default_x_list, key_data_list, facecolor ='Black')
axs[1].axis('tight')
axs[1].axis('off')
table = axs[1].table(cellText = dataset,
					rowLabels = rowlabel,
					#rowColours=colors,
					colLabels = collabel,
					loc = 'center',
					fontsize = 8,
					bbox = [0.0, 0.0, 1, 1])

# Computer 16:9 1080p
plt.subplots_adjust(left = .025, right = .98, bottom = .02, top = .98, hspace = .1)
# Laptop 16:10 4K
#plt.subplots_adjust(left = .025, right = .49, bottom = .51, top = .98, hspace = .1)
#table.subplots_adjust(bottom = .2)
prev_ptrs = [None, None]
ani = animation.FuncAnimation(fig, animate, interval = 1, fargs = (dataset, prev_ptrs, in_category))
plt.get_current_fig_manager().window.state('zoomed')
plt.show()