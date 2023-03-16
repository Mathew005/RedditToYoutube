from instascrape import Reel

SESSIONID = "186e0cafe32-aa7336"

headers =  {
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.74 Safari/537.36 Edg/79.0.309.43",
"cookie":f'sessionid={SESSIONID};'
}

insta_reel = Reel("https://www.instagram.com/reels/CoFYA12jKKO/")
insta_reel.scrape(headers=headers)

insta_reel.download("file.mp4")