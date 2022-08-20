import scrapy


class NewsExtractor(scrapy.Spider):
    name = 'chair_scraper.com'
    allowed_domains = [
        'www.amazon.com',
    ]
    start_urls = [
        'https://www.amazon.com/s?k=desk+chair&__mk_es_US=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=3DXQFLPRSD1CL&sprefix=desk+chai%2Caps%2C208&ref=nb_sb_noss_2',
    ]

    
    def parse(self, response):
        for product in response.css("div.a-section.a-spacing-base"):
            name = product.css("span.a-size-base-plus.a-text-normal::text").get()
            price = product.css("span.a-offscreen::text").get()
            rate = product.css("span.a-icon-alt::text").get()

            yield {'name': name, 'price': price, 'rate': rate.split(' ')[0] if rate else rate}

        next_page = response.css("a.s-pagination-next").attrib['href']

        if next_page:
            yield response.follow(next_page, self.parse)
            