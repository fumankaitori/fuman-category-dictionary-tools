from typing import List, Dict, Union, Any, Tuple, Callable
from tempfile import mkdtemp
from itertools import chain, groupby
from functools import partial
import json
import logging
import os

"""辞書の利用法の一例として、テキストのカテゴリ判別をします。
辞書のスコアにしたがって、テキストにスコア計算をし、ランキングが高い順にカテゴリ名を表示します。

Python3.5.1の環境下で動作を確認しています。
"""

__author__ = "Kensuke Mitsuzawa"
__author_email__ = "kensuke_mitsuzawa@fumankaitori.com"
__license_name__ = "MIT"

try:
    from JapaneseTokenizer import MecabWrapper

except ImportError:
    raise ImportError('先にpip install JapaneseTokenizerを実行してください。')

try:
    from sqlitedict import SqliteDict
except ImportError:
    raise ImportError('先にpip install sqlitedictを実行してください')

POS_CONDITION = [('名詞', '固有名詞'), ('名詞', '一般'), ('名詞', 'サ変接続'), ('動詞', '自立')]

def load_dictionary_data(path_dictionary_data):
    # type: (str)->List[Dict[str,Any]]
    with open(path_dictionary_data, 'r') as f:
        return json.loads(f.read())


def save_into_cached_dictionary(dict_object:Dict[str, List[List[str]]], cached_dict_object:SqliteDict):
    for key, values in dict_object.items():
        if not key in cached_dict_object:
            cached_dict_object[key] = values
        else:
            cached_dict_object[key] += values

    del dict_object
    return cached_dict_object


def reformat_dictionary(score_dictionary,
                        batch_size=10000,
                        is_use_sqlite=False):
    # type: (List[Dict[str,Any]], int)->Union[SqliteDict, Dict[str, List[Tuple[str,float]]]]
    """* What you can do
    - 辞書の形を変形します。

    * Input
    >>> [{"label": "アウトドア・スポーツ-その他", "score": 0.02942301705479622, "word": "お金"}]

    * Output
    >>> {"お金": [("アウトドア・スポーツ-その他", 0.02942301705479622)]}
    """
    temporary_dir = mkdtemp()
    if is_use_sqlite:
        word_score_dictionary = SqliteDict(os.path.join(temporary_dir, 'temporary_dict.sqlite3'), autocommit=True)
    else:
        word_score_dictionary = {}

    logging.info(msg="Loaded N(record)={}".format(len(score_dictionary)))

    if is_use_sqlite:
        counter = 0  # type: int
        temporary_dict_obj = {}

        for score_object in score_dictionary:
            score_tuple = (score_object['label'], score_object['score'])
            if not score_object['word'] in temporary_dict_obj:
                temporary_dict_obj[score_object['word']] = [score_tuple]
            else:
                temporary_dict_obj[score_object['word']].append(score_tuple)

            counter += 1
            if counter % batch_size == 0:
                word_score_dictionary = save_into_cached_dictionary(temporary_dict_obj, word_score_dictionary)
                del temporary_dict_obj
                temporary_dict_obj = {}
                logging.info(msg='Processed {} records now.'.format(counter))
    else:
        for score_object in score_dictionary:
            score_tuple = (score_object['label'], score_object['score'])
            if not score_object['word'] in word_score_dictionary:
                word_score_dictionary[score_object['word']] = [score_tuple]
            else:
                word_score_dictionary[score_object['word']].append(score_tuple)

    return word_score_dictionary


def __tokenize(input_string: str, mecab_tokenizer, pos_condition)->List[str]:
    tokenized_sentence_obj = mecab_tokenizer.tokenize(sentence=input_string, return_list=False)
    return mecab_tokenizer.filter(parsed_sentence=tokenized_sentence_obj, pos_condition=pos_condition).convert_list_object()


def get_text_score(input_text,
                   word_score_dictionary,
                   function_tokenizer):
    """* What you can do
    - スコアリング関数
    - カテゴリごとにスコアを算出することができます。
    """
    # type: (str, Dict[str, List[Tuple[str,float]]], Callable[[str], List[str]])->List[Tuple[str,float]]
    key_function = lambda tuple_obj: tuple_obj[0]
    list_tokens = function_tokenizer(input_text)
    seq_score_elements = [word_score_dictionary[token] for token in list_tokens if token in word_score_dictionary]

    score_category = []
    for key_name, grouped_obj in groupby(sorted(chain.from_iterable(seq_score_elements), key=key_function, reverse=True), key=key_function):
        category_score = sum([score_tuple[1] for score_tuple in grouped_obj])
        score_category.append((key_name, category_score))

    return sorted(score_category, key=lambda tuple_obj: tuple_obj[1], reverse=True)


def main(input_text:str,
         path_mecab_bin:str,
         path_dictionary_data:str,
         pos_condition:List[Tuple[str,...]]=POS_CONDITION):
    if not os.path.exists(os.path.join(path_mecab_bin, 'mecab-config')):
        raise FileExistsError('mecab-configファイルが見つかりません')

    mecab_tokenizer = MecabWrapper(dictType='neologd', path_mecab_config=path_mecab_bin)
    word_score_dictionary = reformat_dictionary(load_dictionary_data(path_dictionary_data))

    function_mecab_tokenizer = partial(__tokenize, mecab_tokenizer=mecab_tokenizer, pos_condition=pos_condition)

    seq_score_tuple = get_text_score(input_text=input_text,
                                     word_score_dictionary=word_score_dictionary,
                                     function_tokenizer=function_mecab_tokenizer)

    return seq_score_tuple

if __name__ == '__main__':
    ### 評価したい文
    input_text = '鈴鹿サーキット（すずかサーキット、Suzuka Circuit）は、三重県鈴鹿市にある国際レーシングコースを中心としたレジャー施設。F1日本グランプリや鈴鹿8時間耐久ロードレースなどの開催で知られる。レーシングコースの他に遊園地やホテル等があり、モビリティリゾート（自動車を題材とする行楽地）を形成している。'
    ### mecab-configが存在しているディレクトリ
    path_mecab_bin = '/usr/local/bin'
    ### 辞書jsonファイルが存在しているパス
    path_dictionary_json = './dictionary-data/word_soa.json'

    seq_evaluated_result = main(input_text=input_text,
                                path_mecab_bin=path_mecab_bin,
                                path_dictionary_data=path_dictionary_json)
    import pprint
    ### スコアが高い順に10カテゴリまでをチェックする
    pprint.pprint(seq_evaluated_result[:10])