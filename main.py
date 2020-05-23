import scrapy
from scrapy.crawler import CrawlerProcess
import argparse
from urllib import parse
from EmailController import EmailController

class AdController:
    def __init__(self, searchString):
        self.searchString = searchString
        self.adQuantity = 0

    def printParsed(self, parsed):
        self.adQuantity = len(parsed)
        self.adList = parsed
        print("Quantidade de anúncios: {}\n".format(self.adQuantity))
        for ad in parsed:
            print(ad)

class OlxScrape(scrapy.Spider):
    name = "olx"
    test = None

    def __init__(self, testObject=None, *args, **kwargs):
        super(OlxScrape, self).__init__(*args, **kwargs)
        self.test = testObject
        self.start_urls = ["https://m.olx.com.br/busca?ca=31_s&q={}&w=1".format(self.test.searchString)]


    def start_requests(self):
        headers= {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}
        for url in self.start_urls:
            yield scrapy.Request(url, headers=headers)

    def parse(self, response):
        parsed = []
        for ad in response.css("div.sc-jTzLTM.sc-ksYbfQ.kIxLfV"):
            parsed.append({'title': ad.css("h2.sc-ifAKCX.sc-192atix-0.kEeSeF ::text").get(), 'price': ad.css("p.sc-ifAKCX.sc-192atix-3.kebNDl ::text").get()})

        self.test.printParsed(parsed)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Esse software é responsável por vigiar anúncios da OLX, dado uma palavra-chave para pesquisa")
    parser.add_argument("-q", action= "store", dest = "query", help="Especifica a termo de busca", required=True)
    parser.add_argument("-e", action= "store", dest = "email", help="Endereço de email do usuário", required=True)
    parser.add_argument("-p", action= "store", dest = "password", help="Senha do email do usuário", required=True)

    # App configuration
    controller = AdController(parse.quote(parser.parse_args().query))
    emailController = EmailController()
    process = CrawlerProcess(settings={"LOG_ENABLED": False})

    # Crawling itself
    process.crawl(OlxScrape, testObject=controller)
    process.start()

    # Composing message
    messageText = "Quantidade de anúncios: {}\n".format(controller.adQuantity)
    for ad in controller.adList:
        messageText = "{}\nAnúncio: {}\nPreço: {}\n".format(messageText, ad['title'], ad['price'])

    emailController.write(parser.parse_args().email, parser.parse_args().password, "Relatório OLX Crawler - Termo de pesquisa: {}".format(parser.parse_args().query), messageText)
    emailController.send()
