from typing import List, Tuple, Dict, Union
import wikipedia
import json
import time
import logging
logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)

SLEEP_TIME = 3

"""辞書の性能評価をするための、評価データを生成します。
評価用のテキストのため、wikipediaから記事の取得を実行します。

Python3.5.1の環境下で動作を確認しています。
"""

__author__ = "Kensuke Mitsuzawa"
__author_email__ = "kensuke_mitsuzawa@fumankaitori.com"
__license_name__ = "MIT"


def get_wikipedia_page(page_title):
    # type: (str) -> Union[bool, str]
    try:
        return wikipedia.page(page_title).content
    except:
        logger.error()
        return False


def get_wikipedia_summary(page_title:str, n_summary_sentence:int=3):
    # type: (str, int)->Union[bool, str]
    try:
        return wikipedia.summary(page_title, n_summary_sentence)
    except:
        logger.error()
        return False


def main(path_extracted_wikipedia_text:str,
         wikipedia_article_names:List[Tuple[str, str]]):
    wikipedia.set_lang('ja')
    wikipedia_text_data = {}
    extracted_summary_text = []
    for article_name in wikipedia_article_names:
        text = get_wikipedia_summary(article_name[0])
        wikipedia_text_format = {}
        wikipedia_text_format["page_title"] = article_name[0]
        wikipedia_text_format["text"] = text
        wikipedia_text_format["gold_label"] = article_name[1]
        logger.info(msg='Got wikipedia page={}'.format(article_name))
        if not text is False:
            logger.info(msg='It gets text from page-name={}'.format(article_name))
            extracted_summary_text.append(wikipedia_text_format)
        time.sleep(SLEEP_TIME)

    extracted_full_text = []
    for article_name in wikipedia_article_names:
        text = get_wikipedia_page(article_name[0])
        wikipedia_text_format = {}
        wikipedia_text_format["page_title"] = article_name[0]
        wikipedia_text_format["text"] = text
        wikipedia_text_format["gold_label"] = article_name[1]
        logger.info(msg='Got wikipedia page={}'.format(article_name))
        if not text is False:
            logger.info(msg='It gets text from page-name={}'.format(article_name))
            extracted_full_text.append(wikipedia_text_format)
        time.sleep(SLEEP_TIME)

    wikipedia_text_data['summary'] = extracted_summary_text
    wikipedia_text_data['full'] = extracted_full_text
    with open(path_extracted_wikipedia_text, 'w') as f:
        f.write(json.dumps(wikipedia_text_data, ensure_ascii=False, indent=4))


