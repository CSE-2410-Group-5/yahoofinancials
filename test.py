import yfinance
import csv

def is_valid_ticker(symbol):
    try:
        ticker = yfinance.Ticker(symbol)
        info = ticker.info['regularMarketPrice']
        return True
    except:
        return False

# Open the CSV file for reading
with open('file.csv', 'r') as csv_file:
    # Create a reader object
    csv_reader = csv.reader(csv_file)
    # Initialize an empty list to hold the values
    values = []
    # Iterate over the rows in the CSV file
    for row in csv_reader:
        # Add the values in the current row to the list
        values.extend(row)

valid = []

for i in values:
    if(is_valid_ticker(i)):
        valid.append(i)

print(valid)