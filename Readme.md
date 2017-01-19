# 不満カテゴリ辞書データ ツールキット

本リポジトリでは、国立情報学研究所経由で提供を行っている「不満カテゴリ辞書データ」のためのスクリプトを公開しています。
本リポジトリのコードを利用すると、不満カテゴリ辞書データを利用して、簡便にカテゴリ分類の実施が可能です。

本リポジトリのコードを利用したカテゴリ分類結果については、国立情報学研究所のページを参照してください。

# 動作環境

Python3.5で動作を確認しています。
Python2x系では動作をしません。

# セットアップ

## 辞書ファイルの用意

NIIのリポジトリからダウンロードした辞書ファイルのJSONファイルを `./dictionary-data` 以下に配置します。

## 形態素解析システムの準備

[JapaneseTokenizer](https://github.com/Kensuke-Mitsuzawa/JapaneseTokenizers)のReadmeを読み、形態素解析器のインストールを実施してください。

## 依存パッケージの準備

```
python setup.py install
```

# スクリプトの説明

## Wikipediaテキストデータの用意

```
python get_wikipedia_text.py
```

## Wikipediaテキストを利用した辞書性能の評価

```
python evaluate_dictionary.py
```

## 辞書データを利用したカテゴリ分類

```
python get_category_score.py
```

