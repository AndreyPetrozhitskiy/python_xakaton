import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, jsonify

from livereload import Server



app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

def init_db():
    conn = sqlite3.connect('memory_pages.db')
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS memory_pages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        war TEXT NOT NULL,
        story TEXT NOT NULL,
        cover TEXT NOT NULL,
        photos TEXT,
        videos TEXT,
        audios TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        memory_page_id INTEGER,
        nickname TEXT NOT NULL,
        comment TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        war = request.form['war']
        story = request.form['story']
        cover_file = request.files['cover']
        cover_filename = None
        if cover_file and cover_file.filename:
            cover_filename = f"cover_{name}_{cover_file.filename}"
            cover_file.save(os.path.join(app.config['UPLOAD_FOLDER'], cover_filename))
        else:
            return "Титульное изображение обязательно", 400

        # Прочие фото
        photos = []
        for photo in request.files.getlist('photos'):
            if photo and photo.filename:
                filename = f"photo_{name}_{photo.filename}"
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                photos.append(filename)
        # Видео
        videos = []
        for video in request.files.getlist('videos'):
            if video and video.filename:
                filename = f"video_{name}_{video.filename}"
                video.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                videos.append(filename)
        # Аудио
        audios = []
        for audio in request.files.getlist('audios'):
            if audio and audio.filename:
                filename = f"audio_{name}_{audio.filename}"
                audio.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                audios.append(filename)

        conn = sqlite3.connect('memory_pages.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO memory_pages (name, war, story, cover, photos, videos, audios)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            name, war, story, cover_filename,
            ','.join(photos), ','.join(videos), ','.join(audios)
        ))
        conn.commit()
        conn.close()
        return redirect('/')

    # Вывод карточек
    conn = sqlite3.connect('memory_pages.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM memory_pages ORDER BY created_at DESC')
    monuments = c.fetchall()
    # Получаем комментарии для каждой карточки
    comments_dict = {}
    for row in monuments:
        c.execute('SELECT nickname, comment FROM comments WHERE memory_page_id=? ORDER BY created_at', (row['id'],))
        comments_dict[row['id']] = c.fetchall()
    conn.close()
    return render_template('main.html', monuments=monuments, comments_dict=comments_dict)

@app.route('/comments/<int:page_id>', methods=['GET', 'POST'])
def comments(page_id):
    conn = sqlite3.connect('memory_pages.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if request.method == 'POST':
        nickname = request.form['nickname']
        comment = request.form['comment']
        c.execute('INSERT INTO comments (memory_page_id, nickname, comment) VALUES (?, ?, ?)', (page_id, nickname, comment))
        conn.commit()
    c.execute('SELECT nickname, comment FROM comments WHERE memory_page_id=? ORDER BY created_at', (page_id,))
    comments = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(comments)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    init_db()

    server = Server(app.wsgi_app)
    server.watch('templates/**/*.html')
    server.watch('static/')
    server.serve(port=5000, debug=True, open_url_delay=1)
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store'
    return response

    app.run(debug=True)

