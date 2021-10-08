# 爬取古诗文网的古诗和翻译

## Requirements

```python
selenium==3.141.0
ujson==4.0.2
requests==2.26.0
```

## Usage

### Step.1 爬取

```sh
# 从页面中爬取
python page.py

# 根据 precached/five.txt 爬取
python five.py

# 根据 precached/seven.txt 爬取
python seven.py

# 根据 precached/tang.txt 爬取
# START_AT 为起始编号
python tang.py --l START_AT
```

输出在 `./result/XXX` 下，每首诗独立 `.json` 保存

### Step.2 整合

```sh
# 执行 **两遍**
python merge.py
```

输出在 `./result/merge/` 与 `./result/merge.json`


Contact: [jason.yang98@foxmail.com](mailto:jason.yang98@foxmail.com)