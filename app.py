import os, zipfile
from libs.utils import create_inserts, allowed_file
from libs.files_manipulator import remove_dir, extract_kmz, create_dir_structure
from libs.sql_generators import final_insert_sql, create_table_sql
from libs.views import upload_view
from flask import Flask, flash, request, redirect, send_from_directory
from werkzeug.utils import secure_filename
from random import getrandbits

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'in'
app.config['TEMP_FOLDER'] = 'temp'
app.config['OUT_FOLDER'] = 'out'


@app.route('/', methods=['GET'])
def reroute():
    return redirect('/upload')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'table' not in request.form and 'buffer' not in request.form:
            flash('POST sem nome e tamanho do buffer!')
            return redirect(request.url)

        folder_name_hash_id = str(getrandbits(32))

        upload_folder, temp_folder, out_folder = create_dir_structure(app, folder_name_hash_id)
        table_name = request.form['table']
        buffer = int(request.form['buffer'])
        aggregate = request.form.get('aggregate')
        if 'file' not in request.files:
            flash('Sem parte arquivo!')
            return redirect(request.url)
        file = request.files['file']
        filename = secure_filename(file.filename)
        if filename == '':
            flash('Arquivo não escolhido!')
            return redirect(request.url)

        if allowed_file(filename):
            file.save(os.path.join(upload_folder, filename))

            with zipfile.ZipFile(os.path.join(upload_folder, filename), 'r') as zip_ref:
                zip_ref.extractall(upload_folder)
                os.remove(os.path.join(upload_folder, filename))

            extract_kmz(upload_folder, temp_folder)
            sql_inserts = create_inserts(temp_folder, table_name, buffer)
            remove_dir(upload_folder)
            remove_dir(temp_folder)

            with open(out_folder + '/' + 'insert.sql', 'w+') as f:
                f.write('BEGIN;\n')
                f.write(create_table_sql(table_name, True))
                f.write(sql_inserts)
                f.write(create_table_sql(table_name, False))
                f.write(final_insert_sql(table_name,aggregate))
                f.write('COMMIT;\n')

            return redirect('/uploads/' + folder_name_hash_id + '/out/' + 'insert.sql')

    return upload_view()


@app.route('/uploads/<foldername>/out/<filename>', methods=['GET', 'POST'])
def uploaded_file(foldername, filename):
    return send_from_directory(os.path.join('temp', foldername, 'out'),
                               filename)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
