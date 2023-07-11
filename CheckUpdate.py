import requests
from bs4 import BeautifulSoup
import time
import os
from deta import Deta
from datetime import datetime
import json
import tweepy
print("library loaded")
newsresponse = requests.get("https://www.innersloth.com/wp-admin/admin-ajax.php?action=am_get_posts_by_category&category_id=70&page=1&lang=en")
print("connected")
def getnews(url):
    pageresponse = requests.get(url)
    soup = BeautifulSoup(pageresponse.text, "html.parser")
    result = {}
    result["url"] = url
    result["code"] = pageresponse.status_code
    result["response"] = pageresponse
    result["title"] = soup.find(attrs={"class":"news-detail_entry"}).text
    result["postauthor"] = soup.find(attrs={"class":"post-author"}).text
    result["detailsoup"] = soup.find(attrs={"class":"news-detail_content"})
    result["detailtext"] = BeautifulSoup(str(result["detailsoup"]).replace("\n","").replace("<br>","\n").replace("<br/>","\n").replace("</p>","\n").replace("<li>","<li>・").replace("</li>","</li>\n"), "html.parser").text
    result["detailhtml"] = str(result["detailsoup"])
    return result
db=Deta(os.environ.get("SNRDETATOKEN","")).Base("NewsStatus")
NEWS_SAISIN = db.get("saisin")["value"]
while True:
    if datetime.utcnow().minute > 20:
        continue
    nsoup = BeautifulSoup(newsresponse.json()["html"], "html.parser")
    items = nsoup.find_all(attrs={ 'class': "news-list_item" })
    if items[0].find("a").get("href") != NEWS_SAISIN:
        break
    time.sleep(30)
print("最新あったよ。:"+items[0].find("a").get("href"))
def send_webhook(target,text,name=None,avater=None):
    webhook_url  = os.environ.get(target,"")
    main_content = {'content': text,
                    'avatar_url':"https://raw.githubusercontent.com/ykundesu/SuperNewRoles/master/SuperNewRoles/Resources/TabIcon.png"}
    if name is not None:
        main_content["username"] = name
    headers      = {'Content-Type': 'application/json'}
    print(requests.post(webhook_url, json.dumps(main_content), headers=headers).text)
send_webhook("SNRKAIHATUNEWS",
             "<@&1005982727050383390>\n新しいニュースが投稿された。\n"+items[0].find("a").get("href"),
             "SuperNewRolesおしらせくん")
text = """【公式アップデートのお知らせ】
※これは自動アナウンスです。情報には誤りがある場合がございます。
現在、公式アップデートのお知らせ(と見られる)記事がAmongUs公式より公開されました。
おそらく本体はアップデートされており、現在互換性についての調査を行っています。

対応版SNRをリリースするまでは
AmongUs ver 2023.6.13 + SNR v1.8.1.3 などを使用する事を推奨します。

この場合のバグ対応及び質問対応は致しません。
該当記事："""+items[0].find("a").get("href")+"\nクルーメイトかわいい\nもちもち\n\nSuperNewRolesくん(よっキング)"
send_webhook("SNRSERVERNEWS",
             "<@&1055729986809638922>\n"+text,
             "SuperNewRolesくん"
             )
CONSUMER_KEY = os.environ.get('CONSUMER_KEY', "")
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET', "")
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN', "")
ACCESS_SECRET = os.environ.get('ACCESS_SECRET', "")
client = tweepy.Client(
	consumer_key = CONSUMER_KEY,
	consumer_secret = CONSUMER_SECRET,
	access_token = ACCESS_TOKEN,
	access_token_secret = ACCESS_SECRET
)
text = """【公式アップデートのお知らせ】
※これは自動アナウンスです。情報には誤りがある場合がございます。
やあ、公式アップデートのお知らせっぽい記事が公開されたよ。
多分本体アップデートされてて、今互換性について調べてるよ。"""
tweetid = client.create_tweet(text=text).data["id"]
text = """
多分対応してないからリリース待ってや。詳しくはDiscord見てな。
"""+items[0].find("a").get("href")+"\nクルーメイトかわいい。もちもち"
client.create_tweet(text=text,in_reply_to_tweet_id=tweetid)
#for a in items:
    #print("ーーーーー")
    #print(a.find(attrs={'class':"news-list_heading"}).text)
    #print(getnews()["detailtext"])
    #print("ーーーーー")
db.put({"key":"saisin","value":items[0].find("a").get("href")}, "saisin")
