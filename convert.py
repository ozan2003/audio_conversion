# Place this file in the directory where you want it to work, then execute.
# FFmpeg must be present and added to path.
import os
import subprocess
from time import sleep
from sys import exit
import argparse

parser = argparse.ArgumentParser(
    description="Convert audio files via FFmpeg.",
    epilog="Remember to include the period at the beginning of the extension.",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter # show the default values in description.
)

parser.add_argument(
    "input",  # this argument denotes a positional argument since it doesn't have - or --.
    type=str,
    help="The extension of the files to be converted.",
    default=".webm",
    nargs="?" # number of arguments, "?" means zero or one value.
)

parser.add_argument(
    "output",
    type=str,
    help="The target extension.",
    default=".mp3",
    nargs="?"
)

input_extension = parser.parse_args().input
output_extension = parser.parse_args().output

# Use os.path.abspath() which returns the absolute path of the current script to be sure.
# os.path.dirname() returns the directory in which the code file is stored.
""" This method relies on clicking on the file; it won't work if the command line is used from somewhere else.
    Use os.getcwd() for command-line usage."""
current_dir = os.path.dirname(os.path.abspath(__file__))

print(f"Current directory is: {current_dir}\n")

# Iterating through files.
for file in filter(
    lambda f: f.endswith(input_extension) and os.path.isfile(os.path.abspath(f)),
    os.listdir(current_dir)
):
    print(f'Found "{file}"! Converting to "{output_extension}".\n')

    # Take only the file's name and remove any leading and trailing white-spaces.
    """ This will be ffmpeg's output.
        It might be deleted as leftover when KeyboardInterrupt raised."""
    output = file[:file.rfind(".")].strip() + output_extension

    try:
        subprocess.run(
            f'ffmpeg -i "{file}" "{output}"',
            shell=True,
            capture_output=True,
            check=True
        )

        print("Done! Moving to the next candidate file.")

        if os.path.exists(os.path.join(current_dir, output)):
            # If everything went okay, remove the original file with input_extension.
            os.remove(file)
            print(f'The original file "{file}" is deleted.')
    except subprocess.CalledProcessError as e:
        print(f"Something went wrong while converting, return code is {e.returncode}.\n")
        print(f'ffmpeg error: "{e.stderr}".\n')
        print("Keeping the original file and moving to the next candidate file.")
    except FileNotFoundError:
        print("The original file hasn't been found.\n")
        print("Moving to the next candidate file.")
    except KeyboardInterrupt:
        print("Keyboard interrupt detected.\n")
        # Ask the user if they want to keep the unfinished files.
        # We are looking for the input's first letter so that it covers "yes", "y", "yea", etc. too.
        if (
            input(f'Delete leftover "{output_extension}" files created? (y/n) ')[0]
            .lower()
            == "y"
        ):
            print("\nDeleting leftovers.")
            for leftover in os.listdir(current_dir):
                # We are looking for exact output so that the other files aren't affected.
                if leftover == output:
                    os.remove(leftover)
                    print(f'"{output}" deleted.')
        print("\nExiting.")
        sleep(2)
        exit()

    print("------------------------------------------------------------------\n")

print("Everything is finished. Closing.")
sleep(1.5)
