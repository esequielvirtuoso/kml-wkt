def upload_view():
    return '''
        <!doctype html>
        <html>
        <title>Carregar arquivo KML</title>
        <h1>Carregar arquivos KML</h1>
            <form method=post enctype=multipart/form-data>
              <input required type=file name=file> </br></br>
              <label for='buffer'>Tamanho do buffer:</label>
              <input type='text' name='buffer' value='0'> </br></br>
              <label for='aggregate'>Gerar um geom por arquivo?</label>
              <input type='checkbox' name='aggregate'> </br></br>
              <label for='table'>Nome da tabela:</label>
              <input required type='text' name='table'> </br></br>
              <input type=submit value=Upload> </br>
            </form>
        </html>
        '''