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
    from rich import print
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

    # Intialize the consoles.
    console = Console()
    err_console = Console(stderr=True, style="bold red")  # For errors.

    # Keep the original files if the option is not present.
    keeping_original: bool = args.keep

    # Get the current directory where this file is located.
    current_dir: Path = Path(__file__).parent.resolve()

    print(
        "{} -> {} {}\nCurrent directory is: {}\n".format(
            input_extension,
            output_extension,
            "[yellow](keeping the original files)" if keeping_original else "",
            current_dir,
        )
    )

    with console.status("Converting files...", spinner="dots") as status:
        # Iterating through files one by one where this file is located.
        for file in filter(
            lambda f: f.is_file(), current_dir.glob(f"*{input_extension}")
        ):
            # Emit a message for each file found.
            status.update(f'Found "{file.name}"\n')

            # This will be ffmpeg's output.
            # It might be deleted as leftover when KeyboardInterrupt raised.
            #output: Path = current_dir.joinpath(file.stem).with_suffix(output_extension)
            output: Path = file.with_suffix(output_extension)

            try:
                command: str = f'ffmpeg -i "{file.name}" "{output.name}"'

                subprocess.run(
                    command,
                    capture_output=True,
                    check=True,
                )

                # if current_dir.joinpath(output).exists() and not keeping_original:
                if output.exists() and not keeping_original:
                    # Delete the original file if the output file is created and the option is present.
                    Path.unlink(file)
                    console.log(
                        "[magenta]Done! Moving to the next candidate file.",
                        highlight=True,
                    )
                    console.log(
                        f'[magenta]The original file "{file.name}" is deleted.',
                        highlight=True,
                    )
            except subprocess.CalledProcessError as e:
                err_console.log(f'Error converting "{file.name}": {e.stderr}')
                console.log("[yellow]Keeping the original file.")
            except FileNotFoundError:
                err_console.log(
                    """The original file hasn't been found.
                    Moving to the next candidate file."""
                )
            except KeyboardInterrupt:
                status.stop()
                print("[red]Keyboard interrupt detected")
                # Ask the user if they want to keep the unfinished files.
                # By default, leftovers will be deleted.
                if not Confirm.ask(
                    "[bright_green]Do you want to keep the unfinished files?",
                    choices=["y", "n"],
                    show_choices=True,
                    show_default=True,
                    default=False,
                ):
                    print("[yellow]Deleting leftovers.")
                    for leftover in filter(
                        lambda f: f.is_file(), current_dir.glob(f"*{output_extension}")
                    ):
                        # We are looking for exact output so that the other files aren't affected.
                        if leftover == output:
                            Path.unlink(leftover)
                            status.update(f'[yellow]{output.name}" deleted.')
                print("Exiting.")
                sleep(4)
                exit()
    print("[dodger_blue1]Everything is finished. Closing.")
    sleep(3.5)


if __name__ == "__main__":
    main()
