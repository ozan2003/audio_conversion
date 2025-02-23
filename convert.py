#!/usr/bin/python3
"""
Place this file in the directory where you want it to work, then execute.

This script mass converts audio files via FFmpeg.
"""

import argparse
from sys import exit
from time import sleep
import subprocess
import re
from pathlib import Path
from shutil import which

# Check if rich is installed.
try:
    from rich import print as rprint
    from rich.prompt import Confirm
    from rich.console import Console
except ModuleNotFoundError as exc:
    exc.add_note("rich is not installed. Please install it via 'pip install rich'.")
    raise

# Check if FFmpeg is available
if not which("ffmpeg"):
    raise FileNotFoundError(
        "FFmpeg is not found. Please install it and add it to path."
    )

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
    action="store",  # store means that the value will be stored in the variable.
    nargs="?",  # number of arguments, "?" means zero or one value.
)

# Option for deleting the original files.
parser.add_argument(
    "-d",
    "--delete",
    help="Option to delete the original files.",
    action="store_true",
)

# Positional argument for the output extension.
parser.add_argument(
    "output",
    type=str,
    help="The target extension.",
    action="store",
    nargs="?",
)

# Option for printing the files that will be converted.
parser.add_argument(
    "-p",
    "--print",
    help="Print the files that will be converted.",
    action="store_true",
    nargs="?",
)


def print_files(input_ext: str, location: Path) -> None:
    """
    Prints the files that will be converted.

    Args:
        input_ext: The source file extension.
        location: The directory where the files are located.
    """

    for file in filter(lambda f: f.is_file(), location.glob(f"*{input_ext}")):
        print(file.name)


def check_extensions(input_ext: str, output_ext: str) -> tuple[str, str]:
    """
    Validates input and output file extensions.

    Args:
        input_ext: The source file extension
        output_ext: The target file extension

    Returns:
        A tuple of (input, output) extensions, each starting with a dot.

    Raises:
        ValueError: If either extension is invalid.
    """

    def clean_ext(ext: str) -> str:
        ext = ext.strip().lstrip(".") # Get the extension w/o its dot. (e.g. "mp3" from ".mp3")

        if not ext or not re.match(r"^[a-zA-Z0-9]+[a-zA-Z0-9-]*$", ext):
            raise ValueError(
                f"Invalid extension: '{ext}'. Extensions must contain only "
                "letters, numbers, and hyphens, and cannot be empty."
            )

        return f".{ext.lower()}"

    return clean_ext(input_ext), clean_ext(output_ext)


def main() -> None:
    args = parser.parse_args()  # Parse the arguments.

    input_extension, output_extension = check_extensions(args.input, args.output)

    # Intialize the console.
    console = Console()

    # Delete the original files if the option is present.
    deleting_original: bool = args.delete

    # Get the current directory where this script is located.
    current_dir: Path = Path(__file__).parent.resolve()

    # Optionally print the files that will be converted.
    if args.print:
        print_files(input_extension, current_dir)
        exit()

    # -n is for exiting if output already exists, rather than asking for overwrite.
    command: str = 'ffmpeg -n -i "{input}" "{output}"'

    rprint(
        "{} -> {} {}\nCurrent directory is: {}\n".format(
            input_extension,
            output_extension,
            "[yellow](keeping the original files)[/yellow]"
            if not deleting_original
            else "",
            current_dir,
        )
    )

    with console.status("Converting files...", spinner="dots") as status:
        # Iterating through files one by one where this file is located.
        for file in filter(
            lambda f: f.is_file(), current_dir.glob(f"*{input_extension}")
        ):
            # This will be ffmpeg's output.
            # It might be deleted as leftover when KeyboardInterrupt raised.
            output: Path = file.with_suffix(output_extension)

            # If the output file already exists, skip this file.
            if output.exists():
                status.update(f'[yellow]"{output.name}" already exists. Skipping.')
                continue

            # Emit a message for each file found.
            status.update(f'Found "{file.name}", converting...')

            try:
                subprocess.run(
                    command.format(input=file.name, output=output.name),
                    capture_output=True,
                    check=True,
                )

                # Keep this outside of the if block to log whether the we are keeping the original files or not.
                console.log("[magenta]Done! Looking for the next candidate file.")
                # if output.exists() and deleting_original:
                if deleting_original:
                    # Delete the original file if the output file is created and the option is present.
                    Path.unlink(file)
                    console.log(
                        f'[magenta]The original file "{file.name}" is deleted.',
                        highlight=True,
                    )
            except subprocess.CalledProcessError as exc:
                console.log(f'[bold red]Error converting "{file.name}"[/bold red]')
                rprint(exc.stderr, file=open("error.log", "a"))
                console.log("[yellow]Keeping the original file.")
            except FileNotFoundError:
                console.log("[bold red]The original file hasn't been found.[/bold red]")
            except KeyboardInterrupt:
                status.stop()
                rprint("[red]Keyboard interrupt detected")
                # Ask the user if they want to keep the unfinished files.
                # By default, leftovers will be deleted.
                if not Confirm.ask(
                    "[bright_green]Do you want to keep the unfinished files?",
                    choices=["y", "n"],
                    show_choices=True,
                    show_default=True,
                    default=False,
                ):
                    rprint("[yellow]Deleting leftovers.")
                    for leftover in filter(
                        lambda f: f.is_file(), current_dir.glob(f"*{output_extension}")
                    ):
                        # We are looking for exact output so that the other files aren't affected.
                        if leftover == output:
                            Path.unlink(leftover)
                            status.update(f'[yellow]{output.name}" deleted.')
                rprint("Exiting.")
                sleep(4)
                exit()
    rprint("[dodger_blue1]Everything is finished. Closing.")
    sleep(3.5)


if __name__ == "__main__":
    main()
