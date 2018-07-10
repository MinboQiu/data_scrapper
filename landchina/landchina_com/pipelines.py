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

    def open_spider(self, spider):
        engine = create_engine(get_project_settings().get("CONNECTION_STRING"))
        self.session = sessionmaker(bind=engine)()

    def close_spider(self, spider):
        self.session.close()

    def process_item(self, item, spider):
        rec = Record()
        rec.name = self.parse_string(item["name"])
        rec.url = self.parse_string(item["url"])
        rec.guid = self.parse_string(item["guid"])
        rec.district = self.parse_string(item["district"])
        rec.regulationNo = self.parse_string(item["regulationNo"])
        rec.location = self.parse_string(item["location"])
        rec.area = self.parse_string(item["area"])
        rec.landSource = self.parse_string(item["landSource"])
        rec.usage = self.parse_string(item["usage"])
        rec.wayOfSupply = self.parse_string(item["wayOfSupply"])
        rec.tenureOfUse = self.parse_int(item["tenureOfUse"])
        rec.industry = self.parse_string(item["industry"])
        rec.landLevel = self.parse_string(item["landLevel"])
        rec.price = self.parse_float(item["price"])
        rec.owner = self.parse_string(item["owner"])
        rec.plotRatioDownLimit = self.parse_float(item["plotRatioDownLimit"])
        rec.plotRatioUpperLimit = self.parse_float(item["plotRatioUpperLimit"])
        rec.dateOfDeliveryAgreed = self.parse_date(item["dateOfDeliveryAgreed"])
        rec.dateOfConstructionAgreed = self.parse_date(item["dateOfConstructionAgreed"])
        rec.dateOfCompletionAgreed = self.parse_date(item["dateOfCompletionAgreed"])
        rec.dateOfConstructionActual = self.parse_date(item["dateOfConstructionActual"])
        rec.dateOfCompletionActual = self.parse_date(item["dateOfCompletionActual"])
        rec.approvedBy = self.parse_string(item["approvedBy"])
        rec.dateOfSigning = self.parse_date(item["dateOfSigning"])

        for payment in item["payments"]:
            pm = Payment()
            pm.guid = self.parse_string(payment["guid"])
            pm.date = self.parse_date(payment["date"])
            pm.amount = self.parse_float(payment["amount"])
            pm.comment = self.parse_string(payment["comment"])
            rec.payments.append(pm)

        try:
            self.session.add(rec)
            self.session.commit()
            spider.log("add database {}".format(rec.url), logging.INFO)
        except:
            self.session.rollback()
            self.log.error("add database {} failed".format(rec.url), logging.ERROR)
            raise
        return item

    def parse_date(self, data):
        if data is None:
            return None
        strip_data = data.strip()
        if strip_data == "":
            return None
        return datetime.datetime.strptime(strip_data, "%Y年%m月%d日")

    def parse_string(self, data):
        if data is None:
            return None
        return data.strip()

    def parse_float(self, data):
        if data is None:
            return None
        strip_data = data.strip()
        if strip_data == "":
            return None
        return float(strip_data)

    def parse_int(self, data):
        if data is None:
            return None
        strip_data = data.strip()
        if strip_data == "":
            return None
        return int(strip_data)
