# -*- coding: utf-8 -*-


# Department : 保障部
# Author : 袁龚浩
# Create_date : 2018-05-22


from datetime import datetime
from FundNavSpiders import GGFundNavItem
from FundNavSpiders import GGFundNavSpider
import re


class ShangHaiTrustSpider(GGFundNavSpider):
    name = 'FundNav_ShangHaiTrust'
    sitename = '上海信托'
    channel = '信托净值'
    allowed_domains = ['www.shanghaitrust.com']

    fps = [
        {'url': 'http://www.shanghaitrust.com/products/purple/index.html'},
        {'url': 'http://www.shanghaitrust.com/products/red/index.html'},
        {'url': 'http://www.shanghaitrust.com/products/600500/gaikuo/index.html'}
    ]

    def parse_fund(self, response):
        pg = 1
        nowtime = datetime.now().strftime('%Y-%m-%d')
        if '600500' in response.url:
            fund_code = '600500'
            fund_name = response.xpath('//ul[@class = "info_list"]/li[1]//text()').extract()[1]
            self.ips.append({
                'url': 'http://www.shanghaitrust.com/chart-web/chart/fundnettable?fundcode=%s&from=2000-01-01&to=%s&pages=%d-15' % (
                fund_code, nowtime, pg),
                'ref': response.url,
                'ext': [fund_name, fund_code],
                'pg': '1'
            })
        else:
            funds = response.xpath('//div[@class ="information_news_list"]//@href').extract()
            fund_names = response.xpath('//div[@class ="information_news_list"]//@title').extract()
            for fund_name, fund in zip(fund_names, funds):
                fund_code = fund.split('/')[3]
                self.ips.append({
                    'url': 'http://www.shanghaitrust.com/chart-web/chart/fundnettable?pages=1-15&fundcode=%s&from=2000-01-01&to=%s' % (
                        fund_code, nowtime),
                    'ref': response.url,
                    'ext': [fund_name, fund_code],
                    'pg': '1'
                })

    def parse_item(self, response):
        fund_name = response.meta['ext'][0]
        fund_code = response.meta['ext'][1]
        pg = response.meta['pg']
        f_list = response.xpath('//table[@id="dataTable"]//tr')
        for i in f_list[1:]:
            t = i.xpath('td//text()').extract()
            item = GGFundNavItem()
            statistic_date = t[0]
            if '600500' in response.url:
                income_value_per_ten_thousand = t[1]
                d7_annualized_return = t[2]
                d30_annualized_return = ''.join(t[3].split())
                item['income_value_per_ten_thousand'] = float(
                    income_value_per_ten_thousand) if income_value_per_ten_thousand is not None else None
                item['d7_annualized_return'] = float(d7_annualized_return) if d7_annualized_return is not None else None
                item['d30_annualized_return'] = float(
                    d30_annualized_return) if d30_annualized_return is not None else None
            else:
                nav = ''.join(t[1].split())
                added_nav = ''.join(t[2].split())
                item['nav'] = float(nav) if nav is not None else None
                item['added_nav'] = float(added_nav) if added_nav is not None else None
            item['sitename'] = self.sitename
            item['channel'] = self.channel
            item['url'] = response.url
            item['fund_name'] = fund_name
            item['statistic_date'] = datetime.strptime(statistic_date,
                                                       '%Y-%m-%d')
            yield item

        max_pg = re.findall('\d+', response.xpath('//td//a[contains(@href,"topage")]//@href').extract_first())[0]
        nowtime = datetime.now().strftime('%Y-%m-%d')
        if int(pg) < int(max_pg):
            next_pg = int(pg) + 1
            self.ips.append({
                'url': 'http://www.shanghaitrust.com/chart-web/chart/fundnettable?fundcode=%s&from=2000-01-01&to=%s&pages=%d-15' % (
                fund_code, nowtime, next_pg),
                'ref': response.url,
                'ext': [fund_name, fund_code],
                'pg': next_pg
            })
