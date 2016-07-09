# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


from scrapy.utils.project import get_project_settings
from pymongo import MongoClient
from scrapy import signals
import json
import codecs
import sys
import traceback
import datetime
# sys.path.append("../../../")

#   $ mongoimport --db test --collection spiderjson --drop --file deals_20160624201938.json
#   $ mongoimport --db diningcopy_development --collection deals --drop --file deals_20160624201938.json
#   $ mongoimport -h ds023674.mlab.com:23674 -d diningcopy -c <collection> -u <user> -p <password> --file <input file>

_GBL_DEALS_FILE_NAME_FORMAT = './output/jobs_%s.json'


class DumpPipeline(object):

    def helper_print_item(self, item):
        print "+++++++ Print Item +++++++"
        for key in item.keys():
            if None != item[key]:
                print key, item[key]

    def process_item(self, item, spider):
        
        self.helper_print_item(item)
        return item 						# Without return item, other pipelines will not get the item to process


class MongoDBPipeline(object):
    
    def __init__(self):
        print "++++++++++++ MongoDB Pipeline Initial!!! +++++++++++ \n"
        
        # initiate connection towards to mongodb
        settings = get_project_settings()

        connstring = settings['MONGODB_DB_INIT'] + settings['MONGODB_DB_USER'] + ":" + settings['MONGODB_DB_PSWD'] + "@" + settings['MONGODB_DB_SVR'] + ":" + settings['MONGODB_DB_PORT'] + "/" + settings['MONGODB_DB_NAME']
        print connstring
        conn = MongoClient(connstring)
        db   = conn[settings['MONGODB_DB_NAME']]
        self.mongo_conllection = db[settings['MONGODB_DB_COLL']]


    def process_item(self, item, spider):

        if not self.mongo_conllection.insert(dict(item)):
            print "++++++++++++  Error Inserting mongo +++++++++++"
        return item 						# Without return item, other pipelines will not get the item to process


class JsonFilePipeline(object):
    
    def __init__(self):
        print "++++++++++++ JsonFile Pipeline Initial!!! +++++++++++ \nSpider: "
        
        # for output file
        self.outputfiles = {}

    
    def open_spider(self, spider):
        
        print "++++++++++++ JsonFile Opened!!! +++++++++++ \nSpider: ", spider.name

        try:
            print "++++++++++++ Open output file ++++++++++++"
            print datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            filename = _GBL_DEALS_FILE_NAME_FORMAT % (datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
            print filename
            outputfile = open(filename, 'w') #, encoding='utf-8')
            # outputfile = open(_GBL_DEALS_FILE_NAME_FORMAT % (datetime.datetime.now().strftime('%Y%m%d%H%M%S')), 'w', encoding='utf-8')
            self.outputfiles[spider] = outputfile
        except Exception as e:
            print "ERROR OPEN FILE!! >>> "
            print traceback.format_exc()
        

    def close_spider(self, spider):
        print "++++++++++++++ JsonFile Closed!!! ++++++++++\nSpider: ", spider.name

        outputfile = self.outputfiles.pop(spider)
        outputfile.close()


    def process_item(self, item, spider):
        
        try:
            print "Write file"
            line = json.dumps(dict(item)) + '\n'
            self.outputfiles[spider].write(line)
            return item 						# Without return item, other pipelines will not get the item to process

        except Exception as e:
            print "ERROR WRITE FILE!! >>> "
            print traceback.format_exc()
            
        


