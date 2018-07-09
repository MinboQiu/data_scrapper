# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import datetime
import logging
from sqlalchemy.orm import sessionmaker
from landchina.landchina_com.models.models import Record, Payment, create_engine
from scrapy.utils.project import get_project_settings

class LandchinaComPipeline(object):
    session = None

    def process_item(self, item, spider):
        rec = Record()
        rec.name = item["name"]
        rec.url = item["url"]
        rec.guid = item["guid"]
        rec.district = item["district"]
        rec.regulationNo = item["regulationNo"]
        rec.location = item["location"]
        rec.area = item["area"]
        rec.landSource = item["landSource"]
        rec.usage = item["usage"]
        rec.wayOfSupply = item["wayOfSupply"]
        rec.tenureOfUse = int(item["tenureOfUse"])
        rec.industry = item["industry"]
        rec.landLevel = item["landLevel"]
        rec.price = float(item["price"])
        rec.owner = item["owner"]
        rec.plotRatioDownLimit = float(item["plotRatioDownLimit"])
        rec.plotRatioUpperLimit = float(item["plotRatioUpperLimit"])
        rec.dateOfDeliveryAgreed = self.parse_date(item["dateOfDeliveryAgreed"])
        rec.dateOfConstructionAgreed = self.parse_date(item["dateOfConstructionAgreed"])
        rec.dateOfCompletionAgreed = self.parse_date(item["dateOfCompletionAgreed"])
        rec.dateOfConstructionActual = self.parse_date(item["dateOfConstructionActual"])
        rec.dateOfCompletionActual = self.parse_date(item["dateOfCompletionActual"])
        rec.approvedBy = item["approvedBy"]
        rec.dateOfSigning = item["dateOfSigning"]

        for payment in item["payments"]:
            pm = Payment()
            pm.guid = payment["guid"]
            pm.date = self.parse_date(payment["date"])
            pm.amount = float(payment["amount"])
            pm.comment = payment["comment"]
            rec.payments.append(pm)

        try:
            self.session.add(rec)
            self.session.commit()
            spider.log("add database {}".format(rec.url), logging.INFO)
        except:
            self.session.rollback()
            spider.log("add database {} failed".format(rec.url), logging.ERROR)
            raise
        return item

    def open_spider(self, spider):
        engine = create_engine(get_project_settings().get("CONNECTION_STRING"))
        self.session = sessionmaker(bind=engine)()

    def close_spider(self, spider):
        self.session.close()

    def parse_date(self, date):
        return datetime.datetime.strptime(date, "%Y年%m月%d日")
