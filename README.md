# OLX Crawler

Um Crawler do site de anúncios OLX, que irá vigiar anúncios sobre qualquer termo de pesquisa que o usuário desejar e notificar quando houver uma mudança na quantidade de anúncios.

## Instruções de uso
1. Clone esse repositório no seu diretório de preferência
```
git clone https://github.com/yuricbraga/olx-crawler.git
```

2. Instale as dependências do pip
```
cd olx-crawler && pip install -r dependencies.txt
```

3. Execute o seguinte para mais informações de uso
```
python main.py -h
```

## TODO
- [x] Enviar link do anúncio pela mensagem
- [ ] Notificar sobre alterações de preço também