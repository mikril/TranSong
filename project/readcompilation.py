import sqlite3
import json

def get_compilation(compilation_id):
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM compilations WHERE id = ?", (compilation_id,))
        compilation = cursor.fetchall()[0]
        tags = compilation[1]
        name = compilation[2]
        photo_url = compilation[4]
        songs_id = json.loads(compilation[3])
        songs = compilation[3]
        author = compilation[5]
    return {"name": name, "songs_id": songs_id, "photo_url": photo_url, "author": author, "tags": tags, "songs": songs}

def get_song(song_id):
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM songs WHERE id = ?", (song_id,))
        song = cursor.fetchall()[0]
        name = song[1]
        url = song[2]
        author = song[3]
        featuring = song[4]
        translated_parts = song[8]
        translated_lyrics= song[9]
    return {"name": name, 
            "url": url,
            "author": author,
            "featuring": featuring,
            "translated_parts": translated_parts,
            "translated_lyrics":translated_lyrics}

def get_all_songs(compilation_id):
    compilation = get_compilation(compilation_id)
    songs = []
    for song_id in compilation["songs_id"]:
        songs.append(get_song(song_id))
    return songs

def get_all_compilations(args):
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        if not args:
            cursor.execute("SELECT name, id, photo_url, author, songs_id, tags FROM compilations")
        else:
            statement = ""
            for arg in args:
                statement += " tags" + " LIKE " + f"'%{arg}%'" + " AND"
            cursor.execute("SELECT name, id, photo_url, author, songs_id, tags FROM compilations WHERE " + statement[:-3])
    return cursor.fetchall()

def delete_compilation(username, compilation_id):
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, author FROM compilations WHERE id = ?", (compilation_id,))
        compilation = cursor.fetchall()[0]
        if compilation[1] == username:
            cursor.execute("DELETE FROM compilations WHERE id = ?", (compilation_id,))
            return True
        return False


def get_user_compilations(author_id):
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        name_author = cursor.execute("SELECT name FROM users WHERE id = ?", (author_id,))
        name_author = name_author.fetchone()[0]
        cursor.execute("SELECT name, id, photo_url, author, songs_id, tags FROM compilations WHERE author = ?", (name_author, ))
    return cursor.fetchall()

def create_compilation(tags, name, songs_url, photo_url, author_id):
    songs_url = ",".join(f"'{w}'" for w in songs_url)
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute(f"""SELECT id FROM songs WHERE url IN ({songs_url})""")
        ids = list(x[0] for x in cursor.fetchall())
        name_author = cursor.execute("SELECT name FROM users WHERE id = ?", (author_id,))
        name_author = name_author.fetchone()[0]
        cursor.execute("INSERT INTO compilations (tags, name, songs_id, photo_url, author) VALUES (?, ?, ?, ?, ?)", (str(tags), name, str(ids), photo_url, name_author))


def addUser(name, email, hpsw):
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(f"SELECT COUNT() as 'count' FROM users WHERE email LIKE '{email}'")
            res = cursor.fetchone()
            if res[0] > 0:
                print("Пользователь с таким email уже существует")
                return False
            cursor.execute(f"SELECT COUNT() as 'count' FROM users WHERE name LIKE '{name}'")
            res = cursor.fetchone()
            if res[0] > 0:
                print("Пользователь с таким именем уже существует")
                return False
            cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, hpsw,))

        except sqlite3.Error as e:
            print("Ошибка добавления пользователя в БД " + str(e))
            return False
        return True

def getUser(user_id):
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(f"SELECT * FROM users WHERE id = {user_id} LIMIT 1")
            res = cursor.fetchone()
            if not res:
                print("Пользователь не найден")
                return False
            return res

        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))
        return False

def getUserByEmail(email):
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(f"SELECT * FROM users WHERE email = '{email}' LIMIT 1")
            res = cursor.fetchone()
            if not res:
                print("Пользователь не найден")
                return False
            return res

        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))
        return False