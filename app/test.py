#  # Add the 'ticker' symbol to each feed for easier identification
            

import os
import json
from google.protobuf.json_format import MessageToDict
import pandas as pd
# tick_data ='{"type": "live_feed", "feeds": {"NSE_EQ|INE263A01024": {"ltpc": {"ltp": 404.55, "ltt": "1759904762170", "ltq": "2", "cp": 410.3}}, "NSE_EQ|INE0HV901016": {"ltpc": {"ltp": 297.75, "ltt": "1759904762075", "ltq": "5", "cp": 310.7}}, "NSE_EQ|INE134E01011": {"ltpc": {"ltp": 400.7, "ltt": "1759904761706", "ltq": "3", "cp": 408.8}}, "NSE_EQ|INE154A01025": {"ltpc": {"ltp": 398.8, "ltt": "1759904762211", "ltq": "24", "cp": 399.8}}, "NSE_EQ|INE066P01011": {"ltpc": {"ltp": 139.19, "ltt": "1759904753154", "ltq": "11", "cp": 139.38}}, "NSE_EQ|INE681B01017": {"ltpc": {"ltp": 590.0, "ltt": "1759904761992", "ltq": "62", "cp": 573.7}}, "NSE_EQ|INE053F01010": {"ltpc": {"ltp": 124.65, "ltt": "1759904761358", "ltq": "1", "cp": 127.08}}, "NSE_EQ|INE002A01018": {"ltpc": {"ltp": 1371.9, "ltt": "1759904762021", "ltq": "17", "cp": 1384.8}}, "NSE_EQ|INE062A01020": {"ltpc": {"ltp": 860.75, "ltt": "1759904762138", "ltq": "1", "cp": 864.7}}, "NSE_EQ|INE13B501022": {"ltpc": {"ltp": 491.2, "ltt": "1759904761736", "ltq": "1", "cp": 460.0}}, "NSE_EQ|INE040H01021": {"ltpc": {"ltp": 53.08, "ltt": "1759904762074", "ltq": "1", "cp": 54.01}}, "NSE_EQ|INE131A01031": {"ltpc": {"ltp": 592.7, "ltt": "1759904761925", "ltq": "20", "cp": 583.95}}, "NSE_EQ|INE020B01018": {"ltpc": {"ltp": 373.0, "ltt": "1759904761450", "ltq": "2", "cp": 377.75}}, "NSE_EQ|INE531E01026": {"ltpc": {"ltp": 341.7, "ltt": "1759904761633", "ltq": "500", "cp": 332.65}}, "NSE_EQ|INE205A01025": {"ltpc": {"ltp": 470.0, "ltt": "1759904762201", "ltq": "69", "cp": 471.85}}, "NSE_EQ|INE090A01021": {"ltpc": {"ltp": 1367.6, "ltt": "1759904762144", "ltq": "100", "cp": 1375.9}}, "NSE_EQ|INE202E01016": {"ltpc": {"ltp": 149.6, "ltt": "1759904762000", "ltq": "265", "cp": 152.44}}, "NSE_EQ|INE040A01034": {"ltpc": {"ltp": 979.4, "ltt": "1759904761973", "ltq": "1", "cp": 982.5}}, "NSE_EQ|INE192H01020": {"ltpc": {"ltp": 391.2, "ltt": "1759904762210", "ltq": "64", "cp": 389.75}}, "NSE_EQ|INE121E01018": {"ltpc": {"ltp": 535.4, "ltt": "1759904761867", "ltq": "20", "cp": 548.05}}, "NSE_EQ|INE00H001014": {"ltpc": {"ltp": 422.05, "ltt": "1759904760878", "ltq": "1", "cp": 420.75}}, "NSE_EQ|INE0LEZ01016": {"ltpc": {"ltp": 648.5, "ltt": "1759904762185", "ltq": "100", "cp": 630.05}}, "NSE_EQ|INE816B01035": {"ltpc": {"ltp": 52.81, "ltt": "1759904762155", "ltq": "59", "cp": 49.74}}, "NSE_EQ|INE038A01020": {"ltpc": {"ltp": 773.75, "ltt": "1759904761480", "ltq": "61", "cp": 767.8}}, "NSE_EQ|INE976G01028": {"ltpc": {"ltp": 282.45, "ltt": "1759904761206", "ltq": "168", "cp": 273.55}}, "NSE_EQ|INE203G01027": {"ltpc": {"ltp": 219.21, "ltt": "1759904759652", "ltq": "5", "cp": 220.12}}, "NSE_EQ|INE070D01027": {"ltpc": {"ltp": 158.4, "ltt": "1759904761455", "ltq": "30", "cp": 143.92}}, "NSE_EQ|INE248A01017": {"ltpc": {"ltp": 366.45, "ltt": "1759904762197", "ltq": "18", "cp": 324.15}}, "NSE_EQ|INE084A01016": {"ltpc": {"ltp": 124.41, "ltt": "1759904761575", "ltq": "12", "cp": 126.24}}, "NSE_EQ|INE269A01021": {"ltpc": {"ltp": 375.4, "ltt": "1759904761452", "ltq": "153", "cp": 352.6}}, "NSE_EQ|INE674K01013": {"ltpc": {"ltp": 295.7, "ltt": "1759904761187", "ltq": "5", "cp": 303.5}}, "NSE_EQ|INE457F01013": {"ltpc": {"ltp": 879.0, "ltt": "1759904761426", "ltq": "1", "cp": 764.1}}, "NSE_EQ|INE528G01035": {"ltpc": {"ltp": 22.0, "ltt": "1759904761919", "ltq": "52", "cp": 22.22}}, "NSE_EQ|INE081A01020": {"ltpc": {"ltp": 172.18, "ltt": "1759904762207", "ltq": "7", "cp": 171.43}}, "NSE_EQ|INE476A01022": {"ltpc": {"ltp": 125.42, "ltt": "1759904761509", "ltq": "1649", "cp": 128.06}}, "NSE_EQ|INE245A01021": {"ltpc": {"ltp": 389.15, "ltt": "1759904761714", "ltq": "23", "cp": 392.5}}, "NSE_EQ|INE095A01012": {"ltpc": {"ltp": 740.4, "ltt": "1759904760819", "ltq": "20", "cp": 749.0}}, "NSE_EQ|INE139A01034": {"ltpc": {"ltp": 222.93, "ltt": "1759904762214", "ltq": "50", "cp": 217.07}}, "NSE_EQ|INE415G01027": {"ltpc": {"ltp": 347.95, "ltt": "1759904756808", "ltq": "50", "cp": 354.85}}, "NSE_EQ|INE758T01015": {"ltpc": {"ltp": 337.35, "ltt": "1759904762209", "ltq": "108", "cp": 337.85}}}, "currentTs": "1759904762281"}'


