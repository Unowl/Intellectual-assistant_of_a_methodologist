
from flask import Flask, request, render_template, send_file
from pymongo import MongoClient
import gridfs
import os
import pandas as pd
from bson.objectid import ObjectId


app = Flask(__name__, template_folder=os.path.abspath('templates'))


client = MongoClient('mongodb://localhost:27017/')
db = client['mydb']
fs = gridfs.GridFS(db)

@app.route('/', methods=['GET', 'POST'])
def upload_and_process():
    if request.method == 'POST':
        
        file = request.files['file']
        if file:
            file_id = fs.put(file.stream, filename=file.filename)#загружает в базу данных
            #передает в pypline.py
            return f"File saved with ID {file_id}"
            
        else:
            return "No file uploaded"
    #место для передачи из базы данных в handler.py и возвращение файла к базе данных
    else:
        
        return render_template('upload.html')


@app.route('/list')
def list_entries():
   
    entries = db.fs.files.find()
    return render_template('list.html', entries=entries)

@app.route('/download/<file_id>')
def download_file(file_id):
    file = fs.get(ObjectId(file_id))
    
    return send_file(file, download_name ='music.mp3', as_attachment=True, mimetype='audio/mpeg')

@app.route('/download_word')
def download_word():
    file_path = os.path.join(app.root_path, 'summary_world.docx')
    return send_file(file_path, download_name='конспект.docx', as_attachment=True)

timecode = pd.read_csv('res6.csv')

def find_term(term, timecode):
    s = []
    for index, row in timecode.iterrows():
        if (term in row['text'].split()):
            s.append( str(int(row['start'] // 60)) + ' мин ' + str(int(row['start'] % 60)) + ' сек')
    return s

@app.route('/search', methods=['GET', 'POST'])
def search():
    results = []
    if request.method == 'POST':
        term = request.form['search_term']
        results = find_term(term, timecode)
    return render_template('search.html', results=results)


@app.route('/delete/<file_id>', methods=['POST'])
def delete_file(file_id):
    fs.delete(ObjectId(file_id))
    entries = db.fs.files.find()
    return render_template('list.html', entries=entries)
if __name__ == '__main__':
    app.run(debug=True)