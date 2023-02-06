import re
from subprocess import call, DEVNULL
from pathlib import Path
from shutil import which
from sys import exec_prefix
from Typing import Optional, Union

# For checking WeeChat import
import_ok = True

try:
    import weechat
except ImportError:
    print("You must run this script within WeeChat!\n"
          "http://weechat.org")
    import_ok = False

SCRIPT_NAME = "xfer_remux_mkv"
SCRIPT_AUTHOR = "Brian Dashore <bdashore3@gmail.com>, "
                "Riven Skaye <riven@tae.moe>"
SCRIPT_VERSION = "0.1"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC = "Runs a command on xfer_ended signal with acces to data (with trigger not possible)"

# These symbols are absolutely unwanted for filenames.
danger = re.compile(r"[\~\$\{\}\!\?\|\:\s]")
# These symbols represent info that is already in the metadata.
groupnames = re.compile(r"\_*\[\S+?\]\_*")


def get_outname(name: str) -> str:
    """Remove unwanted components from a filename and return a proper output name.

    This function naïvely removes dangerous components from filenames to prevent
    silly crafted names like 'somefile ; rm -rf "$SHELL"' from breaking the system.
    If the name collides, ffmpeg will not output anything by default, unless the -y flag
    is specified.
    """
    chunks = name.split(".")[1:]
    spliced = "".join(chunks[:-1]) + ".mp4"
    safe = re.sub(danger, "", spliced)
    return re.sub(groupnames, "", safe).replace("_-_", "-")


def fetch_outpath(infile: Path) -> Path:
    """Create the output path based on the input path.

    This is used to make sure `../processed/` exists and to generate the full
    path for ffmpeg to output the remuxed file to.
    """
    if not infile.is_file():
        raise ValueError(f"{infile} is not a file or symlink!")
    
    if not infile.name.endswith(".mkv"):
        raise ValueError(f"{infile.name} is not a matroska video file!")

    # Make sure we have the correct, absolute directory for ffmpeg
    indir = infile.parent.absolute().resolve()

    outdir = indir.parent.joinpath("processed")
    # Create outdir if it doesn't exist
    outdir.mkdir(exist_ok=True)
    outfile = get_outname(infile.name)
    return outdir.joinpath(outfile)


def do_ffmpeg(infile: str, outfile: str) -> int:
    """The star of the show, this calls ffmpeg and returns its exit status.

    If the exit status is non-zero (indicating something went wrong), the user
    should handle the issue themselves. There are very few things that could
    cause this ffmpeg command to go wrong, according to the authors of this script.
    """
    ffmpeg_args = [
        str(ffmpeg), "-y",
        "-i", infile,
        "-c", "copy",
        # Allow experimental codec support like Opus and FLAC
        "-strict", "-2",
        # If present, allow subs to be transformed too
        "-c:s", "mov_text", outfile
    ]
    return call(ffmpeg_args, stdout=DEVNULL, stderr=DEVNULL)


def xfer_ended_signal_cb(data, signal, signal_data):
    weechat.infolist_next(signal_data)

    local_filename = weechat.infolist_string(signal_data, "local_filename")
    local_filepath = Path(local_filename)
    try:
        outfile = fetch_outfile(local_filepath)
    except ValueError as e:
        print(e)
        return 1

    return do_ffmpeg(local_filename, outfile)


def init_config():
    global OPTIONS
    for option, value in OPTIONS.items():
        weechat.config_set_desc_plugin(option, f"{value[1]} (default: '{value[0]}')")
        if not weechat.config_is_set_plugin(option):
            weechat.config_set_plugin(option, value[0])


if __name__ == "__main__" and import_ok:
    # Check if ffmpeg is present and pray that WeeChat handles errors properly if it isn't.
    ffmpeg = which("ffmpeg")
    if ffmpeg is None:
        raise EnvironmentError("ffmpeg could not be found on the system!")

    registered = weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION,
                                  SCRIPT_LICENSE, SCRIPT_DESC, "", "")
    if registered:
        # Don't init the config just yet
        #init_config()
        weechat.hook_signal("xfer_ended", "xfer_ended_signal_cb", "")