def _initialize_instrument_map():
        """
        Creates and returns a mapping from instrument_key to tradingsymbol.
        Reads from 'instruments.csv' located in the project root.
        """
        instruments_file_path =  "instruments.csv"
        print(f"Creating instrument map from: {instruments_file_path}")
        try:
            df = pd.read_csv(instruments_file_path)
            return pd.Series(df.tradingsymbol.values, index=df.instrument_key).to_dict()
        except FileNotFoundError:
            print(f"ERROR: The file {instruments_file_path} was not found.")
            return {}
        except Exception as e:
            print(f"Could not create instrument map: {e}")
            return {}

# instrument_map = _initialize_instrument_map()
# data_to_dump  = json.loads(tick_data)
# if 'feeds' in data_to_dump:
#     for key, feed_data in data_to_dump['feeds'].items():
#         print(key)
#         feed_data['ticker'] = instrument_map.get(key, 'UNKNOWN')
#         print(feed_data)
                    
# print("#####"*80)
# print(feed_data['ticker'])
# newSTR = json.dumps(data_to_dump)

# data_to_dump  = json.loads(newSTR)
# if 'feeds' in data_to_dump:
#     for key, feed_data in data_to_dump['feeds'].items():
#         print(key)
#         key = instrument_map.get(key, 'UNKNOWN')
#         print(feed_data)

# print(json.dumps(data_to_dump))



# import json

# tick_data_str = '{"type": "live_feed", "feeds": {"NSE_EQ|INE263A01024": {"ltpc": {"ltp": 404.55, "ltt": "1759904762170", "ltq": "2", "cp": 410.3}}, "NSE_EQ|INE0HV901016": {"ltpc": {"ltp": 297.75, "ltt": "1759904762075", "ltq": "5", "cp": 310.7}}}}'

