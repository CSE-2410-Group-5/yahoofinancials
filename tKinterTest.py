from datetime import datetime, timedelta
import tkinter as tk
import tkinter.scrolledtext as scrolledtext
import sys
import time
import pytz
import yfinance
import yfinance as yf
from yahoofinancials import YahooFinancials as YF, yf
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

DEFAULT_ARGS = ()
MODULE_ARGS = ('yf', 'yahoofinancial', 'yahoofinancials')
HELP_ARGS = ('-h', '--help')
OUTPUT = ''
tick = None


def default_api(ticker):
    global OUTPUT
    global tick

    # Stores ticker so info can be grabbed
    tick = YF(ticker)

    # Adds all the basic ticker info to output string
    OUTPUT += '{:25s}{:,f}\n'.format('Current Price: ', tick.get_current_price())
    OUTPUT += '{:22s}{:,f}\n'.format('Current Volume: ', tick.get_current_volume())
    OUTPUT += '{:23s}{:,f}\n'.format('Prev Close Price: ', tick.get_prev_close_price())
    OUTPUT += '{:26s}{:,f}\n'.format('Open Price: ', tick.get_open_price())
    OUTPUT += '{:26s}{:,f}\n'.format('Daily Low: ', tick.get_daily_low())
    OUTPUT += '{:27s}{:,f}\n'.format('Daily High: ', tick.get_daily_high())

    try:
        r = tick._cache.keys()
    except AttributeError:
        pass


def custom_api(queries, ts):
    global OUTPUT
    yf = YF(ts[0] if 1 == len(ts) else ts)
    for q in queries:
        OUTPUT += ('%s:' % (q,)) + '\n'
        timeit(lambda: print(getattr(yf, q)()))


def help_api(queries):
    global OUTPUT
    if len(queries) == 1:
        print(__doc__ % {'scriptname': sys.argv[0], 'defaultargs': ', '.join(DEFAULT_ARGS)})
    else:
        import pydoc
        for q in queries:
            if q in MODULE_ARGS:
                OUTPUT += (pydoc.render_doc(YF, "Help on %s")) + '\n'
            elif q not in HELP_ARGS:
                OUTPUT += (pydoc.render_doc(getattr(YF, q), "Help on %s")) + '\n'


def timeit(f, *args):
    global OUTPUT
    st = time.time()
    f(*args)
    et = time.time()


def setup():
    global OUTPUT

    api = set(s for s in dir(YF) if s.startswith('get_'))
    api.update(MODULE_ARGS)
    api.update(HELP_ARGS)
    ts = sys.argv[1:]
    queries = [q for q in ts if q in api]
    ts = [t for t in ts if not t in queries] or DEFAULT_ARGS
    if [h for h in HELP_ARGS if h in queries]:
        help_api(queries)
    elif queries:
        custom_api(queries, ts)
    else:
        timeit(default_api, ts[0] if 1 == len(ts) else ts)

    # Creates textbox for basic ticker information
    text = tk.Text(root, wrap='word', font=('Times', 18))
    text.insert('insert', OUTPUT)
    text.place(x=1, y=46, width=710, height=300)
    root.update()
    OUTPUT = ''


# Takes ticker entered by user and sets it up if valid
def create_ticker():
    global DEFAULT_ARGS
    DEFAULT_ARGS = (first_entry.get())

    if is_valid_ticker(DEFAULT_ARGS):
        setup()
    else:
        # Cryptos need a specific currency in order to grab info
        DEFAULT_ARGS += '-' + clicked.get()
        if is_valid_ticker(DEFAULT_ARGS):
            setup()
        else:
            tk.messagebox.showinfo('Invalid Ticker', 'The option you entered is not a valid ticker. Please try again.')


