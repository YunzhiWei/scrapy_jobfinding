# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

# import scrapy
from scrapy.item import Item, Field

# class ScrapyJobfindingItem(scrapy.Item):
class JobInfoItem(Item):

    #网站标识
    target_web_name         = Field()
    #生成的文件名
    file_name               = Field()
    #职位来源网址
    source_url              = Field()
    
    #职位发布时间
    job_datetime            = Field()
    #职位名称
    job_title               = Field()
    #工作地点
    job_location            = Field()
    #职位描述
    job_description         = Field()
    #薪水范围
    job_salary              = Field()

    #学历要求
    requirement_edu         = Field()
    #性别要求
    requirement_gender      = Field()
    #语言要求
    requirement_language    = Field()
    #专业要求
    requirement_major       = Field()
    #工作年限
    requirement_anniversary = Field()

    #公司名称
    company_name            = Field()
    #企业介绍
    company_description     = Field()
    #公司地址
    company_address         = Field()
    #行业
    company_industry        = Field()
    #规模
    company_scale           = Field()
    #性质
    company_property        = Field()
    #网址
    company_portal          = Field()


