#!python
"""
Place this file in the directory where you want it to work, then execute.
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
    default="webm",
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
    default="mp3",
    nargs="?",
)


def check_extensions(*extensions: str) -> tuple[str, ...]:
    """
    Checks the validity of the extensions given.

    The extensions should be started with a dot,
    can be of any length, and can contain only
    alphanumeric characters.

    Args:
       *extensions: str: The extensions to be checked.

    Returns:
       A tuple comprised of extensions.

    Raises:
       RuntimeError: If any of the extensions are invalid.
    """
    pattern: str = r"^\.[a-zA-Z0-9]+$"

    for extension in extensions:
        if not re.match(pattern, extension):
            raise RuntimeError(
                f"Invalid extension for {extension!r}. Please check your input."
            )

    return extensions


def main() -> None:
    args = parser.parse_args()  # Parse the arguments.

    # Don't forget the dots.
    input_extension, output_extension = check_extensions(
        "." + args.input, "." + args.output
    )

    # Intialize the console.
    console = Console()

    # Delete the original files if the option is present.
    deleting_original: bool = args.delete

    # Get the current directory where this script is located.
    current_dir: Path = Path(__file__).parent.resolve()

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
                # -n is for exiting if output already exists, rather than asking for overwrite.
                command: str = f'ffmpeg -n -i "{file.name}" "{output.name}"'

                subprocess.run(
                    command,
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
