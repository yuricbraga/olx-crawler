import scrapy
from scrapy.crawler import CrawlerProcess
import argparse
from urllib import parse

class AdController:
    def __init__(self, searchString):
        self.searchString = searchString
        self.adQuantity = 0

    def printParsed(self, parsed):
        self.adQuantity = len(parsed)
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
            #yield {'title': ad.css("h2.sc-ifAKCX.sc-192atix-0.kEeSeF ::text").get(), 'price': ad.css("p.sc-ifAKCX.sc-192atix-3.kebNDl ::text").get()}
            #self.test.printParsed({'title': ad.css("h2.sc-ifAKCX.sc-192atix-0.kEeSeF ::text").get(), 'price': ad.css("p.sc-ifAKCX.sc-192atix-3.kebNDl ::text").get()})
            parsed.append({'title': ad.css("h2.sc-ifAKCX.sc-192atix-0.kEeSeF ::text").get(), 'price': ad.css("p.sc-ifAKCX.sc-192atix-3.kebNDl ::text").get()})

        self.test.printParsed(parsed)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Esse software é responsável por vigiar anúncios da OLX, dado uma palavra-chave para pesquisa")
    parser.add_argument("-q", action= "store", dest = "query", help="Especifica a termo de busca", required=True)

    controller = AdController(parse.quote(parser.parse_args().query))

    process = CrawlerProcess(settings={"LOG_ENABLED": False})
    process.crawl(OlxScrape, testObject=controller)
    process.start()