def display_stock_graph():
    try:
        # makes the ticker object
        ticker_data = yfinance.Ticker(DEFAULT_ARGS)

        # creates the boundary to extract data from
        current_day = datetime.now().strftime('%Y-%m-%d')
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        current_day_data = ticker_data.history(start=current_day, end=tomorrow, interval='1m')

        current_time = datetime.today().strftime('%H:%M:%S')

        open_time = '9:30:00'
        close_time = '16:00:00'

        # Checks if a ticker is a cryptocurrency
        time_interval = '15T'
        info = ticker_data.info
        quote_type = info.get('quoteType')

        if quote_type == 'CRYPTOCURRENCY':
            time_interval = '1H'
            open_time = '0:01:00'
            close_time = '23:59:00'
        hours_data_20 = current_day_data.between_time(open_time, close_time).resample(time_interval).last()

        # convert to Eastern Time
        hours_data_20.index = hours_data_20.index.tz_convert('US/Eastern')
        eastern_time = pytz.timezone('US/Eastern')
        hours_data_20.index = hours_data_20.index.tz_convert(eastern_time)

        # Create empty lists to store the time and price
        stock_times = []
        stock_prices = []

        # puts the items in their own list
        for hour, price in zip(hours_data_20.index, hours_data_20['Close']):
            time = hour.strftime('%I:%M %p')
            stock_times.append(time)
            stock_prices.append(price)

        # Create a figure and add a subplot
        fig = Figure(figsize=(16, 3.95), dpi=100)
        _graph = fig.add_subplot(111)

        _graph.tick_params(axis='x', labelsize=6)
        # plots graph and checks if the stock has gained value or lost
        graph_color = 'green'
        if stock_prices[0] > stock_prices[len(stock_prices) - 1]:
            graph_color = 'red'
        _graph.plot(stock_times, stock_prices, color=graph_color)

        # gets the current day
        fin_current_day = datetime.now().strftime('(%m-%d)')

        # Labels the graph
        _title = DEFAULT_ARGS.upper() + "'s Daily Prices " + fin_current_day
        _graph.set_title(_title)
        _graph.set_xlabel("Time(AM-PM)")
        _graph.set_ylabel("Stock Price($)")

        # Create a canvas to display the graph in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().place(x=0, y=390)

    except TypeError as e:
        if str(e) == "Index must be DatetimeIndex":
            mess = tk.Label(root, text="Stock market is closed, try again later", font=('Times', 26))
            mess.place(x=500, y=500)


def is_valid_ticker(symbol):
    try:
        ticker = yfinance.Ticker(symbol)
        info = ticker.info['regularMarketPrice']
        return True
    except:
        return False


# Function to toggle the visibility of the listbox when the entry widget is clicked
def toggle_dropdown(event):
    global dropdown_visible
    if dropdown_visible:
        listbox.pack_forget()
        dropdown_visible = False
    else:
        listbox.pack()
        dropdown_visible = True


