import argparse
import json
import random
import re
import time

from configs import Config
from crawler import GuShiWen, get_detail_page
from utils import ensure_folder
from web import do_get_plain, create_worker

page_root = "https://so.gushiwen.cn/"

source_pages = [
    "/gushi/tangshi.aspx",
    "/shiwens/default.aspx?xstr=诗&cstr=宋代",
    "/gushi/sanbai.aspx",
    "/gushi/songsan.aspx",
    "/gushi/xiaoxue.aspx",
    "/gushi/chuzhong.aspx",
    "/gushi/gaozhong.aspx",
]

# <span><a href="/shiwenv_4c7868ec4409.aspx" target="_blank">燕歌行</a>(高适)</span>
PATTERN_MATCH_HREF = re.compile(
    r'<span><a href="(?P<url>.*)" target="_blank">(?P<title>.*)</a>\((?P<author>.*)\)</span>'
)
PATTERN_MATCH_COMBINE = re.compile(r"(/shiwenv_.*.aspx)")


def fire(pack):
    poem_idx, poem_data = pack
    if store.joinpath("{:05d}.json".format(poem_idx)).exists():
        return 1

    page_url = poem_data["url"]

    get = get_detail_page(page_url, driver, judge_poem=True)

    if get:
        save_target = store.joinpath("{:05d}.json".format(poem_idx))
        with open(save_target, "w") as save_f:
            json.dump(get, save_f, ensure_ascii=False, indent=4)
        return 1
    else:
        return 0


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--wait_min", type=float, default=0.2)
    parser.add_argument("--wait_max", type=float, default=0.5)
    return parser


if __name__ == "__main__":
    # store = Config.store_root.joinpath("other-poem")
    store = Config.page_root
    ensure_folder(store)

    container = []
    for page in source_pages:
        print("> crawling `{}`...".format(page), end="")
        url = GuShiWen.combine_url(page)
        html_text = do_get_plain(url)
        ret = re.finditer(PATTERN_MATCH_HREF, html_text)
        for idx, group in enumerate(ret):
            d = group.groupdict()
            cut_url = re.search(PATTERN_MATCH_COMBINE, d["url"])
            if cut_url:
                d["url"] = cut_url.group()
                container.append(d)
        print(" => {}".format(len(container)))

    container = [(i, e) for i, e in enumerate(container)]
    num_urls = len(container)

    args = get_parser().parse_args()
    T_min = args.wait_min
    T_max = args.wait_max
    start_at = 0

    driver = create_worker("safari")

    num_success = 0
    num_total = 0
    for e in container[start_at:]:
        num_success += fire(e)
        num_total += 1
        print("{} / {} / {}".format(num_success, num_total, num_urls))
        time.sleep(random.uniform(T_min, T_max))

    driver.close()
