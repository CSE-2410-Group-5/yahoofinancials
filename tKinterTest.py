import tkinter as tk
import sys
import time
from yahoofinancials import YahooFinancials as YF
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import yfinance as yf
from datetime import datetime, timedelta

DEFAULT_ARGS = ('DOGE-JPY')
MODULE_ARGS = ('yf', 'yahoofinancial', 'yahoofinancials')
HELP_ARGS = ('-h', '--help')
OUTPUT = ''
mark = '-' * 64

tick = None

def default_api(ticker):
    global OUTPUT
    global tick
    tick = YF(ticker)

    OUTPUT += str(tick.get_summary_data()) + '\n'
    OUTPUT += mark + '\n'
    OUTPUT += str(tick.get_stock_quote_type_data()) + '\n'
    OUTPUT += mark + '\n'
    OUTPUT += str(tick.get_stock_price_data()) + '\n'
    OUTPUT += mark + '\n'
    OUTPUT += str(tick.get_current_price()) + '\n'
    OUTPUT += mark + '\n'
    OUTPUT += str(tick.get_dividend_rate()) + '\n'

    try:
        r = tick._cache.keys()
    except AttributeError:
        pass
    else:
        OUTPUT += mark + '\n'
        OUTPUT += str(r) + '\n'


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
    OUTPUT += mark + '\n'
    st = time.time()
    f(*args)
    et = time.time()
    OUTPUT += mark + '\n'
    print(et - st, 'seconds')


def test_button():
    global DEFAULT_ARGS
    global OUTPUT
    DEFAULT_ARGS = (first_entry.get())

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

    text = tk.Text(root, wrap='word')
    text.insert('insert', OUTPUT)
    text.place(x=1, y=46, width= 722, height= 300)
    root.update()
    OUTPUT = ''


def display_stock_graph():
    # stock ticker
    DEFAULT_ARGS = (first_entry.get())

    # makes the ticker a object
    ticker_data = yf.Ticker(DEFAULT_ARGS)

    # creates the boundary to extract data from
    current_day = datetime.now().strftime('%Y-%m-%d')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    current_day_data = ticker_data.history(start=current_day, end=tomorrow, interval='1m')

    # shows data in intervals of 30 minutes
    hours_data_30 = current_day_data.between_time('09:00:00', '16:00:00').resample('30T').last()

    # Create empty lists to store the time and price
    stock_times = []
    stock_prices = []

    # puts the items in their list
    for hour, price in zip(hours_data_30.index, hours_data_30['Close']):
        time = hour.strftime('%H:%M')
        stock_times.append(time)
        stock_prices.append(price)

    # Create a figure and add a subplot
    fig = Figure(figsize=(14, 4), dpi=100)
    grap = fig.add_subplot(111)

    # Plot the data as a line graph
    grap.plot(stock_times, stock_prices)

    # Labels the graph
    _title = DEFAULT_ARGS + "'s Daily Prices"
    grap.set_title(_title)
    grap.set_xlabel("Time")
    grap.set_ylabel("Stock Price")

    # Create a canvas to display the graph in Tkinter
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().place(x=0, y=390)

    # end of this method

# BEGIN TKINTER BUILD

# Holds data for drop down menus
currency_options = [
    "USD",
    "CAN",
    "EUR"
]

root = tk.Tk()
root.title("test")
root.geometry("2000x900")

# Search bar text
first_label = tk.Label(root, text='Enter ticker here: ', font=('Times', 22))
first_label.pack(side='left', anchor='nw')

first_entry = tk.Entry(root, font=('Times', 26))
first_entry.pack(side='left', anchor='nw')

# Create Dropdown menu for currency type
clicked = tk.StringVar()  # datatype of menu text
clicked.set("$")  # initial menu text
currency_drop = tk.OptionMenu(root, clicked, *currency_options)
currency_drop.config(height=2, width=10)
currency_drop.pack(side='left', anchor='nw')

search_bar_go_button = tk.Button(root, text='GO', command=lambda: test_button(), height=2, width=5)
search_bar_go_button.place(x='677', y=3)

stock_data_label = tk.Label(root, text='test ', font=('Times', 22))
stock_data_label.place()

quit_button = tk.Button(root, text='Quit', command=root.quit, height=2, width=5)
quit_button.place(x=1480, y=0)

# Graph button
graph_button = tk.Button(root, text='Graph', command=lambda: display_stock_graph(), height=2, width=5)
graph_button.place(x=10, y=348)


root.mainloop()