# Function to update the selected options when the user makes a selection
def update_selection():
    global selected_options, dropdown_visible
    selected_options = [listbox.get(idx) for idx in listbox.curselection()]
    dropdown_entry_var.set(", ".join(selected_options))
    dropdown_visible = False
    listbox.pack_forget()

    # Checks which choices have been chosen in the
    # additional information drop down menu and
    # returns the string to be printed to the screen
    # Loops through chosen information
    # Checks for each option in dropdown, calls appropriate
    # methods and adds appropriate text for each selection
    text = ''
    for selected in selected_options:
        if selected == '5 Year Avg. Div. Yield':
            temp = tick.get_five_yr_avg_div_yield()
            if temp is None:
                temp = '--'
            text += '5 Year Average Dividend Yield: {}\n'.format(temp) + (' ' * 58)

        if selected == '10-day Current Volume':
            temp = '{:,}'.format(tick.get_ten_day_avg_daily_volume())
            if temp is None:
                temp = '--'
            text += '10-day Current Volume: {}\n'.format(temp) + (' ' * 58)

        elif selected == '50 Day Moving Avg.':
            temp = '{:,}'.format(tick.get_50day_moving_avg())
            if temp is None:
                temp = '--'
            text += '50 Day Moving Average: {}\n'.format(temp) + (' ' * 58)

        elif selected == '200 Day Moving Avg.':
            temp = '{:,}'.format(tick.get_200day_moving_avg())
            if temp is None:
                temp = '--'
            text += '200 Day Moving Average: {}\n'.format(temp) + (' ' * 58)

        elif selected == 'Annual Avg. Div. Rate':
            temp = tick.get_annual_avg_div_rate()
            if temp is None:
                temp = '--'
            text += 'Annual Average Dividend Rate: {}\n'.format(temp) + (' ' * 58)

        elif selected == 'Annual Avg. Div. Yield':
            temp = tick.get_annual_avg_div_yield()
            if temp is None:
                temp = '--'
            text += 'Annual Average Dividend Yield: {}\n'.format(temp) + (' ' * 58)

        elif selected == 'Beta':
            temp = tick.get_beta()
            if temp is None:
                temp = '--'
            text += 'Beta: {}\n'.format(temp) + (' ' * 58)

        elif selected == 'Dividend Rate':
            temp = tick.get_dividend_rate()
            if temp is None:
                temp = '--'
            text += 'Dividend Rate: {}\n'.format(temp) + (' ' * 58)

        elif selected == 'Dividend Yield':
            temp = tick.get_dividend_yield()
            if temp is None:
                temp = '--'
            text += 'Dividend Yield: {}\n'.format(temp) + (' ' * 58)

        elif selected == 'Earnings Per Share':
            temp = tick.get_earnings_per_share()
            if temp is None:
                temp = '--'
            text += 'Earnings Per Share: {}\n'.format(temp) + (' ' * 58)

        elif selected == 'Ex-Dividend Date':
            temp = tick.get_exdividend_date()
            if temp is None:
                temp = '--'
            text += 'Ex-Dividend Date: {}\n'.format(temp) + (' ' * 58)

        elif selected == 'Market Cap':
            temp = '{:,}'.format(tick.get_market_cap())
            if temp is None:
                temp = '--'
            text += 'Market Cap: {}\n'.format(temp) + (' ' * 58)

        elif selected == 'Payout Ratio':
            temp = tick.get_payout_ratio()
            if temp is None:
                temp = '--'
            text += 'Payout ratio: {}\n'.format(temp) + (' ' * 58)

        elif selected == 'Price To Sales Trail 1 Yr':
            temp = tick.get_price_to_sales()
            if temp is None:
                temp = '--'
            text += 'Price To Sales Trailing 1 Year: {}\n'.format(temp) + (' ' * 58)

        elif selected == 'Shares Outstanding':
            temp = '{:,}'.format(tick.get_num_shares_outstanding())
            if temp is None:
                temp = '--'
            text += 'Shares Outstanding: {}\n'.format(temp) + (' ' * 58)

        elif selected == 'Trailing PE':
            temp = '{:,}'.format(tick.get_pe_ratio())
            if temp is None:
                temp = '--'
            text += 'Trailing Price-To-Earnings: {}\n'.format(temp) + (' ' * 58)

        elif selected == 'Yearly High':
            temp = '{:,}'.format(tick.get_yearly_high())
            if temp is None:
                temp = '--'
            text += 'Yearly High: {}\n'.format(temp) + (' ' * 58)

        elif selected == 'Yearly Low':
            temp = '{:,}'.format(tick.get_yearly_low())
            if temp is None:
                temp = '--'
            text += 'Yearly Low: {}\n'.format(temp) + (' ' * 58)


    text2 = scrolledtext.ScrolledText(root, wrap='word', font=('Times', 18))
    text2.insert('insert', text)
    # y was 46
    text2.place(x=720, y=46, width=380, height=300)
    root.update()


