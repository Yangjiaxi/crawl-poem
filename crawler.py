import re
from collections import Counter
from itertools import chain
from string import Template

from utils import match_and_trim, PUNCTUATION_ZH, remove_p
from web import do_get_driver


class GuShiWen:
    GUSHIWEN_QUERY = Template("https://so.gushiwen.cn/search.aspx?value=$kw")
    TRANSLATION_QUERY = Template("https://so.gushiwen.cn/nocdn/ajaxshiwencont.aspx?id=$poemid&value=yi")

    GET_CHINESE_PATTERN = re.compile(r"([\u4e00-\u9fa5])")
    GET_TITLE_PATTERN = re.compile(r"font-size:18px; line-height:22px; height:22px;.*\n(.*)")
    GET_AUTHOR_PATTERN = re.compile(r'<p class="source"><a target="_blank".*\n(.*)\n.*<a href.*>(.*)</a>')
    GET_ID_PATTERN = re.compile(r"OnYiwen\('(.*)'\)")
    GET_ID_HAS_TRANSLATION_PATTERN = re.compile(r'getElementById\("btnYiwen(.*)"\)\.style\.display')
    GET_POEM_TRANSLATION_PATTERN = re.compile(r'<p>(.+)<br.*">(.*?)<.*></p>')

    PAGE_WORK = Template("https://so.gushiwen.cn$concat")
    GET_TITLE_IN_PAGE_PATTERN = re.compile(r'line-height:22px; height:22px; margin-bottom:10px;">(.*)</h1>')
    GET_AUTHOR_IN_PAGE_PATTERN = re.compile(r'source"><a.*>(.*)</a>.*>(.*)</a>')

    @staticmethod
    def combine_url(concat):
        return GuShiWen.PAGE_WORK.substitute(concat=concat)

    @staticmethod
    def get_search(kw):
        return GuShiWen.GUSHIWEN_QUERY.substitute(kw=kw)

    @staticmethod
    def get_translation(poem_id):
        return GuShiWen.TRANSLATION_QUERY.substitute(poemid=poem_id)

    @staticmethod
    def extract_info(text):
        match_ids = match_and_trim(GuShiWen.GET_ID_PATTERN, text)
        match_ok_ids = match_and_trim(GuShiWen.GET_ID_HAS_TRANSLATION_PATTERN, text)  # Some tang have translated text.
        match_titles = match_and_trim(GuShiWen.GET_TITLE_PATTERN, text)
        match_authors = re.findall(GuShiWen.GET_AUTHOR_PATTERN, text)
        match_authors = [[text.strip() for text in ele] for ele in match_authors]

        num_candidates = len(match_ids)
        info_ret = []

        for i in range(num_candidates):
            poem_id = match_ids[i]
            if poem_id in match_ok_ids:
                title = match_titles[i]
                author, dynasty = match_authors[i]
                zh_title = "".join(match_and_trim(GuShiWen.GET_CHINESE_PATTERN, title))
                info_ret.append((poem_id, zh_title, author, dynasty))

        return info_ret

    @staticmethod
    def extract_page_info(text):
        def check(ll):
            return ll

        match_ok_ids = match_and_trim(GuShiWen.GET_ID_HAS_TRANSLATION_PATTERN, text)
        match_titles = match_and_trim(GuShiWen.GET_TITLE_IN_PAGE_PATTERN, text)
        match_authors = re.findall(GuShiWen.GET_AUTHOR_IN_PAGE_PATTERN, text)

        if not (check(match_ok_ids) and check(match_titles) and check(match_authors)):
            return None

        title = match_titles[0]
        author, dynasty = match_authors[0]
        poem_id = match_ok_ids[0]

        ret = (poem_id, title, author, dynasty)
        return ret

    @staticmethod
    def extract_translation_pairs(text):
        match_pairs = re.findall(GuShiWen.GET_POEM_TRANSLATION_PATTERN, text)
        if not match_pairs:
            return None
        poem, translation = zip(*match_pairs)
        poem = [text.strip() for text in poem]
        translation = [text.strip() for text in translation]
        return [{"text": text, "poem": poem} for text, poem in zip(translation, poem)]


def do_judge(translated_pairs, len_test=None):
    if len(translated_pairs) > 4:
        poem = [a["poem"] for a in translated_pairs[1:]]  # ignore first line
    else:
        poem = [a["poem"] for a in translated_pairs]
    poem = [remove_p(text) for text in poem]
    poem = list(chain.from_iterable([re.split(PUNCTUATION_ZH, text) for text in poem]))
    poem = list(filter(lambda s: len(s), poem))
    first_len = len(poem[0])

    judge = all([first_len == len(other) for other in poem])

    if not judge:
        return False

    if judge and len_test:
        return first_len in len_test


def get_detail_page(url, s, judge_poem=False):
    combine_url = GuShiWen.combine_url(url)
    page_text = do_get_driver(s, combine_url)

    page_meta = GuShiWen.extract_page_info(page_text)
    # print(page_meta)

    if not page_meta:
        return None

    poem_id, title, author, dynasty = page_meta
    translation_pairs = get_translation_pairs(poem_id, s)

    if not translation_pairs:
        return None

    if judge_poem:
        if not do_judge(translation_pairs):  # judge whether is poem
            return None

    ret = {"title": title, "author": author, "dynasty": dynasty, "content": translation_pairs}
    return ret


def get_gushiwen_metas(kw, s):
    page_text = do_get_driver(s, GuShiWen.get_search(kw))
    poem_metas = GuShiWen.extract_info(page_text)
    return poem_metas


def get_translation_pairs(poem_id, s):
    # print("Poem id: ", poem_id)
    text = do_get_driver(s, GuShiWen.get_translation(poem_id))
    # print(text)
    pairs = GuShiWen.extract_translation_pairs(text)
    # print(pairs)
    return pairs


def majority_judge(elements):
    if len(elements) <= 1:  # GE 2 elements are required.
        return False, None
    cnt = Counter(elements)
    if len(cnt.keys()) <= 1:
        return True, elements[0]

    cnt = cnt.most_common()
    if cnt[0][1] > cnt[1][1] or cnt[0][1] > 0.3 * len(elements):  # Relative majority
        return True, cnt[0][0]
    else:
        return False, None


def majority_select_meta(text, s):
    current_metas = get_gushiwen_metas(text[0], s)
    if not current_metas:
        return None
    for other in text[1:]:
        other_metas = get_gushiwen_metas(other, s)
        # print("add: ", other_metas)
        current_metas.extend(other_metas)
        is_ok, majority = majority_judge(current_metas)
        if is_ok:
            # print("Ok at: ", current_metas)
            return majority
    return None


def try_gushiwen(text_list, s):
    poem_meta = majority_select_meta(text_list, s)

    # print(poem_meta)
    if not poem_meta:
        return None

    poem_id, title, author, dynasty = poem_meta
    translation_pairs = get_translation_pairs(poem_id, s)
    if not translation_pairs:
        return None

    ret = {"title": title, "author": author, "dynasty": dynasty, "content": translation_pairs}
    return ret
