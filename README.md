# mercari
メルカリのサイトをスクレイピングして、macbookの商品概要をまとめて、google spreadsheetに保存する。
商品概要は、以下10項目で判断する。
1. 年式
2. Macbook Air or Macbook Pro
3. メモリ容量
4. 発売時期（Early, Mid, Late）
5. SSDやHDDの容量
6. モニタのインチ数
7. 商品の状態
8. 最近のコメントの日時
9. 価格
10. 商品URL
spreadsheetに保存されたN行×10列の行列をソートすると、各項目に対して相場がわかるようになる。
さらに、1週間当たりどの価格でいくつ商品が売られているかもわかる。
