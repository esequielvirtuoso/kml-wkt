import os, zipfile, shutil


def create_dir(dir_path):
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)


def remove_dir(dir_path):
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)


def extract_kmz(upload_folder, temp_folder):
    for filename in os.listdir(upload_folder):
        if filename.lower().endswith(".kmz"):
            with zipfile.ZipFile(os.path.join(upload_folder, filename), 'r') as zip_ref:
                zip_ref.extractall(temp_folder)
                shutil.move(temp_folder + '/doc.kml', temp_folder + '/' + filename.split('.')[0] + '.kml')
        elif filename.lower().endswith(".kml"):
            shutil.copy(os.path.join(upload_folder, filename), os.path.join(temp_folder, filename))


def create_dir_structure(app, folder_name_hash_id):
    upload_folder = './temp/' + folder_name_hash_id + '/' + app.config['UPLOAD_FOLDER']
    temp_folder = './temp/' + folder_name_hash_id + '/' + app.config['TEMP_FOLDER']
    out_folder = './temp/' + folder_name_hash_id + '/' + app.config['OUT_FOLDER']
    create_dir('./temp/' + folder_name_hash_id)
    create_dir(upload_folder)
    create_dir(temp_folder)
    create_dir(out_folder)
