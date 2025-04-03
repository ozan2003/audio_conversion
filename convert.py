#!/usr/bin/python3
"""
Place this file in the directory where you want it to work, then execute.

This script mass converts audio files via FFmpeg.
"""

import argparse
import re
import subprocess
from pathlib import Path
from shutil import which
from sys import exit as sys_exit
from time import sleep

# Check if rich is installed.
try:
    from rich import print as rprint
    from rich.console import Console
    from rich.prompt import Confirm
    from rich.status import Status
except ModuleNotFoundError as exc:
    exc.add_note("rich is not installed. Please install it via 'pip install rich'.")
    raise

# Check if FFmpeg is available
if not which("ffmpeg"):
    msg = "FFmpeg is not found. Please install it and add it to path."
    raise FileNotFoundError(
        msg,
    )

# -n is for exiting if output already exists, rather than asking for overwrite.
ffmpeg_command: str = 'ffmpeg -n -i "{input}" "{output}"'


def main() -> None:
    parser = setup_argparser()
    args = parser.parse_args()

    # Get the current directory where this script is located.
    current_dir: Path = Path(__file__).parent.resolve()

    # Sanitize the input and output extensions.
    input_extension: str = check_extension(args.input)

    # Optionally print the files that will be converted.
    if args.print:
        # We are not converting anything, so we don't need to check the output extension.
        print_files(input_extension, current_dir)
        sys_exit()

    # We can check the output extension here.
    output_extension: str = check_extension(args.output)

    # Delete the original files if the option is present.
    deleting_original: bool = args.delete

    # Intialize the console.
    console = Console()

    rprint(
        "{} -> {} {}\nCurrent directory is: {}\n".format(
            input_extension,
            output_extension,
            "[yellow](keeping the original files)[/yellow]"
            if not deleting_original
            else "",
            current_dir,
        ),
    )

    with console.status("Converting files...", spinner="dots") as status:
        # Iterating through files one by one where this file is located.
        for input_file in filter(
            lambda f: f.is_file(),
            current_dir.glob(f"*{input_extension}"),
        ):
            # This will be ffmpeg's output.
            # It might be deleted as leftover when KeyboardInterrupt raised.
            output_file: Path = input_file.with_suffix(output_extension)

            # If the output file already exists, skip this file.
            if output_file.exists():
                status.update(f'[yellow]"{output_file.name}" already exists. Skipping.')
                continue

            # Emit a message for each file found.
            status.update(f'Found "{input_file.name}", converting...')

            try:
                subprocess.run(  # noqa: S602
                    ffmpeg_command.format(
                        input=input_file.name, output=output_file.name
                    ),
                    shell=True,
                    capture_output=True,
                    check=True,
                )

                # Keep this outside of the if block to log whether the we are keeping the original files or not.
                console.log("[magenta]Done! Looking for the next candidate file.")
                # if output.exists() and deleting_original:
                if deleting_original:
                    # Delete the original file if the output file is created and the option is present.
                    Path.unlink(input_file)
                    console.log(
                        f'[magenta]The original file "{input_file.name}" is deleted.',
                        highlight=True,
                    )
            except subprocess.CalledProcessError as exc:
                console.log(
                    f'[bold red]Error converting "{input_file.name}"[/bold red]'
                )
                with Path("error.log").open("a", encoding="utf-8") as error_file:
                    rprint(exc.stderr, file=error_file)
                console.log("[yellow]Keeping the original file.")
            except FileNotFoundError:
                console.log("[bold red]The original file hasn't been found.[/bold red]")
            except KeyboardInterrupt:
                handle_keyboard_interrupt(
                    current_dir, status, output_extension, output_file
                )
    rprint("[dodger_blue1]Everything is finished. Closing.")
    sleep(3.5)


def setup_argparser() -> argparse.ArgumentParser:
    """
    Set up the argument parser for the script.
    Argument parser will be created inside this function.

    Returns:
        argparse.ArgumentParser: The argument parser object.

    """
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
        help="Print the files to be converted.",
        action="store_true",
    )

    return parser


def print_files(input_ext: str, location: Path) -> None:
    """
    Prints the files that will be converted.

    Args:
        input_ext: The source file extension.
        location: The directory where the files are located.

    """
    for file in filter(lambda f: f.is_file(), location.glob(f"*{input_ext}")):
        print(file.name)  # noqa: T201


def check_extension(extension: str) -> str:
    """
    Check if the extension is valid.

    Args:
        extension: The extension to be checked.

    Returns:
        str: The sanitized extension.

    Raises:
        ValueError: If either extension is invalid.

    """

    def clean_ext(ext: str) -> str:
        # Get the extension w/o its dot. (e.g. "mp3" from ".mp3")
        ext = ext.strip().lstrip(".")

        if not ext or not re.match(r"^[a-zA-Z0-9]+[a-zA-Z0-9-]*$", ext):
            msg = (
                f"Invalid extension: '{ext}'. Extensions must contain only "
                "letters, numbers, and hyphens, and cannot be empty."
            )
            raise ValueError(
                msg,
            )

        return f".{ext.lower()}"

    return clean_ext(extension)


def handle_keyboard_interrupt(
    current_dir: Path, status: Status, output_extension: str, output_file: Path
) -> None:
    """
    Handle KeyboardInterrupt gracefully.

    Args:
        current_dir: The directory where the files are located.
        status: The status object to update.
        output_extension: The output file extension.
        output_file: The output file to delete if needed.

    """
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
            lambda f: f.is_file(),
            current_dir.glob(f"*{output_extension}"),
        ):
            # We are looking for exact output so that the other files aren't affected.
            if leftover == output_file:
                Path.unlink(leftover)
                status.update(f'[yellow]{output_file.name}" deleted.')
    rprint("Exiting.")
    sleep(4)
    sys_exit()


if __name__ == "__main__":
    main()
