# -*- coding: utf-8 -*-

# macbookマーケティング用
# スクレイピングしてきて各商品の各項目（モデル、SSD容量等）をspreadsheetに保存

import urllib2
from bs4 import BeautifulSoup
import codecs
import string
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import threading
import time
from datetime import datetime
import httplib2
import os
import apiclient
import oauth2client
import argparse
import base64
from email.mime.text import MIMEText
from email.utils import formatdate
import traceback
flags = argparse.ArgumentParser(
    parents=[oauth2client.tools.argparser]
).parse_args()

# 購入された商品or出品中の賞品
#どっちか選択
sold_out = True
on_sale = False

# 最後のページ
last_page_num = 100

#spreadsheetに保存する変数たち
year = 0
AP = 0
memory = 0
season = 0
HDD = 0
inch = 0
state_state = 0
Day = 0
price = 0
goods_url = 0

# 以下で定義する変数が、本文中やタイトルの中にあるかチェックする。
# Macbook Air or Macbook Pro
text_AorP = [   {"key":1, "val":[u'Air', u'air', u'エアー']},
                {"key":2, "val":[u'Pro', u'pro', u'プロ']}
             ]

# モデル（年式）
text_year = [   {"key":2008, "val":[u'2008', u'２００８']},
                {"key":2009, "val":[u'2009', u'２００９']},
                {"key":2010, "val":[u'2010', u'２０１０']},
                {"key":2011, "val":[u'2011', u'２０１１']},
                {"key":2012, "val":[u'2012', u'２０１２']},
                {"key":2013, "val":[u'2013', u'２０１３']},
                {"key":2014, "val":[u'2014', u'２０１４']},
                {"key":2015, "val":[u'2015', u'２０１５']},
                {"key":2016, "val":[u'2016', u'２０１６']}
              ]

# Early or Middle or Late
text_EML = [    {"key":1, "val":[u'Early', u'early']},
                {"key":2, "val":[u'Mid', u'mid']},
                {"key":3, "val":[u'Late', u'late']}
             ]

# HDDやSSDの容量
text_capacity =[{"key":64, "val":[u'64G' , u'６４G'  ,u'64g', u'６４g',u'64 G'   , u'６４ G'  ,  u'64 g', u'６４ g']},
                {"key":80, "val":[u'80G', u'８０G',u'80g', u'８０g', u'80 G', u'８０ G', u'80 g', u'８０ g']},
                {"key":120, "val":[u'120G', u'１２０G',u'120g', u'１２０g', u'120 G', u'１２０ G', u'120 g', u'１２０ g']},
                {"key":121, "val":[u'121G', u'１２１G',u'121g', u'１２１g', u'121 G', u'１２１ G', u'121 g', u'１２１ g']},
                {"key":128, "val":[u'128G', u'１２８G',u'128g', u'１２８g', u'128 G', u'１２８ G', u'128 g', u'１２８ g']},
                {"key":160, "val":[u'160G', u'１６０G',u'160g', u'１６０g', u'160 G', u'１６０ G', u'160 g', u'１６０ g']},
                {"key":250, "val":[u'250G', u'２５０G',u'250g', u'２５０g', u'250 G', u'２５０ G', u'250 g', u'２５０ g']},
                {"key":256, "val":[u'256G', u'２５６G',u'256g', u'２５６g', u'256 G', u'２５６ G', u'256 g', u'２５６ g']},
                {"key":297, "val":[u'297G', u'２９７G',u'297g', u'２９７g', u'297 G', u'２９７ G', u'297 g', u'２９７ g']},
                {"key":320, "val":[u'320G', u'３２０G',u'320g', u'３２０g', u'320 G', u'３２０ G', u'320 g', u'３２０ g']},
                {"key":480, "val":[u'480G', u'４８０G',u'480g', u'４８０g', u'480 G', u'４８０ G', u'480 g', u'４８０ g']},
                {"key":500, "val":[u'500G', u'５００G',u'500g', u'５００g', u'500 G', u'５００ G', u'500 g', u'５００ g']},
                {"key":512, "val":[u'512G', u'５１２G',u'512g', u'５１２g', u'512 G', u'５１２ G', u'512 g', u'５１２ g']},
                {"key":1000, "val":[u'1T', u'１T',u'1t', u'１t', u'1 T', u'１ T', u'1 t', u'１ t']}
                 ]

