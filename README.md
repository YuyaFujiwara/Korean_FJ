# Hanguk Word Trainer

韓国語単語の学習用 Tkinter アプリです。

## 必要環境

- Python 3.10+
- Windows（`osk` / `winmm` を使うため）

## セットアップ

```bash
pip install -r requirements.txt
```

## 起動

```bash
python Hanguk_word.py
```

## 機能

- 4択: 日→韓
- 4択: 韓→日
- 入力: 日→韓（ローマ字 / ハングル入力パッド）
- フラッシュ: 韓⇄日
- 音声再生（`edge-tts`）
- 学習進捗の JSON 保存

## ファイル構成

- `Hanguk_word.py`: エントリポイント
- `trainer_app.py`: アプリ組み立て
- `trainer_ui.py`: UI 構築
- `trainer_handlers.py`: 出題・判定・進捗処理
- `trainer_ime.py`: ハングル入力処理
- `hangul_utils.py`: ハングル関連ユーティリティ
- `vocab_progress.py`: 語彙読み込み・進捗保存
- `tts_player.py`: 音声再生

## 補足

- `tkinter` は標準ライブラリです。
- `edge-tts` が未導入の場合、音声再生時に案内ダイアログが表示されます。
