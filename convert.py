# Place this file in the directory where you want it to work, then execute.
# FFmpeg must be present and added to path.
import argparse
from sys import exit
from time import sleep
import subprocess
import re
from pathlib import Path


# An exception for invalid inputs.
class InvalidInput(Exception):
    pass


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


def main() -> None:
    args = parser.parse_args()  # Parse the arguments.

    input_extension: str = "." + args.input  # Don't forget the dot.

    # Check if the input extension format is valid.
    if not re.match(r"\.[a-zA-Z0-9]+", input_extension):
        raise InvalidInput("Invalid input extension. Please check your input.")

    output_extension: str = "." + args.output  # Don't forget the dot.

    # Check if the output extension format is valid.
    # Input must be comprised of letters and numbers.
    if not re.match(r"\.[a-zA-Z0-9]+", input_extension):
        raise InvalidInput("Invalid output extension. Please check your input.")

    # Keep the original files if the option is not present.
    keeping_original: bool = args.keep

    # Get the current directory where this file is located.
    current_dir: Path = Path(__file__).parent.resolve()

    print(
        f"""{input_extension} -> {output_extension} {"(keeping the original files)" if keeping_original else ""}
Current directory is: {current_dir}.\n"""
    )

    # Iterating through files one by one where this file is located.
    for file in filter(lambda f: f.is_file(), current_dir.glob(f"*{input_extension}")):
        print(f'=> Found "{file.name}", converting to "{output_extension}".\n')

        # Take only the file's name and remove any leading and trailing white-spaces.
        """ This will be ffmpeg's output.
            It might be deleted as leftover when KeyboardInterrupt raised."""
        output: Path = current_dir.joinpath(file.stem.strip() + output_extension)

        try:
            command: str = f'ffmpeg -i "{file.name}" "{output.name}"'

            subprocess.run(
                command,
                capture_output=True,
                check=True,
            )

            print("Done! Moving to the next candidate file.")

            if current_dir.joinpath(output).exists() and not keeping_original:
                # Delete the original file if the output file is created and the option is present.
                Path.unlink(file)
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
            if (
                input("Do you want to keep the unfinished files? (y/n) ")[0].lower()
                == "y"
            ):
                print("\nDeleting leftovers.")
                for leftover in filter(
                    lambda f: f.is_file(), current_dir.glob(f"*{output_extension}")
                ):
                    # We are looking for exact output so that the other files aren't affected.
                    if leftover == output:
                        Path.unlink(leftover)
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