# モニターのインチ数
text_inch = [  {"key":11, "val":[u'11-inch', u'11inch', u'11 inch', u'１１inch', u'11inch', u'11 inch', u'１１inch', u'１１　inch', u'１１-inch', u'11インチ', u'１１インチ', u'11.6', u'１１．６', u'Air 11', u'Air11', u'air 11', u'air11']},
                {"key":12, "val":[u'12-inch', u'12inch', u'12 inch', u'１２inch', u'１２　inch', u'１２-inch', u'12インチ', u'１２インチ']},
                {"key":13, "val":[u'13-inch', u'13inch', u'13 inch', u'１３inch', u'１３　inch', u'１３-inch', u'13インチ', u'１３インチ', u'13.3', u'１３．３', u'Air 13', u'Retina 13', u'Pro 13', u'Air13', u'Retina13', u'Pro13', u'retina 13', u'pro 13', u'air13', u'retina13', u'pro13']},
                {"key":15, "val":[u'15-inch' , u'15inch' , u'15 inch' , u'１５inch' , u'１５　inch' , u'１５-inch' , u'15インチ' , u'１５インチ' , u'15.4' , u'１５．４' , u'Pro 15' , u'Retina 15' , u'Pro15', u'Retina15',u'pro 15',u'retina 15',u'pro15',u'retina15']},
                {"key":17, "val":[u'17inch' , u'17 inch' , u'１７inch' , u'１７　inch' , u'１７-inch' , u'17インチ' , u'１７インチ' , u'17inch' , u'17 inch' , u'１７inch' , u'１７　inch' , u'１７-inch' , u'17インチ' , u'１７インチ']},
                 ]

# 商品の状態
text_state = [  {"key":1, "val":[u'<td>新品、未使用</td>']},
                    {"key":2, "val":[u'<td>未使用に近い</td>']},
                    {"key":3, "val":[u'<td>目立った傷や汚れなし</td>']},
                    {"key":4, "val":[u'<td>やや傷や汚れあり</td>']},
                    {"key":5, "val":[u'<td>傷や汚れあり</td>']},
                    {"key":6, "val":[u'<td>全体的に状態が悪い</td>']}
                 ]

#spreadsheet用
SCOPES = "https://www.googleapis.com/auth/gmail.send"
CLIENT_SECRET_FILE = "client_secret.json"
APPLICATION_NAME = "MyGmailSender"

MAIL_FROM = "yuppppppppppqii@gmail.com"
# MAIL_TO = "yuppppppppppqi@gmail.com, omori-tomohiro-sd@ynu.jp" #大森さんにも送る場合
MAIL_TO = "yuppppppppppqi@gmail.com"

# gmail用の関数（現在は使っていないが、いい商品が出たら通知）
def mail_sender(MyText):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build("gmail", "v1", http=http)
    try:
        result = service.users().messages().send(
            userId=MAIL_FROM,
            body=create_message(MyText)
        ).execute()

        print("Message Id: {}".format(result["id"]))

    except apiclient.errors.HttpError:
        print("------start trace------")
        traceback.print_exc()
        print("------end trace------")

# HTML取得関数
def URLOpener(url):
    opener = urllib2.build_opener()
    return opener.open(url)

def main_func():
    # spreadsheet関係
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('mercari7-39c96ad9fafc.json', scope)
    gc = gspread.authorize(credentials)
    sh = gc.open("mercari6").worksheet("mac")

    # https://www.mercari.com/jp/search/?page=2&keyword=macbook&sort_order=&category_root=7&category_child=96&category_grand_child[840]=1&brand_name=&brand_id=&size_group=&price_min=&price_max=&status_trading_sold_out=1
    # https://www.mercari.com/jp/search/?page=2&keyword=macbook&sort_order=&category_root=7&category_child=96&category_grand_child[840]=1&brand_name=&brand_id=&size_group=&price_min=&price_max=&status_on_sale=1

    # 各<div>の中（つまり、各商品ページ）を詳しく見ていく
    for var in range(0, last_page_num):
        print(var+1)
        cell_list = sh.range(var*48+1+1, 1, (var+1)*48+1, 10)
        if(sold_out):
            alz_URL = "https://www.mercari.com/jp/search/?page=" + str(var+1) + "&keyword=macbook&sort_order=&category_root=7&category_child=96&category_grand_child[840]=1&brand_name=&brand_id=&size_group=&price_min=&price_max=&status_trading_sold_out=1"
        elif(on_sale):
            alz_URL = "https://www.mercari.com/jp/search/?page=" + str(var+1) + "&keyword=macbook&sort_order=&category_root=7&category_child=96&category_grand_child[840]=1&brand_name=&brand_id=&size_group=&price_min=&price_max=&status_on_sale=1"
        else:
            print("EROOR")

        html = URLOpener(alz_URL)
        soup = BeautifulSoup(html, "lxml")
        # HTMLの<div>タグを見つけてくる（各商品ページがある）
        divs = soup.find('div', class_="items-box-content clearfix").find_all('section', class_ = 'items-box')
        i=0
        for div in divs:
            goods_url =  div.find("a").get('href') #商品一覧ページから、各商品ページのURLを取得
            html = URLOpener(goods_url)
            soup = BeautifulSoup(html, "lxml")

            title = str(soup.find('section', class_="item-box-container").find("h2")).replace("<h2 class=\"item-name\">", "").replace("</h2>", "").decode('utf8')
            text  = str(soup.find('section', class_="item-box-container").find('div', class_="item-description f14")).decode('utf8')
            state = str(soup.findAll('td')[3])
            price  = str(soup.find('section', class_="item-box-container").find('span', class_="item-price bold")).replace(" ", "").replace("¥", "").replace(",", "").replace("<spanclass=\"item-pricebold\">", "").replace("</span>", "")
            day  = soup.find('div', class_="message-icons clearfix")

            cell_list[i*10].value = check_text(title, text, text_year)
            cell_list[i*10+1].value = check_text(title, text, text_AorP)
            cell_list[i*10+2].value = check_memory(title, text)
            cell_list[i*10+3].value = check_text(title, text, text_EML)
            cell_list[i*10+4].value = check_text(title, text, text_capacity)
            cell_list[i*10+5].value = check_text(title, text, text_inch)
            cell_list[i*10+6].value = check_state(state)
            cell_list[i*10+7].value = check_day(day)
            cell_list[i*10+8].value = price
            cell_list[i*10+9].value = goods_url
            i+=1

        sh.update_cells(cell_list) #spreadsheetに配列を保存

    print(datetime.now().strftime("%Y/%m/%d %H:%M:%S")) #終了時刻表示