if __name__ == '__main__':
    path_extracted_wikipedia_text = './wikipedia-text/wikipedia_text.json'
    wikipedia_article_names = [
        ### 住まい・暮らし ###
        ("マジックリン", "暮らし・住まい-バス・トイレ・洗面用品"),
        ("フライパン", "暮らし・住まい-キッチン用品・食器・調理器具"),
        ("マットレス", "暮らし・住まい-寝具・ベッド"),
        ("学習机", "暮らし・住まい-インテリア・収納"),
        ("アパート", "暮らし・住まい-賃貸"),
        ("訳あり物件", "暮らし・住まい-住宅"),
        ("公営住宅", "暮らし・住まい-暮らし・住まい-賃貸"),
        ("文房具", "暮らし・住まい-オフィス用品・文房具"),
        ("MONO消しゴム", "暮らし・住まい-オフィス用品・文房具"),
        ### ファッション ###
        ("トートバッグ", "ファッション-バッグ・小物・雑貨"),
        ("ブラジャー", "ファッション-下着・ナイトウェア"),
        ("ビキニ (水着)", "ファッション-服（レディース）"),
        ("G-SHOCK", "ファッション-腕時計"),
        ("Apple Watch", "ファッション-腕時計"),
        ("指輪", "ファッション-ジュエリー・アクセサリー"),
        ("ミキモト", "ファッション-ジュエリー・アクセサリー"),
        ("マドラス (企業)", "ファッション-靴"),
        ### 趣味・エンタメ ###
        ("スター・ウォーズ エピソード4/新たなる希望", "趣味・エンタメ-映画・ミュージカル"),
        ("アルジャジーラ", "趣味・エンタメ-テレビ番組"),
        ("PlayStation 3", "趣味・エンタメ-ゲーム"),
        ("PlayStation 4", "趣味・エンタメ-ゲーム"),
        ("アクオス", "デジタル・家電-TV・レコーダー・オーディオ"),
        ("競馬", "趣味・エンタメ-ギャンブル"),
        ("月刊コロコロコミック", "趣味・エンタメ-マンガ・雑誌"),
        ("世界の果てまでイッテQ!", "趣味・エンタメ-テレビ番組"),
        ("プラレール", "趣味・エンタメ-おもちゃ"),
        ("Google Play", "趣味・エンタメ-モバイルアプリ"),
        ### 食品・飲料 ###
        ("カップヌードル", "食品・飲料-インスタント食品"),
        ("日清焼そばU.F.O.", "食品・飲料-インスタント食品"),
        ("コーラ (飲料)", "食品・飲料-水・ソフトドリンク"),
        ("第三のビール", "食品・飲料-ビール・チューハイ"),
        ("FRISK", "食品・飲料-タブレット菓子"),
        ("冷凍みかん", "食品・飲料-冷凍食品"),
        ("ハリボー", "食品・飲料-グミ"),
        ("明治ミルクチョコレート", "食品・飲料-チョコレート"),
        ("カステラ", "食品・飲料-スイーツ・お菓子"),
        ### 外食・店舗 ###
        ("大戸屋ホールディングス", "外食・店舗-レストラン"),
        ("マクドナルド", "外食・店舗-ファーストフード"),
        ("昭和お好み焼き劇場うまいもん横丁", "外食・店舗-居酒屋"),
        ("ローソン", "外食・店舗-コンビニ・スーパーマーケット"),
        ("立ち食いそば・うどん店", "外食・店舗-レストラン"),
        ("ほっかほっか亭", "外食・店舗-お弁当屋"),
        ("ジョナサン (ファミリーレストラン)", "外食・店舗-ファミリーレストラン"),
        ("エクセルシオール カフェ", "外食・店舗-カフェ・喫茶"),
        ("バーミヤン (レストランチェーン)", "外食・店舗-レストラン"),
        ("あきんどスシロー", "外食・店舗-レストラン"),
        ### 医療・福祉 ###
        ("東京大学医学部附属病院", "医療・福祉-病院"),
        ("漢方薬", "医療・福祉-医薬品"),
        ("ルル (風邪薬)", "医療・福祉-医薬品"),
        ("介護老人福祉施設", "医療・福祉-介護"),
        ("要介護認定", "医療・福祉-介護"),
        ("訪問介護", "医療・福祉-介護"),
        ("タケダ胃腸薬", "医療・福祉-医薬品"),
        ("診療所", "医療・福祉-病院"),
        ("地域医療", "医療・福祉-病院"),
        ("ベンザ (風邪薬)", "医療・福祉-医薬品"),
        ### アウトドア・スポーツ ###
        ("ヤマハ・SR", "アウトドア・スポーツ-バイク・バイク用品"),
        ("スカッシュ (スポーツ)", "アウトドア・スポーツ-スポーツ"),
        ("剣道", "アウトドア・スポーツ-スポーツ"),
        ("ホットヨーガ", "アウトドア・スポーツ-ジム・ヨガ"),
        ("フィットネスクラブ", "アウトドア・スポーツ-ジム・ヨガ"),
        ("リカンベント", "アウトドア・スポーツ-自転車・自転車用品"),
        ("電動アシスト自転車", "アウトドア・スポーツ-自転車・自転車用品"),
        ("ヘルメット (オートバイ)", "アウトドア・スポーツ-バイク・バイク用品"),
        ("ホンダ・アフリカツイン", "アウトドア・スポーツ-バイク・バイク用品"),
        ### デジタル・家電 ###
        ("VARDIA", "デジタル・家電-TV・レコーダー・オーディオ"),
        ("ブラビアリンク", "デジタル・家電-TV・レコーダー・オーディオ"),
        ("ビエラリンク", "デジタル・家電-TV・レコーダー・オーディオ"),
        ("DIGA", "デジタル・家電-TV・レコーダー・オーディオ"),
        ("VAIO", "デジタル・家電-パソコン・周辺機器"),
        ("iPhone 6", "デジタル・家電-タブレットPC・スマートフォン"),
        ("一眼レフカメラ", "デジタル・家電-カメラ・デジタルカメラ"),
        ("Microsoft Surface", "デジタル・家電-タブレットPC・スマートフォン"),
        ("本炭釜", "デジタル・家電-家電"),
        ### 宿泊・観光・レジャー ###
        ("ユニバーサル・スタジオ・ジャパン", "宿泊・観光・レジャー-観光・レジャー施設"),
        ("志摩スペイン村", "宿泊・観光・レジャー-観光・レジャー施設"),
        ("リトルワールド", "宿泊・観光・レジャー-観光・レジャー施設"),
        ("スペースワールド", "宿泊・観光・レジャー-観光・レジャー施設"),
        ("帝国ホテル", "宿泊・観光・レジャー-ホテル・宿泊"),
        ("ムツゴロウ動物王国", "宿泊・観光・レジャー-観光・レジャー施設"),
        ### 公共・環境 ###
        ("山手線", "公共・環境-駅・電車"),
        ("新宿駅", "公共・環境-駅・電車"),
        ("成田国際空港", "公共・環境-空港・飛行機"),
        ("エールフランス", "公共・環境-空港・飛行機"),
        ("国道1号", "公共・環境-道路・交通"),
        ("名神高速道路", "公共・環境-道路・交通"),
        ("公民館", "公共・環境-公共施設"),
        ("名鉄バス", "公共・環境-バス・タクシー"),
        ("エムケイ (タクシー会社)", "公共・環境-バス・タクシー"),
        ("エマーム・ホメイニー国際空港", "公共・環境-空港・飛行機"),
        ### 教育・大学 ###
        ("奈良先端科学技術大学院大学", "教育-大学"),
        ("Z会", "教育-通信教育"),
        ("東進ハイスクール", "教育-塾・教育支援"),
        ("大学院大学", "教育-大学"),
        ("日本ジャーナリスト専門学校", "教育-専門学校"),
        ("HAL (専門学校)", "教育-専門学校"),
        ("日本大学東北高等学校", "教育-高等学校"),
        ("PL学園中学校・高等学校", "教育-高等学校"),
        ("学習院初等科", "教育-小学校"),
        ### 政治・行政 ###
        ("比例代表制", "政治・行政-政治・選挙"),
        ("アメリカ合衆国大統領選挙", "政治・行政-政治・選挙"),
        ("常会", "政治・行政-国政"),
        ("特別会", "政治・行政-国政"),
        ### 仕事 ###
        ("求人", "仕事-就職"),
        ("転職会議", "仕事-転職"),
        ("雇用保険事業", "仕事-待遇・福利厚生"),
        ### ペット ###
        ("ペットホテル", "ペット-ペットショップ"),
        ("コジマ (ペット)", "ペット-ペットショップ"),
        ("うさぎのしっぽ", "ペット-ペットショップ"),
        ("西武ペットケア", "ペット-ペットフード"),
        ("ドギーマンハヤシ", "ペット-ペットフード"),
    ]
    main(path_extracted_wikipedia_text, wikipedia_article_names)