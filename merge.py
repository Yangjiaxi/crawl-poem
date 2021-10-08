import os
import pprint
import re
from itertools import chain
from pathlib import Path

from crawler import do_judge, GuShiWen
from utils import random_string, ensure_folder, match_and_trim, remove_p, PUNCTUATION_ZH

try:
    import ujson as json
except ImportError:
    import json

from configs import Config


PATH_SET = [Config.five_root, Config.seven_root, Config.tang_root, Config.page_root]
# PATH_SET = [Config.store_root.joinpath("test")]


def read_json(file: Path):
    with open(file, "r") as f:
        a = json.load(f)
    return a


def process_content(content):
    pairs = [{"text": line["text"], "poem": remove_p(line["poem"])} for line in content]
    processed = []
    for pair in pairs:
        t_poem, t_text = pair["poem"], pair["text"]
        poem_split = re.split(PUNCTUATION_ZH, t_poem)
        poem_split = list(filter(lambda s: len(s), poem_split))

        if len(poem_split) > 2:
            if not all([len(t) == len(poem_split[0]) for t in poem_split]):
                continue  # ignore first line, not the content of a poem

            cut_poem = re.findall(PUNCTUATION_ZH, t_poem)[1::2]

            poem_start, text_start = 0, 0
            for cut in cut_poem:
                poem_pos = t_poem.find(cut, poem_start) + 1
                sub_poem = t_poem[poem_start:poem_pos]
                poem_start = poem_pos

                text_pos = t_text.find(cut, text_start) + 1
                sub_text = t_text[text_start:text_pos]
                text_start = text_pos

                processed.append({"poem": sub_poem, "text": sub_text})
        else:
            processed.append({"poem": t_poem, "text": t_text})

    return processed


def walk_dir(folder: Path):
    collection = []
    for file in folder.iterdir():
        if file.suffix == ".json":
            dirty = read_json(file)
            if not do_judge(dirty["content"], len_test=[5, 7]):
                continue

            clean = {
                "title": "".join(match_and_trim(GuShiWen.GET_CHINESE_PATTERN, dirty["title"])),
                "author": "".join(match_and_trim(GuShiWen.GET_CHINESE_PATTERN, dirty["author"])),
                "dynasty": dirty["dynasty"],
                "content": process_content(dirty["content"]),
            }
            collection.append(clean)
    return collection


if __name__ == "__main__":
    ensure_folder(Config.merge_root)
    if len(list(Config.merge_root.iterdir())) == 0:
        full_collection = []
        for path in PATH_SET:
            dir_collection = walk_dir(path)
            full_collection.extend(dir_collection)

        print("Full: ", len(full_collection))

        washed = {(v["title"], v["author"], v["dynasty"], v["content"][0]["poem"]): v for v in full_collection}.values()
        print("P-K: ", len(washed))

        _washed = list(filter(lambda e: do_judge(e["content"], len_test=[5, 7]), washed))
        print("Judge: ", len(washed))

        for poem in _washed:
            name = Config.merge_root.joinpath("{}.json".format(random_string(5)))
            while name.exists():
                name = Config.merge_root.joinpath("{}.json".format(random_string(5)))

            with open(name, "w") as f:
                json.dump(poem, f, ensure_ascii=False, indent=4)

    elif not Config.merge_file.exists():
        washed = walk_dir(Config.merge_root)
        with open(Config.merge_file, "w") as f:
            json.dump(washed, f, ensure_ascii=False, indent=2)

    else:  # result/merge.json exist
        pass
