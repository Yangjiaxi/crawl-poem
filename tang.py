import argparse
import random
import time

from configs import Config
from crawler import try_gushiwen
from utils import ensure_folder, count_with_suffix
from web import create_worker

try:
    import ujson as json
except ImportError:
    import json


def fire(pack):
    idx, info = pack
    if Config.tang_root.joinpath("{:05d}.json".format(idx)).exists():
        return 1

    text_list = info["paragraphs"].split("$")
    get = try_gushiwen(text_list, driver)

    if get:
        save_target = Config.tang_root.joinpath("{:05d}.json".format(idx))
        with open(save_target, "w") as save_f:
            json.dump(get, save_f, ensure_ascii=False, indent=4)
        return 1
    else:
        return 0


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--l", type=int, default=5913)
    parser.add_argument("--r", type=int, default=-1)
    parser.add_argument("--wait_min", type=float, default=0)
    parser.add_argument("--wait_max", type=float, default=0.3)
    return parser


if __name__ == "__main__":
    with open(Config.tang_poem_file) as f:
        json_poem = json.load(f)
    num_poems = len(json_poem)
    json_poem = [(idx, d) for idx, d in enumerate(json_poem)]
    ensure_folder(Config.tang_root)

    driver = create_worker("safari")

    args = get_parser().parse_args()
    start_at = args.l
    stop_at = args.r if args.r > 0 else num_poems
    T_min = args.wait_min
    T_max = args.wait_max

    num_success = count_with_suffix(Config.tang_root, ".json")
    num_total = start_at
    for e in json_poem[start_at:stop_at]:
        num_success += fire(e)
        num_total += 1
        print("{} / {} / {}".format(num_success, num_total, num_poems))
        time.sleep(random.uniform(T_min, T_max))

    driver.close()
