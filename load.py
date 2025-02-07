import datetime
import csv
import glob
from datetime import datetime, timedelta

# Should I add shit to a set to make sure there are no dupes? There doesnt seem to be any in the CSV so I didnt bother,
#Also is not adding 'bad' data valid

def main():
    csv_files = glob.glob("data/ctg_tick*.csv")
    header = ["Timestamp", "Price", "Size"]
    times = set()

    with open(file="output.csv", mode="w", newline="") as out_file: # WITH CLOSES BY DEFAULT, FIRST PARAM = FIle path
        writer = csv.writer(out_file)
        writer.writerow(header)

        for file in csv_files:

            with open(file, mode="r") as in_file:
                content = csv.reader(in_file)
                

                for line in content:
                    timestamp, price_str, size_str = line


                    if timestamp == "Timestamp": #Skips header
                        continue

                    if timestamp not in times and isClean(timestamp, price_str, size_str): #timestamp not in times takes care of potential duplicate times
                        writer.writerow(line)
                        times.add(timestamp)

      # Get user input for start and end times
    print("\nEnter datetime values in format: YYYY-MM-DD HH:MM:SS.fff")
    start_time = get_valid_datetime("Enter start time: ")
    end_time = get_valid_datetime("Enter end time: ")
    
    # Validate that end time is after start time
    while end_time <= start_time:
        print("End time must be after start time.")
        end_time = get_valid_datetime("Enter end time: ")
    
    # Get interval from user
    interval = get_valid_interval()

    
    start_time = datetime.strptime("2024-09-16 20:35:07.270", "%Y-%m-%d %H:%M:%S.%f")
    end_time = datetime.strptime("2024-09-17 13:50:01.089", "%Y-%m-%d %H:%M:%S.%f")
    filtered = makeData(start_time, end_time)
    ohlcv_bars = generate_ohlcv_for(filtered, start_time, end_time)

    write_ohlcv_to_csv(ohlcv_bars, "sorted.csv")

def isClean(time, price, size):
    #ISSUES FOUND, NEG PRICES, DECIMAL POINT ERRORS (40 instead of 400), MISSING DATA
    
    if time == "" or price == "" or size == "":
        #takes care of missing data by continuing to next input 
        return False
    
    try:
        price = float(price)
        size = int(size)
    except ValueError:
        return False
    

    if int(price) < 0 or round(price/10)< 20: 
        #Takes care of decimal point errors and negative prices
        return False
    return True
    
def get_valid_datetime(prompt):
 
    while True:
        try:
            date_str = input(prompt)
            return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            print("Use: YYYY-MM-DD HH:MM:SS.fff")

def validate_interval(interval):
   
    if not interval:
        return False
        
    valid_units = {'s', 'm', 'h', 'd'}
    num = ""
    
    for char in interval:
        if char.isdigit():
            num += char
        elif char in valid_units:
            if not num:  # No number before unit
                return False
            num = ""
        else:
            return False
            
    return num == ""  # Should have ended with a valid unit

def get_valid_interval():
    while True:
        interval = input("Enter time interval (e.g., '4s', '15m', '2h', '1d'): ")
        if validate_interval(interval):
            return interval
        print("Invalid interval format. Examples: '4s', '15m', '2h', '1d'")
        
def getSeconds(time):
    units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    total = 0
    num = ""
    for char in time:
        if char.isdigit():
            num += char
        else:
            total += int(num) * units[char]
            num = "" #clears num for next input 

    return total
    
def makeData(start, end):
    filtered_data = []
    start_time = start

    with open(file="output.csv", mode="r") as data_file:
        content = csv.reader(data_file)
        for line in content:
            timestamp = line[0]
            if timestamp == "Timestamp":
                continue
            
            curr = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
            

            if start_time <= curr < end:
                filtered_data.append(line)
            if curr >= end:
                break
    return filtered_data

def generate_ohlcv_for(filtered_data, start_time, end_time, interval="1m"):
    interval_seconds = getSeconds(interval)
    ohlcv_bars = []
    current_time = start_time
    
    while current_time < end_time:
        next_time = current_time + timedelta(seconds=interval_seconds)
        
        open_price = None
        high_price = float('-inf')
        low_price = float('inf')    
        close_price = None
        total_volume = 0
        
        for trade in filtered_data:
            trade_time = datetime.strptime(trade[0], "%Y-%m-%d %H:%M:%S.%f")
            
            if trade_time >= next_time:
                break
                
            if current_time <= trade_time < next_time:
                price = float(trade[1])
                volume = float(trade[2])      
               
                if open_price is None:
                    open_price = price             
               
                high_price = max(high_price, price)
                low_price = min(low_price, price)
               
               
                close_price = price        
                total_volume += volume
        
        if open_price is not None:
            ohlcv_bars.append([
                current_time,
                open_price,
                high_price,
                low_price,
                close_price,
                total_volume
            ])      
        current_time = next_time
    
    return ohlcv_bars

def write_ohlcv_to_csv(ohlcv_bars, output_filename):
    print(ohlcv_bars)
    with open(output_filename, "w", newline="") as csvfile:
        
        writer = csv.writer(csvfile)
       
        writer.writerow(["Timestamp", "Open", "High", "Low", "Close", "Volume"]) #HEADER

        for bar in ohlcv_bars:
            time = bar[0].strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([time, bar[1], bar[2], bar[3], bar[4], bar[5]])
# DO YOU NEED TO MAKE OHLC A CANDLE STICK THINGY OR CAN IT JUST BE OUTPUT IN A CSV FILE 

main()