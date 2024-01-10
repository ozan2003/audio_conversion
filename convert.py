# Place this file in the directory where you want it to work, then execute.
# FFmpeg must be present and added to path.
import argparse
from sys import exit
import os
from time import sleep
import subprocess
import re

def main():
    # argparse allows us to communicate the program via terminal.
    parser = argparse.ArgumentParser(
        description="Convert audio files via FFmpeg.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,  # show the default values in description.
    )

    # Positional argument for the input extension.
    parser.add_argument(
        "input",  # this argument denotes a positional argument since it doesn't have - or --.
        type=str,
        help="The extension of the files to be converted.",
        default="webm",
        action="store",  # store means that the value will be stored in the variable.
        nargs="?",  # number of arguments, "?" means zero or one value.
    )

    # Option for keeping the original files.
    parser.add_argument(
        "-k",
        "--keep",
        help="Option to keep the original files.",
        action="store_true",  # store_true means that if the option is present, it will be True.
    )

    # Positional argument for the output extension.
    parser.add_argument(
        "output",
        type=str,
        help="The target extension.",
        action="store",
        default="mp3",
        nargs="?",
    )

    # Parse the arguments.
    args = parser.parse_args()

    input_extension: str = "." + args.input  # Don't forget the dot.

    # Check if the input extension format is valid.
    # Input and output extension must be comprised of letters and numbers.
    if not re.match(r"\.[a-zA-Z0-9]+", input_extension):
        print("Invalid input extension.")
        exit()

    output_extension: str = "." + args.output  # Don't forget the dot.

    # Check if the output extension format is valid.
    if not re.match(r"\.[a-zA-Z0-9]+", input_extension):
        print("Invalid output extension.")
        exit()

    keeping_original: bool = (
        args.keep
    )  # Keep the original files if the option is not present.

    """ __file__ is a special variable that represents the path of the current script being executed. 
        It might not be always absolute."""
    # Use os.path.abspath() which returns the absolute path of the current script to be sure.
    # os.path.dirname() returns the directory in which the code file is stored.
    """ This method relies on clicking on the file; it won't work if the command line is used from somewhere else.
        Use os.getcwd() for command-line usage."""
    current_dir = os.path.dirname(os.path.abspath(__file__))

    print(
        f"""{input_extension} -> {output_extension} {"(keeping the original files)" if keeping_original else ""}
    Current directory is: {current_dir}."""
    )


    # Iterating through files one by one where this file is located.
    for file in filter(
        lambda f: f.endswith(input_extension) and os.path.isfile(os.path.abspath(f)),
        os.listdir(current_dir),
    ):
        print(f'=> Found "{file}", converting to "{output_extension}".\n')

        # Take only the file's name and remove any leading and trailing white-spaces.
        """ This will be ffmpeg's output.
            It might be deleted as leftover when KeyboardInterrupt raised."""
        output = file[: file.rfind(".")].strip() + output_extension

        try:
            command = f'ffmpeg -i "{file}" "{output}"'

            subprocess.run(
                command,
                shell=True,
                capture_output=True,
                check=True,
            )

            print("Done! Moving to the next candidate file.")

            if os.path.exists(os.path.join(current_dir, output)) and not keeping_original:
                # Delete the original file if the output file is created and the option is present.
                os.remove(file)
                print(f'The original file "{file}" is deleted.')
        except subprocess.CalledProcessError as e:
            print(
                f"Something went wrong while converting, return code is {e.returncode}.\n"
            )
            print(f'ffmpeg error: "{e.stderr}".\n')
            print("Keeping the original file and moving to the next candidate file.")
        except FileNotFoundError:
            print("The original file hasn't been found.\n")
            print("Moving to the next candidate file.")
        except KeyboardInterrupt:
            print("Keyboard interrupt detected.\n")
            # Ask the user if they want to keep the unfinished files.
            # We are looking for the input's first letter so that it covers "yes", "y", "yea", etc. too.
            if input("Do you want to keep the unfinished files? (y/n) ")[0].lower() == "y":
                print("\nDeleting leftovers.")
                for leftover in os.listdir(current_dir):
                    # We are looking for exact output so that the other files aren't affected.
                    if leftover == output:
                        os.remove(leftover)
                        print(f'"{output}" deleted.')
            print("\nExiting.")
            sleep(2)
            exit()
        finally:
            print("-" * 65)
    print("Everything is finished. Closing.")
    sleep(1.5)

if __name__ == "__main__":
    main()