# # Step 1: Define the mapping
# instrument_mapping = {
#     "NSE_EQ|INE263A01024": "HDFC",
#     "NSE_EQ|INE0HV901016": "ADANI",
# }

# # Step 2: Parse the JSON string into a dictionary
# tick_data_dict = json.loads(tick_data_str)

# # Step 3: Replace the keys in the dictionary
# new_feeds = {}
# for old_key, data in tick_data_dict["feeds"].items():
#     if old_key in instrument_mapping:
#         new_feeds[instrument_mapping[old_key]] = data
#     else:
#         new_feeds[old_key] = data

# # Update the feeds in the main dictionary
# tick_data_dict["feeds"] = new_feeds

# # Step 4: Convert the modified dictionary back to a JSON string
# modified_json_str = json.dumps(tick_data_dict, indent=4)

# print(modified_json_str)



import json
import os

def replace_instrument_keys_in_file(filepath, instrument_map, filepath2):
    """
    Reads a JSON file, replaces keys in the 'feeds' dictionary based on a map,
    and overwrites the file with the modified JSON.
    """
    try:
        # Read the entire JSON file into a Python dictionary
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        # Check if the 'feeds' key exists and is a dictionary
        if "feeds" in data and isinstance(data["feeds"], dict):
            new_feeds = {}
            # Iterate through the original 'feeds' dictionary
            for old_key, feed_data in data["feeds"].items():
                # Replace the key if it exists in the instrument map
                new_symbol = instrument_map.get(old_key, old_key)
                new_feeds[new_symbol] = feed_data
            
            # Update the main data dictionary with the new feeds
            data["feeds"] = new_feeds

            # Write the modified data back to the same file
            with open(filepath2, 'w') as f:
                # Use indent for a human-readable format
                json.dump(data, f, indent=4)
            
            print(f"Successfully updated instrument keys in '{filepath}'.")
        else:
            print(f"No 'feeds' dictionary found in '{filepath}'. No changes made.")

    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{filepath}'. Please check file format.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# --- Configuration ---
# 1. Define your instrument key to symbol mapping
instrument_map  = _initialize_instrument_map()

# 2. Specify the path to your JSON file
file_path = 'static/UpstoxWSS_08_10_25.txt' # Make sure this is the correct filename
file_path2 = 'static/UpstoxWSS_08_10_25_new.txt' # Make sure this is the correct filename

import json

def replace_instrument_keys_in_jsonl(input_file, output_file, instrument_map):
    """
    Reads a file with one JSON object per line, replaces keys in the 'feeds'
    dictionary, and writes the modified JSON to a new file.
    
    Args:
        input_file (str): The path to the input file.
        output_file (str): The path to the output file.
        instrument_map (dict): A dictionary mapping old keys to new symbols.
    """
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            for line in infile:
                # Skip empty lines
                if not line.strip():
                    continue

                try:
                    # Parse the JSON string from the current line
                    data = json.loads(line)
                    
                    # Check if 'feeds' exists and is a dictionary
                    if "feeds" in data and isinstance(data["feeds"], dict):
                        new_feeds = {}
                        # Replace keys based on the map
                        for old_key, feed_data in data["feeds"].items():
                            new_symbol = instrument_map.get(old_key, old_key)
                            new_feeds[new_symbol] = feed_data
                        
                        data["feeds"] = new_feeds
                    
                    # Convert the modified dictionary back to a JSON string and write it
                    # The newline character is important for the JSONL format
                    outfile.write(json.dumps(data) + '\n')
                    
                except json.JSONDecodeError:
                    print(f"Skipping malformed JSON line: {line.strip()}")
                
        print(f"Processing complete. Modified data written to '{output_file}'.")
    
    except FileNotFoundError:
        print(f"Error: One of the files was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

 
# 2. Specify the paths for your input and output files
input_file_path = 'tick_data_per_line.json'
output_file_path = 'modified_tick_data_per_line.json'

# --- Run the script ---
if __name__ == "__main__":
 
    
    replace_instrument_keys_in_jsonl(file_path, file_path2, instrument_map)
