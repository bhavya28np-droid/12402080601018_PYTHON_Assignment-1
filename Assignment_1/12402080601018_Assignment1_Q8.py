
"""
Q8: Compressed Log Index using Pickle and ZIP
Python 3.10+

BUILD: Create an inverted index and ZIP archive.
SEARCH: Find all file and line locations for query tokens.
"""

import os
import re
import pickle
import zipfile
from pathlib import Path
from collections import defaultdict


TOKEN_PATTERN = re.compile(r"\b[a-zA-Z0-9_]+\b")


def tokenize(text):
    """Extract lowercase tokens from a line."""
    return {
        token.lower()
        for token in TOKEN_PATTERN.findall(text)
        if len(token) <= 50
    }


def build_index(folder_path, zip_path):
    """Build the inverted index and compress source files."""

    folder = Path(folder_path).resolve()
    archive_path = Path(zip_path).resolve()

    if not folder.is_dir():
        raise ValueError("The specified folder does not exist.")

    if archive_path.suffix.lower() != ".zip":
        raise ValueError("The output archive must have a .zip extension.")

    if archive_path.exists() and archive_path.is_dir():
        raise ValueError("The ZIP output path is a directory.")

    # Keep the index beside the requested ZIP archive.
    index_path = archive_path.with_suffix(".pkl")

    if index_path == archive_path:
        raise ValueError("Choose a valid archive filename.")

    # Collect source files recursively, excluding generated outputs.
    source_files = sorted(
        path for path in folder.rglob("*")
        if path.is_file()
        and path.resolve() not in {
            archive_path,
            index_path.resolve(),
        }
        and "__pycache__" not in path.parts
    )

    # token -> list of (relative file path, line number)
    inverted_index = defaultdict(list)
    total_lines = 0

    for file_path in source_files:
        relative_name = file_path.relative_to(folder).as_posix()

        try:
            with file_path.open(
                "r", encoding="utf-8", errors="replace"
            ) as file:
                for line_number, line in enumerate(file, start=1):
                    total_lines += 1

                    # One posting per token per line.
                    for token in sorted(tokenize(line)):
                        inverted_index[token].append(
                            (relative_name, line_number)
                        )

        except OSError as error:
            raise OSError(
                f"Could not read {relative_name}: {error}"
            ) from error

    # Save the index in binary pickle format.
    with index_path.open("wb") as file:
        pickle.dump(dict(inverted_index), file,
                    protocol=pickle.HIGHEST_PROTOCOL)

    # Compress the source files into a ZIP archive.
    archive_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(
        archive_path, "w", compression=zipfile.ZIP_DEFLATED
    ) as archive:
        for file_path in source_files:
            archive.write(
                file_path,
                arcname=file_path.relative_to(folder).as_posix(),
            )

    print("\nBUILD completed successfully.")
    print(f"Total files: {len(source_files)}")
    print(f"Total lines: {total_lines}")
    print(f"Unique tokens: {len(inverted_index)}")
    print(f"Index saved: {index_path}")
    print(f"ZIP archive saved: {archive_path}")


def search_index(index_path, query_tokens):
    """Load a saved index and search for tokens."""

    path = Path(index_path)

    if not path.is_file():
        raise ValueError("Pickle index file not found.")

    # Only load pickle files that you trust.
    with path.open("rb") as file:
        inverted_index = pickle.load(file)

    if not isinstance(inverted_index, dict):
        raise ValueError("Invalid index file format.")

    for token in query_tokens:
        normalized_token = token.lower()

        print(f"\n{normalized_token}:")

        matches = inverted_index.get(normalized_token, [])

        if not matches:
            print("No matches found.")
            continue

        for file_name, line_number in sorted(set(matches)):
            print(f"{file_name}:{line_number}")


def main():
    print("=" * 50)
    print("       COMPRESSED LOG INDEX")
    print("=" * 50)
    print("1. BUILD - Create index and ZIP archive")
    print("2. SEARCH - Search an existing index")

    while True:
        mode = input("\nChoose mode (BUILD/SEARCH): ").strip().upper()

        if mode in ("BUILD", "SEARCH"):
            break

        print("Please enter BUILD or SEARCH.")

    try:
        if mode == "BUILD":
            folder = input("Enter source folder path: ").strip().strip('"')
            zip_name = input(
                "Enter output ZIP path (e.g. archive.zip): "
            ).strip().strip('"')

            build_index(folder, zip_name)

        else:
            index_path = input(
                "Enter pickle index path (e.g. archive.pkl): "
            ).strip().strip('"')

            query_input = input(
                "Enter query tokens separated by spaces: "
            ).strip()

            query_tokens = query_input.split()

            if not query_tokens:
                print("Please enter at least one query token.")
                return

            search_index(index_path, query_tokens)

    except (OSError, ValueError, pickle.UnpicklingError,
            EOFError) as error:
        print(f"\nError: {error}")
    except KeyboardInterrupt:
        print("\nProgram stopped by user.")


if __name__ == "__main__":
    main()
