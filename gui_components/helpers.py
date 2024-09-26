from datetime import datetime
import re


def calc_timestamp():
    return int(datetime.now().timestamp())


def extract_channel_from_label(text):
    ch = re.search(r"\d+", text).group()
    ch_num = int(ch)
    ch_num_index = ch_num - 1
    return ch_num_index
