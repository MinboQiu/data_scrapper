import scrapy
import logging
import time
from scrapy.selector import HtmlXPathSelector
from urllib.parse import urljoin
from landchina_com.landchina_com.items import LandChinaItem, Payment


class LandSpider(scrapy.Spider):
    name = "landchina_com"
    root_url = "http://www.landchina.com/default.aspx?tabid=263"
    encoding = "gbk"
    start_date = "2018-06-26"
    end_date = "2018-06-26"
    postData = {'TAB_QueryConditionItem': '9f2c3acd-0256-4da2-a659-6949c4671a2a',
                'TAB_QuerySubmitConditionData': '9f2c3acd-0256-4da2-a659-6949c4671a2a:{}~{}'.format(
                    start_date, end_date),
                'TAB_QuerySortItemList': '282:False',
                'TAB_QuerySubmitPagerData': 1,
                'hidComName': 'default',
                '__VIEWSTATE': "",
                '__EVENTVALIDATION': ""}

    def start_requests(self):
        self.log("begin login for {} - {}".format(self.start_date, self.end_date), logging.INFO)
        return [scrapy.Request(url=self.root_url, callback=self.parse_login, encoding=self.encoding)]

    def parse_login(self, response):
        self.log("process login ...", logging.INFO)
        resp = HtmlXPathSelector(response)
        self.retrieve_state(resp)

        time.sleep(10)
        self.log("begin page 1 for {} - {}".format(self.start_date, self.end_date), logging.INFO)
        scrapy.FormRequest(url=self.root_url, callback=self.parse_page, formdata=self.postData, meta=self.postData)

    def parse_list(self, response):
        self.log("process list page {}".format(response.url), logging.INFO)
        resp = HtmlXPathSelector(response)
        table = resp.xpath('//table[@id="TAB_contentTable"]')[0]

        # push detail page links to scrapy
        detail_links = table.xpath('//a[contains(., "tabid=386")/@href').extract()
        for link in detail_links:
            scrapy.Request(url=urljoin(self.root_url, link), callback=self.parse_detail)

        # push page links to scrapy
        if response.meta["TAB_QuerySubmitPagerData"] == 1:
            self.retrieve_state(resp)
            totalPage = table.xpath("//a[contains(., '尾页')]").re_first(r"QueryAction.GoPage\('TAB',(\d*)")
            for pageNo in range(2, int(totalPage)):
                self.log("begin page {} for {} - {}".format(pageNo, self.start_date, self.end_date), logging.INFO)
                scrapy.FormRequest(url=self.root_url, callback=self.parse_page, formdata=self.postData, meta=self.postData)

    def parse_detail(self, response):
        self.log("process detail page {}".format(response.url), logging.INFO)
        resp = HtmlXPathSelector(response)
        childTrs = resp.xpath('//table[@id="theme"]/tbody/tr')
        data = LandChinaItem()
        data["url"] = response.url
        data["district"] = childTrs[2].xpath('td')[1].extract()
        data["regulationNo"] = childTrs[2].xpath('td')[3].extract()
        data["name"] = childTrs[3].xpath('td')[1].extract()
        data["location"] = childTrs[4].xpath('td')[1].extract()
        data["area"] = childTrs[5].xpath('td')[1].extract()
        are2 = childTrs[5].xpath('td')[3].extract()
        try:
            if are2 == "" or not are2:
                data["landSource"] = "新增建设用地(来自存量库)"
            elif float(data["area"]) == float(are2):
                data["landSource"] = "现有建设用地"
            elif float(are2) == 0:
                data["landSource"] = "新增建设用地"
            else:
                data["landSource"] = "新增建设用地(来自存量库)"
        except:
            data["landSource"] = "新增建设用地(来自存量库)"
        data["usage"] = childTrs[6].xpath('td')[1].extract()
        data["wayOfSupply"] = childTrs[6].xpath('td')[3].extract()
        data["tenureOfUse"] = childTrs[7].xpath('td')[1].extract()
        data["industry"] = childTrs[7].xpath('td')[3].extract()
        data["landLevel"] = childTrs[8].xpath('td')[1].extract()
        data["price"] = childTrs[8].xpath('td')[3].extract()
        data["owner"] = childTrs[10].xpath('td')[1].extract()
        plotRatio = childTrs[12].xpath('tbody tr')[1].xpath('td')
        data["plotRatioUpperLimit"] = plotRatio[1].extract()
        data["plotRatioDownLimit"] = plotRatio[3].extract()
        data["dateOfDeliveryAgreed"] = childTrs[12].xpath('td')[3].extract()
        data["dateOfConstructionAgreed"] = childTrs[13].xpath('td')[1].extract()
        data["dateOfCompletionAgreed"] = childTrs[13].xpath('td')[3].extract()
        data["dateOfConstructionActual"] = childTrs[14].xpath('td')[1].extract()
        data["dateOfCompletionActual"] = childTrs[14].xpath('td')[3].extract()
        data["approvedBy"] = childTrs[15].xpath('td')[1].extract()
        if "人民政府" not in data["approvedBy"]:
            data["approvedBy"] += "人民政府"
        data["dateOfSigning"] = childTrs[15].xpath('td')[3].extract()
        paymentsTrs = childTrs[9].xpath('table tbody')[0].xpath('tr[position()>3]')
        for paymentsTr in paymentsTrs:
            payment = Payment()
            payment.date = paymentsTr.xpath('td')[1].extract()
            payment.amount = paymentsTr.xpath('td')[2].extract()
            payment.comment = paymentsTr.xpath('td')[3].extract()
            data["payments"].append(payment)
        return data

    def parse(self, response):
        self.log("process parse func {}".format(response.url), logging.INFO)
        pass

    def retrieve_state(self, resp):
        vs = resp.xpath('//input[@id="__VIEWSTATE"]/@value').extract_first()
        ev = resp.xpath('//input[@id="__EVENTVALIDATION"]/@value').extract_first()
        self.postData['__VIEWSTATE'] = vs
        self.postData['__EVENTVALIDATION'] = ev
