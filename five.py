import argparse
import random
import re
import time

from configs import Config
from crawler import try_gushiwen
from utils import ensure_folder, PUNCTUATION_ZH
from web import create_worker

try:
    import ujson as json
except ImportError:
    import json


def fire(pack):
    idx, text_list = pack
    if Config.five_root.joinpath("{:05d}.json".format(idx)).exists():
        return 1

    get = try_gushiwen(text_list, driver)
    # driver.close()

    if get:
        save_target = Config.five_root.joinpath("{:05d}.json".format(idx))
        with open(save_target, "w") as save_f:
            json.dump(get, save_f, ensure_ascii=False, indent=4)
        return 1
    else:
        return 0


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--wait_min", type=float, default=0.0)
    parser.add_argument("--wait_max", type=float, default=0.2)
    return parser


if __name__ == "__main__":
    args = get_parser().parse_args()

    with open(Config.five_poem_file) as f:
        poems = f.readlines()
    ensure_folder(Config.five_root)

    poems = [text.strip() for text in poems]

    poem_text = []
    for i in range(len(poems)):
        if (i + 1 - 2) % 3 == 0:
            poem = poems[i]
            res = re.split(PUNCTUATION_ZH, poem)
            res = list(filter(lambda s: len(s) > 0, res))
            poem_text.append(res)

    T_min = args.wait_min
    T_max = args.wait_max

    json_poem = [(idx, d) for idx, d in enumerate(poem_text)]
    driver = create_worker("safari")

    num_success = 0
    num_total = 0
    for e in json_poem:
        num_success += fire(e)
        num_total += 1
        print("{} / {}".format(num_success, num_total))
        time.sleep(random.uniform(T_min, T_max))

    driver.close()
