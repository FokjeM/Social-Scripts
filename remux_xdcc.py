#!/usr/bin/env python

import argparse
import re
import subprocess
from pathlib import Path
from shutil import which
from typing import Optional, Union

# Create an argparser insance
parser = argparse.ArgumentParser(
    description="Automated remuxing of matroska downloads to mp4 video."
    "Exits with an exit code of 2 if ffmpeg can't be found, 3 if `infile`"
    "was not a matroska video (or actually if it doesn't end in `.mkv`)."
    "And whatever ffmpeg returns as exit code if this script didn't fail."
)
# Check for the useful args. Might wanna override the pattern or something
parser.add_argument("--infile", "-i", required=True, type=str,
                    help="The input file to process. If it's not an mkv,"
                    "expect an early exit.")
parser.add_argument("--ffmpeg", required=False, type=str, default=None,
                    help="Exact path to your copy of ffmpeg. Not required if"
                    "ffmpeg lives on your PATH")
parser.add_argument("--pattern", "-P", required=False, type=str, default=None,
                    help="Override the replacement pattern.")
parser.add_argument("--keep", "-k", "--save", default=False, type=bool,
                    required=False,
                    help="Whether or not to keep the file. Defaults to False.")
parser.add_argument("--overwrite", "--yes", "-y", default=True, required=False,
                    type=bool,
                    help="Whether or not to add the `-y` flag to ffmpeg. "
                    "Defaults to True.")
parser.add_argument("--debug", default=False, type=bool,
                    help="print paths instead of doing anything.")
# Fetch the actual args
args = parser.parse_args()

if not args.infile.endswith(".mkv"):
    print("This script was specifically made for remuxing from "
          "matroska to mp4 containers.")
    print(f"{args.infile} is no bueno!")
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


def get_outname(name: str, repls: Optional[str] = None) -> str:
    """Get a cleaned up output name representing the input file.

    Pray it doesn't collide, ffmpeg doesn't override by default.
    """
    chunks = name.split(".")[1:]
    spliced = "".join(chunks[:-1]) + ".mp4"
    return clean_name(spliced, repls)


def do_ffmpeg(infile: str, outfile: str) -> int:
    # Return the exit code of the ffmpeg call
    ffmpeg_args = [
        # This saves your logs, if you use them
        str(ffmpeg), "-hide_banner",
        # Grab input
        "-i", infile,
        # Copy codecs
        "-c", "copy",
        # Don't nag about experimental mp4 codec support
        "-strict", "-2",
        # Fix subs
        "-c:s", "mov_text",
        # Write here
        outfile
    ]
    if args.overwrite:
        ffmpeg_args += ["-y"]
    return subprocess.call(ffmpeg_args)


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
    infile = Path(args.infile).absolute()
    if not infile.is_file():
        print(f"{infile} is not a real file, can't pass it to ffmpeg!")
        exit(3)

    infile_name = infile.name
    # Get the directory the file is in
    indir = infile.parent.resolve()
    # Resolve any symlinks and relatives on the infile pathname
    infile = infile.resolve()

    # Create a directory next to indir called "processed"
    outdir = indir.parent.joinpath("processed")
    # Or don't create it if it exists
    outdir.mkdir(exist_ok=True)

    # Get the output filename
    outfile = get_outname(infile_name, args.pattern)
    # Replace the input directory with the output directory
    outfile = outdir.joinpath(outfile)

    # Are we there yet?
    if args.debug:
        print(f"Infile: `{infile}` in `{indir}`\n"
              f"Outfile: `{outfile}` in `{outdir}`")
        exit(0)

    # Make sure to capture ffmpeg's result
    result = do_ffmpeg(infile, outfile)
    if result == 0 and not args.keep:
        infile.unlink()
    # And use it as our exit code.
    exit(result)
