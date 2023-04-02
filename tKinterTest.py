import tkinter as tk
import sys
import time
from yahoofinancials import YahooFinancials as YF


DEFAULT_ARGS = ('DOGE-JPY')
MODULE_ARGS = ('yf', 'yahoofinancial', 'yahoofinancials')
HELP_ARGS = ('-h', '--help')
OUTPUT = ''
mark = '-' * 64


def default_api(ticker):
    global OUTPUT
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
    text.place(x=1, y=30)
    root.update()
    OUTPUT = ''


# BEGIN TKINTER BUILD

# Holds data for drop down menus
currency_options = [
    "USD",
    "CAN",
    "EUR"
]

stock_data = [

]

root = tk.Tk()
root.title("test")
root.geometry("2000x900")

first_label = tk.Label(root, text='Enter ticker here: ')
first_label.pack(side='left', anchor='nw')

first_entry = tk.Entry(root)
first_entry.pack(side='left', anchor='nw')

# Create Dropdown menu for currency type
clicked = tk.StringVar()  # datatype of menu text
clicked.set("$")  # initial menu text
currency_drop = tk.OptionMenu(root, clicked, *currency_options)
currency_drop.config(width=6)
currency_drop.pack(side='left', anchor='nw')

search_bar_go_button = tk.Button(root, text='GO', command=lambda:test_button(), height = 1, width = 5)
search_bar_go_button.place(x='300', y=0)

quit_button = tk.Button(root, text='Quit', command=root.quit)
quit_button.place(x=1490, y=0)

# Graph button
graph_button = tk.Button(root, text='Graph')
graph_button.place(x=10, y=450)

root.mainloop()

