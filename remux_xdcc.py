#!/usr/bin/env python

import argparse
import re
import subprocess
from pathlib import Path
from shutil import which
from typing import Union

# Create an argparser insance
parser = argparse.ArgumentParser(
    description="Automated remuxing of matroska downloads to mp4 video.\n"
    "Exits with an exit code of 2 if ffmpeg can't be found, 3 if `infile`"
    "was not a matroska video (or actually if it doesn't end in `.mkv`).\n"
    "And whatever ffmpeg returns as exit code if this script didn't fail."
)
# Check for the useful args. Might wanna override the pattern or something
parser.add_argument("--infile", "-i", required=True, type=str,
                    help="The input file to process. If it's not an mkv,"
                    "expect an early exit.")
parser.add_argument("--pattern", "-P", required=False, type=str,
                    help="Override the replacement pattern.")
parser.add_argument("--ffmpeg", required=False, type=str,
                    help="Exact path to your copy of ffmpeg")
# Fetch the actual args
args = parser.parse_args()

if not args.infile.endswith(".mkv"):
    print("This script was specifically made for remuxing from "
          "matroska to mp4 containers. This file is no bueno!")
    exit(3)


# These symbols be danger!
danger = re.compile(r"[\~\$\{\}\!\?\|\:\s]")
# These symbols be groupnames! Or resolutions. Just info though.
groupnames = re.compile(r"\_*\[\S+?\]\_*")


def clean_name(name: str,
               replacements: Union[re.Pattern, str, None] = None
               ) -> str:
    """Clean up a name from unsafe stuff and groupnames.

    Optionally takes a replacements argument that should be a RegExp, or
    a string representation thereof. The pattern is used to filter out
    characters that are undesirable in the output.
    """
    if replacements is None:
        replacements = danger
    elif not isinstance(replacements, re.Pattern):
        replacements = re.compile(replacements)
    safe = re.sub(replacements, "", name)
    return re.sub(groupnames, "", safe).replace("_-_", "-")


def get_outname(name: str) -> str:
    chunks = name.split(".")[1:]
    spliced = "".join(chunks[:-1]) + ".mp4"
    return clean_name(spliced)


def do_ffmpeg(infile: str, outfile: str) -> int:
    # Return the exit code of the ffmpeg call
    return subprocess.call([
        # This saves your logs, if you use them
        str(ffmpeg), "-hide_banner",
        # Grab input
        "-i", infile,
        # Copy codecs
        "-c", "copy",
        # Don't nag about experimental mp4 codec support
        "-strict", "-2"
        # Fix subs
        "-c:s", "mov_text",
        # Write here
        outfile
    ])


if __name__ == "__main__":
    # Get the place where your ffmpeg copy lives
    ffmpeg = which("ffmpeg") if not args.ffmpeg else args.ffmpeg
    if ffmpeg is None:
        # And screech if none was found
        print("ffmpeg could not be found on the system! Please add it to"
              "the path or install it if you haven't.\n"
              "Otherwise, this program is unusable.")
        exit(2)
    # Get an absolute path to the infile and resolve any `./` and `../`
    infile = Path(args.infile).absolute().resolve()
    # Get the directory the file is in
    indir = infile.parent
    # Create a directory next to indir called "processed"
    outdir = indir.parent.joinpath("processed")
    # Or don't create it if it exists
    outdir.mkdir(exist_ok=True)
    # Get the output filename
    outfile = get_outname(infile)
    # Replace the input directory with the output directory
    outfile = outfile.replace(str(indir), str(outdir))
    # Make sure to capture ffmpeg's result
    result = do_ffmpeg(infile, outfile)
    # And use it as our exit code.
    exit(result)
