from pathlib import Path
import shutil
import sys
import file_parser as parser
import normalize


def handle_media(filename: Path, target_folder: Path) -> None:
    target_folder.mkdir(exist_ok=True, parents=True)
    filename.replace(target_folder / normalize(filename.name))


def handle_other(filename: Path, target_folder: Path) -> None:
    target_folder.mkdir(exist_ok=True, parents=True)
    filename.replace(target_folder / normalize(filename.name))


def handle_archive(filename: Path, target_folder: Path) -> None:
    folder_for_file = target_folder / normalize(
        filename.name.replace(filename.suffix, "")
    )
    folder_for_file.mkdir(exist_ok=True, parents=True)
    try:
        shutil.unpack_archive(str(filename.resolve()), str(folder_for_file.resolve()))
    except shutil.ReadError:
        folder_for_file.rmdir()
        return None
    filename.unlink()


def handle_folder(folder: Path) -> None:
    try:
        folder.rmdir()
    except OSError:
        print(f"Sorry, we can not delete the folder: {folder}")


def sort_dir(folder: Path) -> str:
    files = parser.scan(folder)
    for category in ["images", "audio", "video", "documents"]:
        for file in files["files"][category]:
            handle_media(file, folder / category)
    for file in files["other_files"]:
        handle_other(file, file.parent)
    for file in files["files"]["archives"]:
        handle_archive(file, folder / "archives")
    for folder in files["folders"][::-1]:
        handle_folder(folder)
    return "OK"


if __name__ == "__main__":
    folder_for_scan = Path(sys.argv[1])
    sort_dir(folder_for_scan.resolve())
