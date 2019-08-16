Estrutura básica

    GET /upload

Retorno o formulário com campo para inserir nome da tabela e tamanho do arquivo. 

    POST /upload?t=[nome tabela]&b=[tamanho do buffer]
    
Low level:
- Recebe o arquivo zipado e extraí para a pasta input
- Lê a pasta input e extrai para pasta /.temp
- Lê os KML e gera os inserts do kml