@echo off
CHCP 65001
REM The first line makes CMD not print every line of this script
REM The tilde (~) makes it remove quotes from input arguments
SET readdir=%~1
SET delvar=%~2
REM Get the first letter of the second argument given
REM This gets checked in the loop
SET yeet=%delvar:~0,1%
REM Delete any file still present from a failed or manual run
DEL /F D:\files.txt
REM Check if the thing ends in a backslash for paths
IF NOT %readdir:~-1,1% == "\" (
    REM If it doesn't end with a backslash, add it because CMD is retarded
    SET readdir=%readdir%\
)
REM Save all files from the input directories to a file
DIR /S /B "%readdir%*.mkv" 2>NUL 1>>D:\Files.txt
REM For every file there, run the ffmpeg commands and then delete intermediary steps
FOR /F "tokens=*" %%F in (D:\files.txt) DO (
    ffmpeg -i "%%F" -map 0:a:0 -f wav -ar 48000 -b:a 320k - | qaac - -V 127 --adts -r auto --ignorelength -o - | ffmpeg -i "%%F" -i - -map_metadata 0 -map 0:v -map 1:a -map 0:s? -map 0:t? -map 0:b? -codec copy "%%~dpFtranscoded\%%~nF"
    IF /I "%yeet%" == "y" (
        echo Deleting "%%F"
        DEL /F "%%F"
)
echo All done!!
