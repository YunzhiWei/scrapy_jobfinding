# -*- coding: utf-8 -*-
import scrapy
import re
import datetime
from scrapy_jobfinding.items import JobInfoItem


_GLB_SPIDER_NAME     = "neitui"
_GLB_ALLOWED_DOMAIN  = ["neitui.me"]
_GLB_START_POINT_URL = "http://www.neitui.me/index.php?name=neitui&handle=lists&fr=search&keyword="
_GLB_SEARCH_KEYWORDS = ["Python", "hadoop", "大数据", "技术总监"]
_GLB_START_URL_LIST  = [_GLB_START_POINT_URL + _keyword for _keyword in _GLB_SEARCH_KEYWORDS]


class NeituiSpider(scrapy.Spider):

    name = _GLB_SPIDER_NAME
    allowed_domains = _GLB_ALLOWED_DOMAIN

    start_urls = _GLB_START_URL_LIST

    todayflag  = datetime.datetime.now().strftime('%m-%d')

    def parse(self, response):
        """
        Function:   This function is to parse the search result list

        IN:         response - crawl response
        Out:        NA

        Special:    
        """

        # iterate each search result to see if there is any new for today
        # if yes, try to get the link and invoke parse_result_detail for details
        for result in response.xpath('//div[@id="joblist"]/div[@class="content commentjobs brjobs topjobs"]/ul/li'):
            # print result
            resulthref = result.xpath('div[@class="cont"]/div[@class="jobnote clearfix"]/div[@class="jobnote-l"]/a/@href').extract()
            resultdate = result.xpath('div[@class="cont"]/div[@class="jobmore display"]/span[@class="createtime"]/text()').extract()
            if (len(resulthref) > 0) and (len(resultdate) > 0):
                detailurl  = "http://www." + _GLB_ALLOWED_DOMAIN[0] + resulthref[0].encode('utf-8')
                if resultdate[0].find(self.todayflag) == -1:
                    print resultdate[0], self.todayflag
                    # continue # the record is old, go on for next one
                    break

                # print detailurl
                yield scrapy.Request(detailurl, callback = self.parse_result_detail)

        # try to find if there is the next page link in the current search result
        # if yes, try to get the link and invoke this parse to process
        pagelinks = response.xpath('//div[@class="t_pagelink"]/p[@class="page"]/a[@class="next"]/@href').extract()
        if len(pagelinks) > 0:
                nextpageurl = "http://www." + _GLB_ALLOWED_DOMAIN[0] + '/' + pagelinks[0].encode('utf-8')
                print "Next @ ", nextpageurl
                yield scrapy.Request(nextpageurl, callback = self.parse)

    def parse_result_detail(self, response):
        """
        Function:   This function is to parse the detail page for more information for the job position

        IN:         response - crawl response
        Out:        NA

        Special:    
        """
        
        keystringdict = {
            'job_title':                '//div[@id="neituiDetail"]/div[@class="maincontent"]/div[@id="detail"]/div/ul[@class="clearfix"]/li/div[@class="cont"]/div[@class="jobnote"]/strong[@class="padding-r10"]/text()',
            'job_salary':               '//div[@id="neituiDetail"]/div[@class="maincontent"]/div[@id="detail"]/div/ul[@class="clearfix"]/li/div[@class="cont"]/div[@class="jobnote"]/span[@class="padding-r10 pay"]/text()',
            'requirement_anniversary':  '//div[@id="neituiDetail"]/div[@class="maincontent"]/div[@id="detail"]/div/ul[@class="clearfix"]/li/div[@class="cont"]/div[@class="jobnote"]/span[@class="padding-r10 experience"]/text()',
            'job_location':             '//div[@id="neituiDetail"]/div[@class="maincontent"]/div[@id="detail"]/div/ul[@class="clearfix"]/li/div[@class="cont"]/div[@class="jobtitle"]/span[@class="jobtitle-r"]/text()',
            'company_name':             '//div[@id="neituiDetail"]/div[@class="maincontent"]/div[@id="detail"]/div/ul[@class="clearfix"]/li/div[@class="cont"]/div[@class="jobtitle"]/span[@class="jobtitle-l"]/text()',
            'job_description':          '//div[@id="neituiDetail"]/div[@class="maincontent"]/div[@id="detail"]/div/ul[@class="clearfix"]/li/div[@class="cont"]/div[@class="jobdetail nooverflow"]/text()'            
        }
        keyslookupdict = {
            u'主页':     'company_portal', 
            u'地点':     'company_address', 
            u'公司规模': 'company_scale', 
            u'业务领域': 'company_industry', 
            u'融资信息': 'company_property', 
            u'公司愿景': 'company_description'
        }
        itemkeystringlist = [
            'target_web_name'         ,
            'file_name'               ,
            'source_url'              ,
            'job_datetime'            ,
            'job_title'               ,
            'job_location'            ,
            'job_description'         ,
            'job_salary'              ,
            'requirement_edu'         ,
            'requirement_gender'      ,
            'requirement_language'    ,
            'requirement_major'       ,
            'requirement_anniversary' ,
            'company_name'            ,
            'company_description'     ,
            'company_address'         ,
            'company_industry'        ,
            'company_scale'           ,
            'company_property'        ,
            'company_portal'
        ]

        item = JobInfoItem()

        for itemfield in itemkeystringlist:
            item[itemfield]     = None
        
        item['target_web_name'] = 'neitui'
        item['source_url']      = response.url
        item['file_name']       = response.url.split("/")[-1]
        item['job_datetime']    = datetime.datetime.now().strftime('%Y%m%d')
        
        for itemfield in keystringdict.keys():
            item[itemfield]     = self.helper_abstract_key_info(response, keystringdict[itemfield])
        
        pattern = re.compile(ur'(?<=<dt>).*?(?=</dt>)|(?<=<dd>).*?(?=</dd>)')
        for strcontent in self.helper_abstract_key_info(response, '//div[@id="neituiDetail"]/div[@class="sider"]/div[@class="plate company_information"]/dl[@class="ci_body"]', -1):            
            details = re.findall(pattern, strcontent)
            itemnum = (len(details) / 2) * 2
            idx = 0
            while idx < itemnum:
                # print details[idx], details[idx + 1]
                keystr = details[idx][:]
                keystr = keystr.replace(u'：', '')
                keystr = keystr.replace(u':', '')
                keystr = keystr.replace(u' ', '')
                if keyslookupdict.has_key(keystr):
                    item[keyslookupdict[keystr]] = details[idx + 1].encode('utf-8')
                idx += 2
        
        yield item

    def helper_abstract_key_info(self, response, keystr, idx = 0):
        """
        Function:   This helper function for the routain job of xpath process

        IN:         response - crawl response
                    keystr - string to locate the key information in the xpath
        Out:        NA

        Special:    
        """

        strlist = response.xpath(keystr).extract()
        if idx < 0:
            return strlist
        elif len(strlist) > idx:
            return strlist[idx].encode('utf-8')
        else:
            return None

