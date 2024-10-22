# Import necessary libraries
from json import load as jsonload
from math import floor
from os import listdir, isfile
from os.path import split as path_split, abspath, join
from time import time
from shutil import copy  # Import copy from shutil
from common import logs 


# CONFIGURATION --------------------------------------------------------
GLOBAL_CONFIG = join(path_split(abspath(__file__))[0], "config.json")

# FUNCTIONS ------------------------------------------------------------
def in_boundary(X, Y, startX, startY, endX, endY):
    """Determines if a co-ordinate is within a boundary"""
    return (int(X) >= int(startX)) and (int(X) <= int(endX)) and \
           (int(Y) >= int(startY)) and (int(Y) <= int(endY))

def load_configuration(file):
    """Loads the JSON Configuration document as defined"""
    if isfile(file):
        try:
            with open(file) as file_object:
                return jsonload(file_object)
        except Exception as error:
            raise ValueError("Improperly formatted configuration") from error
    else:
        raise FileNotFoundError(f"File not found: {file}")

def resetmap(log, path, output_path,  # Added output_path parameter
             startX, startY, startChunkX, startChunkY,
             endX, endY, endChunkX, endChunkY):
    """Copies a series of files that are within the boundaries to the output directory."""
    files = listdir(path)
    counter_map = 0
    counter_meta = 0
    timer_start = time()

    # Co-ordinates are sent in absolute tiles; we convert them for filename checks
    startX = floor(startX / 10)
    startY = floor(startY / 10)
    endX = floor(endX / 10)
    endY = floor(endY / 10)

    # Loop through the map files and copy any that are within our boundaries
    for file in files:
        current_item = file[:-4].split('_')
        # Copy Map files that are within our co-ordinates
        if len(current_item) == 3 and current_item[0] == 'map':
            if in_boundary(current_item[1], current_item[2], startX, startY, endX, endY):
                log.add(f"> Copying {file} to {output_path}")
                copy(join(path, file), output_path)  # Use shutil.copy
        # If not a map file, but actually meta data then if it's in chunk data
        elif len(current_item) == 3 and current_item[0] == 'chunkdata':
            if in_boundary(current_item[1], current_item[2], startChunkX, startChunkY, endChunkX, endChunkY):
                log.add(f"> Copying {file} to {output_path}")
                copy(join(path, file), output_path)  # Use shutil.copy

    log.add_header("Summary")
    log.add(f"> Completed in {(time() - timer_start):.2f} seconds")
    log.add(f"> Removed {counter_map:,d} map files")
    log.add(f"> Removed {counter_meta:,d} meta files")

# MAIN -----------------------------------------------------------------
def main(user_config):
    """Main application routine"""
    # Load Configuration settings
    config = load_configuration(user_config)

    # Setup Logfile settings
    log = logs.NewLog(65, config['logs']['save'], config['logs']['path'])
    log.enable_treeview()

    # Prompt the user for which region they want to be reset
    counter = 0
    print("Which region would you like to reset?")
    print("")
    for region in config['regions']:
        print(f"  {counter}\t{region['name']}")
        counter += 1
    print("")
    selection = input("Reset region #")
    try:
        selection = int(selection)
    except ValueError:
        print("ERROR: Incorrect region selection")
        exit(1)

    if int(selection) < 0 or (int(selection) >= int(counter)):
        print("ERROR: Region out of bounds")
        exit(2)

    # Display some meta information about your selection
    log.timestamp()
    log.add_header(f"{config['regions'][selection]['name']}")
    log.add(f"> Region: {selection}")
    log.add(f"> Start:  {config['regions'][selection]['start'][0]} x "
            f"{config['regions'][selection]['start'][1]} "
            f" Chunk ({config['regions'][selection]['start'][2]} x "
            f"{config['regions'][selection]['start'][3]})")
    log.add(f"> Stop:   {config['regions'][selection]['stop'][0]} x "
            f"{config['regions'][selection]['stop'][1]} "
            f" Chunk ({config['regions'][selection]['stop'][2]} x "
            f"{config['regions'][selection]['stop'][3]})")
    log.add_header("Reset Log")

    # Reset the selected boundaries
    resetmap(log, config['path'], config['output_path'],  # Pass output_path here
             config['regions'][selection]['start'][0],
             config['regions'][selection]['start'][1],
             config['regions'][selection]['start'][2],
             config['regions'][selection]['start'][3],
             config['regions'][selection]['stop'][0],
             config['regions'][selection]['stop'][1],
             config['regions'][selection]['stop'][2],
             config['regions'][selection]['stop'][3])

    # Done
    log.timestamp()

# ROUTINE --------------------------------------------------------------
if __name__ == "__main__":
    main(GLOBAL_CONFIG)