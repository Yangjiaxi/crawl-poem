from pathlib import Path


class Config:
    _root = "./result"
    store_root = Path(_root)
    _precached_root = "./precached"
    precached_root = Path(_precached_root)

    # ---------------------------------------------------
    _poem_urls = "poem_urls.txt"
    path_poem_urls = store_root.joinpath(_poem_urls)

    _poem_meta = "poem_meta.txt"
    _meta_bin = "poem_meta.pkl"
    path_poem_meta = store_root.joinpath(_poem_meta)
    path_meta_bin = store_root.joinpath(_meta_bin)

    # ---------------------------------------------------
    # to crawl from precached json file
    _tang_poem_file = "tang.txt"
    tang_poem_file = precached_root.joinpath(_tang_poem_file)
    _tang_folder = "tang"
    tang_root = store_root.joinpath(_tang_folder)

    # ---------------------------------------------------
    # five characters poems
    _five_poem_file = "five.txt"
    five_poem_file = precached_root.joinpath(_five_poem_file)
    _five_folder = "five"
    five_root = store_root.joinpath(_five_folder)

    # ---------------------------------------------------
    # seven characters poems
    _seven_poem_file = "seven.txt"
    seven_poem_file = precached_root.joinpath(_seven_poem_file)
    _seven_folder = "seven"
    seven_root = store_root.joinpath(_seven_folder)

    # ---------------------------------------------------
    # crawl from webpage
    _page_folder = "page"
    page_root = store_root.joinpath(_page_folder)

    # ---------------------------------------------------
    # merge
    _merge_folder = "merge"
    merge_root = store_root.joinpath(_merge_folder)
    _merge_file = "merge.json"
    merge_file = store_root.joinpath(_merge_file)
