"""
Small script written by FokjeM/Riven Skaye

Written for Dayt solely for getting the current volume levels of
all media files in a directory and its sub-directories.
Expect quick and dirty solutions.
"""
from pathlib import Path # To get all the files
import os # We need this to create a text file and output to it
import sys # We need this for to parse the arguments
import subprocess

# Make sure we're system independent so long as ffmpeg exists on the PATH variable
if sys.platform.startswith("win"):
    dump = "NUL"
else:
    dump = "/dev/null"
printnext = False # Begin ignoring output of ffmpeg
targets = sys.argv[1:] # Allow multiple target directories, get all of the input except for this file.
if len(targets) == 0:
    targets.append(str(sys.path[0])) # If no args were given, run here
for target in targets:
    os.chdir(target) # Set the target directory as current working directory
    for f in list(Path(".").glob("volumelevels.txt")):
        os.remove(str(f.absolute()))
        print("Deleted old volumelevels.txt")
    for f in list(Path(".").glob("*.*")):
        if f.is_file():
            if str(f.absolute()).endswith(".py"):
                continue
            results = []
            res = subprocess.run(["ffmpeg", "-i", str(f.absolute()), "-hide_banner", "-vn", "-af", "volumedetect", "-f", "null", dump], capture_output=True)
            if res.returncode > 0:
                print("Whoops! We fucked up! Found a non-media file:")
                print(str(f.absolute()))
                continue
            for out in str(res.stderr).split("\r\n"):
                for r in out.split():
                    # Add relevant info in reverse so we can use pop later
                    if "mean_volume" in r or "max_volume" in r: #unless it's mean or max volume
                        printnext = True # Add the next element, we'll need it
                    elif printnext:
                        results.insert(0, r)
                        printnext = False # Start ignoring until next match
            with open("volumelevels.txt", "a") as output: # Create a filehandle. Overwrite existing files if need be.
                output.write("File: %s\n" % str(f.absolute()))
                output.write("Levels:\n\t")
                output.write("mean_volume: %s\n\tmax_volume: %s\n\n" % (results.pop(), results.pop()))
