import sys
from pathlib import Path

CATEGORIES = {
    'images': ['jpeg', 'jpg', 'png', 'svg'],
    'audio': ['mp3', 'ogg', 'wav', 'amr'],
    'video': ['avi', 'mp4', 'mov', 'mkv'],
    'documents': ['doc', 'docx', 'txt', 'pdf', 'xlsx', 'pptx'],
    'archives': ['zip', 'gz', 'tar']
}


def get_extension(filename: str) -> str:
    return Path(filename).suffix[1:].lower()


def scan_folder(folder: Path, files: dict) -> None:
    for item in folder.iterdir():
        if item.is_dir():
            if item.name not in ('archives', 'video', 'audio', 'documents', 'images', 'other'):
                files["folders"].append(item)
                scan_folder(item, files)
            continue
        ext = get_extension(item.name)
        full_name = folder / item.name
        if not ext:
            files['other_files'].append(full_name)
        else:
            if ext in files['files_by_extension']:
                container = files['files_by_extension'][ext]
                files['extensions'].add(ext)
                container.append(full_name)
            else:
                files['unknown_extensions'].add(ext)
                files['other_files'].append(full_name)


def scan(folder: Path):
    files_by_category = dict((category, []) for category in CATEGORIES)
    files_by_extension = {}
    for category, extensions in CATEGORIES.items():
        for extension in extensions:
            files_by_extension[extension] = files_by_category[category]
    files = {
        "files": files_by_category,
        "files_by_extension": files_by_extension,
        "extensions": set(),
        "folders": [],
        "unknown_extensions": set(),
        "other_files": [],
    }
    scan_folder(folder, files)
    return files


if __name__ == '__main__':
    folder_for_scan = sys.argv[1]
    print(f'Start in folder: {folder_for_scan}')
    folder_files = scan(Path(folder_for_scan))
    print(folder_files)
