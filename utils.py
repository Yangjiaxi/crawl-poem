import random
import re
import string
from pathlib import Path

PUNCTUATION_ZH = r"[\u3002|\uff1f|\uff01|\uff0c|\u3001|\uff1b|\uff1a|\u201c|\u201d|\u2018|\u2019|\uff08|\uff09|\u300a|\u300b|\u3008|\u3009|\u3010|\u3011|\u300e|\u300f|\u300c|\u300d|\ufe43|\ufe44|\u3014|\u3015|\u2026|\u2014|\uff5e|\ufe4f|\uffe5]"


def ensure_folder(folder):
    folder = Path(folder)
    if not folder.is_dir():
        folder.mkdir()


def ensure_file(path_to_file):
    path = Path(path_to_file)
    folder_path = path.parent
    ensure_folder(folder_path)
    if not path.exists():
        path.touch(exist_ok=False)

    return path


def match_and_trim(pat, text):
    match = re.findall(pat, text)
    match = [text.strip() for text in match]
    return match


def random_string(n=5):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


def remove_p(text):
    return re.sub(r"\([^)]*\)", "", text)


def count_with_suffix(path: Path, suffix: str):
    if not path.exists():
        return 0
    if not path.is_dir():
        return 0

    return sum([1 if file.suffix == suffix else 0 for file in path.iterdir()])