# Holds data for drop down menus
currency_options = [
    'USD', 'AUD', 'EUR', 'ALL', 'AOA',
    'AMD', 'AUD', 'BEF', 'AZN', 'BBD',
    'BOB', 'BAM', 'BND', 'CAD', 'CVE',
    'CNY', 'COP', 'KMF', 'CRC', 'EGP',
    'SVC', 'ETB', 'EUR', 'GEL', 'GHS',
    'HKD', 'INR', 'IDR', 'LVL', 'LTL',
    'MGA', 'MRO', 'MUR', 'NAD', 'NIO',
    'NOK', 'PAB', 'PEN', 'PTE', 'WST',
    'SAR', 'SKK', 'SOS', 'ESP', 'SDG',
    'TOP', 'TTD', 'AED'
]

additional_info = [
    "5 Year Avg. Div. Yield",
    "10-day Current Volume",
    "50 Day Moving Avg.",
    "200 Day Moving Avg.",
    "Annual Avg. Div. Rate",
    "Annual Avg. Div. Yield",
    "Beta",
    "Dividend Rate",
    "Dividend Yield",
    "Earnings Per Share",
    "Ex-Dividend Date",
    "Market Cap",
    "Payout Ratio",
    "Price To Sales Trail 1 Yr",
    "Shares Outstanding",
    "Trailing PE",
    "Yearly High",
    "Yearly Low"
]

# BEGIN TKINTER BUILD

root = tk.Tk()
root.title("test")
root.geometry("2000x900")

first_label = tk.Label(root, text='Enter ticker here: ', font=('Times', 26))
first_label.place(x=0, y=0)

first_entry = tk.Entry(root, font=('Times', 26))
first_entry.place(x=250, y=0)

# Create Dropdown menu for currency type
clicked = tk.StringVar()  # datatype of menu text
clicked.set(currency_options[0])  # initial menu text
currency_drop = tk.OptionMenu(root, clicked, *currency_options)
currency_drop.config(height=2, width=6)
currency_drop.place(x=585, y=0)

search_bar_go_button = tk.Button(root, text='GO', command=lambda: create_ticker(), height=2, width=5)
search_bar_go_button.place(x=665, y=3)

# Additional information text
stock_data_label = tk.Label(root, text='Additional Information: ', font=('Times', 26))
stock_data_label.place(x=720, y=0)

# Additional Information Dropdown menu
# Create a frame to hold the dropdown widget
dropdown_frame = tk.Frame(root)
dropdown_frame.place(x=1058, y=0)
# Create an entry widget to display the selected options
dropdown_entry_var = tk.StringVar()
dropdown_entry_var.set("Select options...")
dropdown_entry = tk.Entry(dropdown_frame, textvariable=dropdown_entry_var, width=19, font=('Times', 26))
dropdown_entry.pack()
# Create a listbox widget to display the options when the dropdown is opened
dropdown_visible = False
listbox = tk.Listbox(dropdown_frame, selectmode=tk.MULTIPLE, font=('Times', 18))
for option in additional_info:
    listbox.insert(tk.END, option)
# Create a Scrollbar for the Listbox
listbox_scrollbar = tk.Scrollbar(dropdown_frame, orient=tk.VERTICAL, command=listbox.yview)
# Configure the Listbox to use the Scrollbar
listbox.configure(yscrollcommand=listbox_scrollbar.set)
listbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
listbox.pack_forget()
# Bind events to the entry and listbox widgets to handle the dropdown behavior
dropdown_entry.bind("<Button-1>", toggle_dropdown)
listbox.bind("<FocusOut>", lambda event: dropdown_entry.focus())
listbox.bind("<Button-1>", lambda event: dropdown_entry.focus())
listbox.bind("<ButtonRelease-1>", lambda event: update_selection)

add_info_go_button = tk.Button(root, text='GO', command=update_selection, height=2, width=5)
add_info_go_button.place(x='1404', y=3)

quit_button = tk.Button(root, text='Quit', command=root.quit, height=2, width=5)
quit_button.place(x=1480, y=0)

# Graph button
graph_button = tk.Button(root, text='Graph', command=lambda: display_stock_graph(), height=2, width=5)
graph_button.place(x=1, y=348)

root.mainloop()