# タイトル、本文の中に、見たい文字列が存在するかチェック
def check_text(title, text, check_text):
    ans = 0
    for v1 in check_text:
        for v2 in v1["val"]:
            if(v2 in title) or (v2 in text):
                ans = v1["key"]
    return ans

# def check_memory(title, text):
#     memory = 0
#     if((u'8G' in title or u'８G' in title or u'8 G' in title or u'８ G' in title) or (u'8G' in text or u'８G' in text or u'8 G' in text or u'８ G' in text)):
#         # print("a")
#         for x in range(0, len(title)-2):
#             if(((title[x]!=u"2" and title[x+1]==u"8" and title[x+2]==u"G") or (title[x]!=u"２" and title[x+1]==u"８" and title[x+2]==u"G") or (title[x]!="2" and title[x+1]==u"8" and title[x+2]==u" ")) or ((text[x]!=u"2" and text[x+1]==u"8" and text[x+2]==u"G") or (text[x]!=u"２" and text[x+1]==u"８" and text[x+2]==u"G") or (text[x]!="2" and text[x+1]==u"8" and text[x+2]==u" "))):
#                 memory = 8
#                 break
#     if((u'2G' in title or u'２G' in title or u'2 G' in title or u'２ G' in title in title) or (u'8G' in text or u'８G' in text or u'8 G' in text or u'８ G' in text)):
#         # print("a")
#         for x in range(0, len(title)-2):
#             if(((title[x]!=u"1" and title[x+1]==u"2" and title[x+2]==u"G") or (title[x]!=u"１" and title[x+1]==u"２" and title[x+2]==u"G") or (title[x]!="1" and title[x+1]==u"2" and title[x+2]==u" ")) or ((text[x]!=u"1" and text[x+1]==u"2" and text[x+2]==u"G") or (text[x]!=u"１" and text[x+1]==u"２" and text[x+2]==u"G") or (text[x]!="1" and text[x+1]==u"2" and text[x+2]==u" "))):
#                 memory = 2
#                 break
#     if((u'4G' in title or u'４G' in title or u'4 G' in title or u'４ G' in title) or (u'4G' in text or u'４G' in text or u'4 G' in text or u'４ G' in text)):
#         memory = 4
#     elif((u'16G' in title or u'１６' in title or u'16 G' in title or u'１６ G' in title) or (u'16G' in text or u'１６' in text or u'16 G' in text or u'１６ G' in text)):
#         memory = 16
#     else:
#         memory = 0
#     return memory

