from typing import List, Dict, Union, Any, Tuple, Callable
from tempfile import mkdtemp
from itertools import chain, groupby
from functools import partial
import json
import logging
import os
logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)

"""辞書の利用法の一例として、テキストのカテゴリ判別をします。
辞書のスコアにしたがって、テキストにスコア計算をし、ランキングが高い順にカテゴリ名を表示します。
性能評価はデータにはWikipediaテキストを利用しています。

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


def load_evaluation_data(path_evaluation_data):
    # type: (str)->Dict[str,Any]
    with open(path_evaluation_data, 'r') as f:
        return json.loads(f.read())


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

    logger.info(msg="Loaded N(record)={}".format(len(score_dictionary)))

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
                logger.info(msg='Processed {} records now.'.format(counter))
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


def evaluate_result(gold_label,
                    predicred_result):
    # type: (str, List[Tuple[str, float]])->Tuple[str, bool]
    """* What you can do
    - You get run evaluation on test text
    - It returns Tuple of (gold-category, flag). The flag is True if gold label in predicted result Else False
    """
    seq_category_name = set([category_name_tuple[0] for category_name_tuple in predicred_result])
    if gold_label in seq_category_name: return (gold_label, True)
    else: return (gold_label, False)


def  get_result_statistics(seq_result_tuple):
    # type: List[Tuple[str, bool]] -> None
    """* What you can do
    - カテゴリごとに性能評価を出す
    """
    key_function = lambda eval_res_tuple: eval_res_tuple[0]

    seq_eval_result = [(tuple_eval_result[0].split('-')[0], tuple_eval_result[1]) for tuple_eval_result in seq_result_tuple]
    g_object = groupby(sorted(seq_eval_result, key=key_function, reverse=True), key=key_function)
    for category_name, seq_eval_res in g_object:
        seq_result_flags = [seq_eval_tuple[1] for seq_eval_tuple in seq_eval_res]
        accuracy_of_category = len([res_flag for res_flag in seq_result_flags if res_flag is True]) / len(seq_result_flags)
        logger.info(msg='Accuracy of category={}; {} = {} / {}'.format(category_name,
                                                                        accuracy_of_category,
                                                                        len([res_flag for res_flag in seq_result_flags if res_flag is True]),
                                                                        len(seq_result_flags)))


def main(path_mecab_bin,
         path_evaluation_data,
         path_dictionary_data,
         pos_condition,
         ranking_evaluation=3):
    # type: (str, str, str, List[Any, int])->None
    mecab_tokenizer = MecabWrapper(dictType='neologd', path_mecab_config=path_mecab_bin)
    evaluation_data = load_evaluation_data(path_evaluation_data)
    word_score_dictionary = reformat_dictionary(load_dictionary_data(path_dictionary_data))

    function_mecab_tokenizer = partial(__tokenize, mecab_tokenizer=mecab_tokenizer, pos_condition=pos_condition)
    flags = []
    ### wikipediaリードテキストに対する評価 ###
    for evaluation_obj in evaluation_data['summary']:
        #### スコアリングの実施 ####
        seq_score_tuple = get_text_score(input_text=evaluation_obj['text'],
                                         word_score_dictionary=word_score_dictionary,
                                         function_tokenizer=function_mecab_tokenizer)
        #### 評価 ####
        tuple_boolean_flag = evaluate_result(gold_label=evaluation_obj['gold_label'],
                                       predicred_result=seq_score_tuple[:ranking_evaluation])
        logger.info(
            msg='Page-name={} -> Evaluation-flag={}, Score = {}'.format(evaluation_obj['page_title'],
                                                                        tuple_boolean_flag[1],
                                                                        seq_score_tuple[:ranking_evaluation]))
        flags.append(tuple_boolean_flag)

    ### 評価の統計値算出 ###
    true_flags = [True for tuple_flag in flags if tuple_flag[1] is True]
    logger.info(msg='='*40)
    logger.info(msg='Accuracy of wikipedia summary text when rank={}'.format(ranking_evaluation))
    logger.info(msg='Accuracy; {} = {} / {}'.format(len(true_flags)/len(flags), len(true_flags), len(flags)))
    ### カテゴリごとの正解率統計算出に対する評価 ###
    get_result_statistics(flags)
    logger.info('+'*40)

    # --------------------------------------------------------------------------------------------------------


    ### wikipedia全文に対する評価 ###
    flags = []
    for evaluation_obj in evaluation_data['full']:
        #### スコアリングの実施 ####
        seq_score_tuple = get_text_score(input_text=evaluation_obj['text'],
                                         word_score_dictionary=word_score_dictionary,
                                         function_tokenizer=function_mecab_tokenizer)
        #### 評価 ####
        tuple_boolean_flag = evaluate_result(gold_label=evaluation_obj['gold_label'],
                                       predicred_result=seq_score_tuple[:ranking_evaluation])
        logger.info(
            msg='Page-name={} -> Evaluation-flag={}, Score = {}'.format(evaluation_obj['page_title'],
                                                                        tuple_boolean_flag[1],
                                                                        seq_score_tuple[:ranking_evaluation]))
        flags.append(tuple_boolean_flag)

    ### 評価の統計値算出 ###
    true_flags = [True for tuple_flag in flags if tuple_flag[1] is True]
    logger.info(msg='='*40)
    logger.info(msg='Accuracy of wikipedia full text when rank={}'.format(ranking_evaluation))
    logger.info(msg='Accuracy; {} = {} / {}'.format(len(true_flags)/len(flags), len(true_flags), len(flags)))
    ### カテゴリごとの正解率統計算出に対する評価 ###
    get_result_statistics(flags)
    logger.info('+'*40)

    if isinstance(word_score_dictionary, SqliteDict): word_score_dictionary.close()


if __name__ == '__main__':
    PATH_MECAB_BIN = '/usr/local/bin'
    #PATH_EVALUATION_DATA = './wikipedia-text/wikipedia_text.json'
    PATH_EVALUATION_DATA = './wikipedia-text/wikipedia_text.json'

    #PATH_DICTIONARY_DATA = './wikipedia-text/word_soa.json'
    PATH_DICTIONARY_DATA = './dictionary-data/word_soa.json'
    pos_condition = [('名詞', '固有名詞'), ('名詞', '一般'), ('名詞', 'サ変接続'), ('動詞', '自立')]
    if not os.path.exists(PATH_DICTIONARY_DATA): raise FileExistsError('辞書ファイルが発見できません。')

    main(
        path_mecab_bin=PATH_MECAB_BIN,
        path_evaluation_data=PATH_EVALUATION_DATA,
        path_dictionary_data=PATH_DICTIONARY_DATA,
        pos_condition=pos_condition,
        ranking_evaluation=1
    )

    main(
        path_mecab_bin=PATH_MECAB_BIN,
        path_evaluation_data=PATH_EVALUATION_DATA,
        path_dictionary_data=PATH_DICTIONARY_DATA,
        pos_condition=pos_condition,
        ranking_evaluation=3
    )

    main(
        path_mecab_bin=PATH_MECAB_BIN,
        path_evaluation_data=PATH_EVALUATION_DATA,
        path_dictionary_data=PATH_DICTIONARY_DATA,
        pos_condition=pos_condition,
        ranking_evaluation=5
    )