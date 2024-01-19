from bs4 import BeautifulSoup
import requests
import re
from googletrans import Translator
import sqlite3
import json
from time import sleep

token = "debM231y_RrM5ntppbOD44_PMDjKhoi7eCq6MJTugV3_uem5TYVWJWRRXFEq1xV8"

class Song:
    def __init__(self, url):
        self.url = url
        self.parse_song()
        self._get_parts()
        self._translate_parts()
        self.clean_lyrics = self.clean_lyrics.replace(f"[[{self.parts_names[0]}]", "")

    def parse_song(self):
        page = requests.get(self.url)
        soup = BeautifulSoup(page.text, "html.parser")
        self.lyrics = soup.findAll('div',attrs={'data-lyrics-container':'true'})

            
        self.song_id = soup.find('meta',attrs={'property': "twitter:app:url:iphone"})["content"].split("/")[-1]
        url = f"https://api.genius.com/songs/{int(self.song_id)}?access_token={token}"
        print(self.song_id)
        result = requests.get(url).json()["response"]["song"]
        self.song_name = result["title"]
        print(self.song_name)
        self.authors = list(result["primary_artist"]["name"].replace("\u200b","").replace("&", ",").split(','))
        self.parts_names = []
        print(self.authors)
        for part in self.lyrics:
            self.parts_names += re.findall(r'\[([^\[\]]+)\]', part.text.replace("'", ""))
        self.featuring = []
        print(self.parts_names)
        for artist in result["featured_artists"]:
            self.featuring.append(artist["name"])
        print(self.featuring)
        self.clean_lyrics = self.cleanhtml(str(self.lyrics).replace("<br/>", "\n")).replace("&amp;", "&")
        print("clean_lyrics")
        self.parts_names = self.parts_names[1:]
        self.translated_lyrics = self.translate(self.clean_lyrics)
        print(self.translated_lyrics)

        self.tags = [] # TODO: Добавление тегов вручную при создании песни

    def __str__(self) -> str:
        return f'{self.song_name}, {self.authors}, {self.featuring}'

    def get_lyrics(self):
        return self.lyrics

    def cleanhtml(self, raw_html):
        cleantext = re.sub(re.compile('<.*?>') , '', raw_html)
        return cleantext

    def get_part_type(self, part_name):
        try:
            if "бридж" in part_name.lower() or "bridge" in part_name.lower():
                part_type = "bridge"
            elif "предприпев" in part_name.lower() or "pre-chorus" in part_name.lower() or "refrain" in part_name.lower() or "instrumental break" in part_name.lower():
                part_type = "prechorus"
            elif "припев" in part_name.lower() or "chorus" in part_name.lower():
                part_type = "chorus"
            elif "интро" in part_name.lower() or "intro" in part_name.lower():
                part_type = "intro"
            elif "аутро" in part_name.lower() or "outro" in part_name.lower():
                part_type = "outro"
            elif "куплет" in part_name.lower() or "verse" in part_name.lower():
                part_type = "verse"
            return part_type
        except:
            return ""

        

    def _get_parts(self):
        parts = []
        parts_split = self.clean_lyrics.split("[")[2:]
        for part_numb in range(len(parts_split)):
            part = parts_split[part_numb]
            part_name = re.findall(r'\[([^\[\]]+)\]', "[" + part)[0]
            if "song" in part_name or "песни" in part_name or "lyrics" in part_name or "текст" in part_name:
                continue
            parts.append({"type": self.get_part_type(part_name), "text": re.sub(r'\[([^\[\]]+)\]', "", "[" + part)})
        self.parts = parts

    def translate(self, text):
        translator = Translator()
       
        langs = ['zh-CN', 'it', 'ja', 'mn', 'ru']
        print( translator)
        for lang in langs:
            text = translator.translate(text, dest=lang).text
        return text

    def _translate_parts(self):
        self.translated_parts = []
        for part in self.parts:
            self.translated_parts += [{"type": part["type"], "text": self.translate(part["text"])}]

class Compilation:
    def __init__(self, links):
        self.links = links
        self.tags = []

def create_song(x):
    for i in range(10):
        try:
            return Song(x)
        except Exception as e:
            print("ошибка: ",e)
            sleep(21212)

def get_songs(songs_url):
    songs = []
    print("url: ",songs_url)
    for song in songs_url:
        song = create_song(song)
        if song != None:
            songs.append(song)
    return songs

def add_songs(songs):
    songs = get_songs(songs)
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        for song in songs:
            urlSong = song.url
            cursor.execute("SELECT url FROM songs WHERE url = ?", (urlSong,))
            if cursor.fetchone() is None:
                cursor.execute("""
                INSERT INTO songs (name, url, authors, featuring, lyrics, tags, parts, translated_parts, translated_lyrics)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (str(song.song_name), str(song.url), str(song.authors), str(song.featuring), song.clean_lyrics,
                str(song.tags), json.dumps(song.parts, ensure_ascii=False),
                json.dumps(song.translated_parts, ensure_ascii=False), song.translated_lyrics),)
    print("added")