# メモリの容量をチェック
def check_memory(title, text):
    if(u'8G' in title):
        # print("a")
        for x in range(0, len(title)-2):
            if(title[x]!=u"2" and title[x+1]==u"8" and title[x+2]==u"G"):
                memory = 8
                break
    elif(u'８G' in title):
        # print("b")
        for x in range(0, len(title)-2):
            if(title[x]!=u"２" and title[x+1]==u"８" and title[x+2]==u"G"):
                memory = 8
                break
    elif(u'8G' in text):
        # print("c")
        for x in range(0, len(text)-2):
            if(text[x]!=u"2" and text[x+1]==u"8" and text[x+2]==u"G"):
                memory = 8
                break
    elif(u'８G' in text):
        # print("d")
        for x in range(0, len(text)-2):
            if(text[x]!=u"２" and text[x+1]==u"８" and text[x+2]==u"G"):
                memory = 8
                break
    elif(u'8 G' in title):
        # print("e")
        for x in range(0, len(title)-2):
            if(title[x]!="2" and title[x+1]==u"8" and title[x+2]==u" "):
                memory = 8
                break
    elif(u'８ G' in title):
        # print("f")
        for x in range(0, len(title)-2):
            if(title[x]!=u"２" and title[x+1]==u"８" and title[x+2]==u" "):
                memory = 8
                break
    elif(u'8 G' in text):
        # print("g")
        for x in range(0, len(text)-2):
            if(text[x]!=u"2" and text[x+1]==u"8" and text[x+2]==u" " and text[x+3]==u"G"):
                memory = 8
                break
    elif(u'８ G' in text):
        # print("h")
        for x in range(0, len(text)-2):
            if(text[x]!=u"２" and text[x+1]==u"８" and text[x+2]==u" " and text[x+3]==u"G"):
                memory = 8
                break

    if(u'2G' in title):
        # print("a")
        for x in range(0, len(title)-2):
            if(title[x]!=u"1" and title[x+1]==u"2" and title[x+2]==u"G"):
                memory = 2
                break
    elif(u'２G' in title):
        # print("b")
        for x in range(0, len(title)-2):
            if(title[x]!=u"１" and title[x+1]==u"２" and title[x+2]==u"G"):
                memory = 2
                break
    elif(u'2G' in text):
        # print("c")
        for x in range(0, len(text)-2):
            if(text[x]!=u"1" and text[x+1]==u"2" and text[x+2]==u"G"):
                memory = 2
                break
    elif(u'２G' in text):
        # print("d")
        for x in range(0, len(text)-2):
            if(text[x]!=u"１" and text[x+1]==u"２" and text[x+2]==u"G"):
                memory = 2
                break
    elif(u'2 G' in title):
        # print("e")
        for x in range(0, len(title)-2):
            if(title[x]!="1" and title[x+1]==u"2" and title[x+2]==u" "):
                memory = 2
                break
    elif(u'２ G' in title):
        # print("f")
        for x in range(0, len(title)-2):
            if(title[x]!=u"１" and title[x+1]==u"２" and title[x+2]==u" "):
                memory = 2
                break
    elif(u'2 G' in text):
        # print("g")
        for x in range(0, len(text)-2):
            if(text[x]!=u"1" and text[x+1]==u"2" and text[x+2]==u" "):
                memory = 2
                break
    elif(u'２ G' in text):
        # print("h")
        for x in range(0, len(text)-2):
            if(text[x]!=u"１" and text[x+1]==u"２" and text[x+2]==u" "):
                memory = 2
                break
    elif(u'4G' in title):
        memory = 4
    elif(u'４G' in title):
        memory = 4
    elif(u'16G' in title):
        memory = 16
    elif(u'１６G' in title):
        memory = 16
    elif(u'4G' in text):
        memory = 4
    elif(u'４G' in text):
        memory = 4
    elif(u'16G' in text):
        memory = 16
    elif(u'１６G' in text):
        memory = 16
    elif(u'4 G' in title):
        memory = 4
    elif(u'４ G' in title):
        memory = 4
    elif(u'16 G' in title):
        memory = 16
    elif(u'１６ G' in title):
        memory = 16
    elif(u'2 G' in text):
        memory = 2
    elif(u'２ G' in text):
        memory = 2
    elif(u'4 G' in text):
        memory = 4
    elif(u'４ G' in text):
        memory = 4
    elif(u'16 G' in text):
        memory = 16
    elif(u'１６ G' in text):
        memory = 16

# 商品の状態をチェック
def check_state(state):
    if(u'<td>新品、未使用</td>' in state.decode('utf8')):
        state_state = 1
    elif(u'<td>未使用に近い</td>' in state.decode('utf8')):
        state_state = 2
    elif(u'<td>目立った傷や汚れなし</td>' in state.decode('utf8')):
        state_state = 3
    elif(u'<td>やや傷や汚れあり</td>' in state.decode('utf8')):
        state_state = 4
    elif(u'<td>傷や汚れあり</td>' in state.decode('utf8')):
        state_state = 5
    elif(u'<td>全体的に状態が悪い</td>' in state.decode('utf8')):
        state_state = 6
    else:
        state_state = 0
    return state_state

# 最近のコメントの日時
def check_day(day):
    if(day != None):
        if(u'時間前' or u'分前' or u'秒前' in str(soup.find('div', class_="message-icons clearfix").find('span')).decode('utf8')):
            Day = 0
        elif(u'日前' in str(day.find('span')).decode('utf8')):
            Day = str(day.find('span')).replace(" 日前", "").replace("<span>", "").replace("</span>", "")
    else:
        Day = -1
    return Day

if __name__=='__main__':
    main_func()
