def upload_view():
    return '''
        <!doctype html>
        <title>Carregar arquivo KML</title>
        <h1>Carregar arquivos KML</h1>
        <form method=post enctype=multipart/form-data>
          <input required type=file name=file> </br></br>
          <label for='buffer'>Tamanho do buffer:</lable>
          <input type='text' name='buffer' value='0'> </br></br>
          <label for='table'>Nome da tabela:</lable>
          <input required type='text' name='table'> </br></br>
          <input type=submit value=Upload> </br>
        </form>
        '''