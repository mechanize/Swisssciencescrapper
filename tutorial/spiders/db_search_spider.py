import scrapy
import re


class QuotesSpider(scrapy.Spider):
    name = "db_search"
    result_companies = 'http://www.swisslifesciences.com/swiss/portal/result_companies.php'

    def start_requests(self):
        urls = [
            'http://www.swisslifesciences.com/swiss/portal/search_companies.php',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_form)

    def parse_form(self):
        data = {
            'search':                   '2',
            'ret':                      'companies',
            'search_freetext_all':      '',
            'search_cname':             '',
            'search_region_single':     '-1',
            'search_country_single':    '-1',
            'search_state[]':           ['3', '2', '5'],
            'search_sector_single':     '0',
            'search_empl_domicil_from': '',
            'search_empl_domicil_to':   '',
            'search_empl_worldwide_from': '',
            'search_empl_worldwide_to': '',
            'search_ipo_from':          '',
            'search_ipo_to':            '',
            'search_foundation_from':   '',
            'search_foundation_to':     '',
            'search_latest_round':      '0',
            'search_relationship':      '0',
            's': 'search'
        }
        yield scrapy.FormRequest(url=self.result_companies, formdata=data, callback=self.parse_companies)

    def parse_companies(self, response):
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)

        company_links = set()
        # cookie = response.headers.getlist('Set-Cookie')[0].split(b';')[0]
        for company in response.xpath("//div[starts-with(@class,'openPopUp')]"):
            searchstr = company.xpath(".//div[starts-with(@class, 'main_profile')]").get()
            company_link = re.search(r'app/portal/detail_layer\.php\?c=.*'
                                     r'main individual company profile', searchstr).group().split('\'')[0]
            company_links.add(company_link)
            self.log('Found link: %s' % company_link)

        base_url = 'http://www.swisslifesciences.com/'
        for company_link in company_links:
            data = {'__utmz': '103162498.1557616900.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
                    'ck_headerwarning': 'warning_accepted',
                    'PHPSESSID': 'mqrvb22pqch2m5k0d8i7ab1ucs',
                    '__utma': '103162498.1629763947.1557616900.1558992342.1559047312.13',
                    ' __utmc': '103162498',
                    '__utmt': '1',
                    'sc_is_visitor_unique': 'rx442531.1559047362.597C627FAB354FBE1DCA2791B90EC3E4.13.10.8.6.5.5.3.3.2',
                    ' __utmb': '103162498.7.9.1559047362538'
                    }
            yield scrapy.Request(url=base_url + company_link, cookies=data, callback=self.parse_data)

    def parse_data(self, response):
        filename = response.url.split('/')[-1] + '.html'
        with open(filename, 'w') as f:
            f.write(response.body)
        self.log('File created: %s' % filename)
