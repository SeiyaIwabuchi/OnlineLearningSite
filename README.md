# OnlineLearningSite
# READMEはまだ真面目に書くつもりはないですのでよろしく  ( ｀・∀・´)ﾉﾖﾛｼｸ
# なにこれ
オンラインで勉強できるように作りました。自分で問題を作って自分で解く、もしくはみんなに解いてもらう。そういう使い方ができそうです。
# ブランチについて
そのうちにgit-flowに従ってブランチを分け始めます。
# 使い方
起動の方法を変更しました。
「python ./server.py」
だけで起動できます。
また教科や問題をブラウザ上から編集できるように今開発中です。
# 今後追加したい機能
- ユーザー管理機能
    - 主に管理者の管理を行いたい
# 私利私欲メモ
``` txt
---------------------------------------------------
クライアント側ノート
結果表示用ページは
問題数
正答数
誤答数
正答率
誤答率
を表示して
問題と正誤を表で表示する。

----------------------------------------------------
サーバー側ノート
問題ページアクセス時に成績classのインスタンスを作成しrecordListに追加しておく
回答するボタンで回答数のインクリメント、正答数、誤答数を状態に応じてインクリメント
結果ページアクセス時に統計データを呼び出す
アクセスから一定時間経過したデータは消すようにする。
管理用画面の追加（現在のアクセス数、直近のアクセス時間、問題アップロード）
問題アップロード
ユーザー認証
jsでサーバーにデータ転送
サーバーから認証の失敗、成立とURLを送る
ブラウザ側でURLに遷移するか、誤っていると表示する。
ログイン画面要求→ログイン画面返送→ログイン情報送信→ログイン認証結果返送
--------------------------------------------------------------------
やりたいこと
ユーザー登録用画面の実装
データベース連携
やっぱりURLをコピペすればログインできちゃうから、ブラウザを閉じたときにかこのURLは使えないようにする。
結果画面で自分が何を選択したかを表示する。

教科ごとに分ける
別ページを用意する。
内容は
    リストボックスで科目選択して、始めるをクリックする。
    iwabuchi.ddns.net/mainmenuでこのページにアクセスできるようにする。
メインサーバー起動後自動で各教科のサーバーも起動するようにする。
別プロセスで呼び出すか
そのままインポートして読み込む
    server.pyをクラス化してmainmenu.pyでインスタンスを必要分生成する。
subjectListはjson形式で   教科名:URLで記述する
レスポンシブデザインにすること

クッキーを使ったセッション管理方法
    ユーザーデータは最終アクセスから１時間で消滅する
    クッキーデータはアクセス毎に更新し有効期間を上書きしていく。
    フロー
        （ユーザーが）アクセス→（サーバーで）クッキーを取得→問題をセッションIDに基づいて返信するとともにクッキーを 書き換える。
    新規のユーザーへは新しくクッキーをセットする。

ブラウザからサーバーに送信はしたものの、サーバーからレスポンスが返ってこないときがある。そのときに回答するボタンをク リックする前までは次に進まないようにする。リロードされたときに再び同じ問題を回答するようにする。

テキストデータで判定もできるようにもしたい。その問題がラジオボタンで答える問題かテキストで答える問題かを識別して処理 を分ける必要がある。ユーザーによっては同じ意味の文字列でもコンピュータとしては別の文字列となるときがあるので認識の差 をどうにかして吸収したい。たとえばスペースは正規表現で吸収できる。半角全角の差は全角<->半角の相互変換で対応できそう。

ユーザー管理機能追加してください。
"
``` python
subjectMngListTemp = "\
   <tr>\
      <td>{subName}</td>\
      <td align=\"right\">\
            <input type=\"text\" id=\"{subText}\"></input>\
      </td>\
      <td align=\"right\">\
            <button onclick=\"location.href='#'\" class=\"btn btn-secondary\" id=\"{subMod}\">変更</button>\
      </td>\
      <td align=\"right\">\
         <button onclick=\"location.href='{URL}'\" class=\"btn btn-secondary\" id=\"{subDel}\">削除</button>\
      </td>\
   </tr>"
```