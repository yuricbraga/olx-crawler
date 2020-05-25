import os
import scrapy
from scrapy.crawler import CrawlerProcess, CrawlerRunner
import argparse
from urllib import parse
from EmailController import EmailController
from time import sleep
from multiprocessing import Process, Queue
from twisted.internet import reactor

CAN_SEND_EMAIL = False

class AdController:
    def __init__(self, queryString, ddd):
        self.queryString = queryString
        self.ddd = ddd
        self.adList = []
        self.adQuantity = 0
        self.canSendEmail = False

    def append(self, item):
        self.adQuantity += 1
        self.adList.append(item)

    def printParsed(self):
        print("Quantidade de anúncios: {}\n".format(self.adQuantity))
        for ad in self.adList:
            print(ad)

class OlxScrape(scrapy.Spider):
    name = "olx"

    def __init__(self, adController=None, *args, **kwargs):
        super(OlxScrape, self).__init__(*args, **kwargs)
        self.adController = adController
        self.start_urls = ["https://m.olx.com.br/busca?ca={}_s&q={}&w=1".format(adController.ddd, adController.queryString)]


    def start_requests(self):
        headers= {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}
        for url in self.start_urls:
            yield scrapy.Request(url, headers=headers)

    def parse(self, response):
        if len(response.css("div.sc-jTzLTM.sc-ksYbfQ.kIxLfV")) != self.adController.adQuantity:
            self.adController.canSendEmail = True

        self.adController.adList = []
        self.adController.adQuantity = 0
        #for ad in response.css("div.sc-jTzLTM.sc-ksYbfQ.kIxLfV"):
        #    self.adController.append({'title': ad.css("h2.sc-ifAKCX.sc-192atix-0.kEeSeF ::text").get(), 'price': ad.css("p.sc-ifAKCX.sc-192atix-3.kebNDl ::text").get()})
        for ad in response.css("ul#ad-list>li.c1zfsg-1.dcdGwU>a.sc-19i6wrj-0.lnBmvt"):
            self.adController.append({"title": ad.css("div>div>h2 ::text").get(),"price": ad.css("div>div>p.sc-ifAKCX.sc-192atix-3.kebNDl ::text").get(),"link": ad.css("::attr(href)").extract()[0]})
            

        self.adController.printParsed()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Esse software é responsável por vigiar anúncios da OLX, dado uma palavra-chave para pesquisa")
    parser.add_argument("-q", action= "store", dest = "query", help="Especifica a termo de busca", required=True)
    parser.add_argument("-e", action= "store", dest = "email", help="Endereço de email do usuário", required=True)
    parser.add_argument("-p", action= "store", dest = "password", help="Senha do email do usuário", required=True)
    parser.add_argument("-r", action= "store", dest = "region", help="DDD da região a se fazer a pesquisa", required=True)

    # App configuration
    controller = AdController(parse.quote(parser.parse_args().query), parser.parse_args().region)
    process = CrawlerProcess(settings={"LOG_ENABLED": False})

    try:
        def _crawl(result, spider, adController):
            deferred = process.crawl(spider, adController=adController)

            # Composing message
            def _compose():
                if controller.canSendEmail:
                    emailController = EmailController()
                    messageText = "Quantidade de anúncios: {}\n".format(controller.adQuantity)
                    for ad in controller.adList:
                        messageText = "{}\nAnúncio: {}\nPreço: {}\nLink: {}\n".format(messageText, ad['title'], ad['price'], ad['link'])
                    emailController.write(parser.parse_args().email, parser.parse_args().password, "Relatório OLX Crawler - Termo de pesquisa: {}".format(parser.parse_args().query), messageText)
                    emailController.send()
                    controller.canSendEmail = False

            deferred.addCallback(lambda _: _compose())
            deferred.addCallback(lambda _: sleep(60*15))
            deferred.addCallback(_crawl, spider, adController)
            return deferred

        _crawl(None, OlxScrape, controller)
        process.start()

    except KeyboardInterrupt:
        print("OLX Crawling finalizado")

