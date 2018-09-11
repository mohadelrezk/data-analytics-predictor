# mongo
from util.mongo import Mongo
from util.config import mongo_db, mongo_collection_name as mongo_collection
from util.config_cred import mongo_host, mongo_port
from collections import defaultdict


class queries:
    queries = 'customized mongo queries to fit app needs@'

    mongo = Mongo()
    collection = mongo.connect(mongo_host, mongo_port, mongo_db, mongo_collection)

    def _init__(self):
        print self.queries

    def get_dataset_meta_from_mongo(self, limit):
        query = {}
        query["datasetSize"] = {
            u"$lte": 100000
        }

        query["scriptCount"] = {
            u"$gt": 0
        }

        projection = {}
        projection["datasetId"] = 1.0
        projection["dateUpdated"] = 1.0
        projection["datasetUrl"] = 1.0
        projection["datasetSize"] = 1.0
        projection["scriptCount"] = 1.0
        projection["commonFileTypes"] = 1.0
        projection["type"] = 1.0
        projection["isDatasetHarvested"] = 1.0
        projection["isKernelsHarvested"] = 1.0

        # check update date as old datasets become unavailable after some time
        sort = [(u"dateUpdated", -1)]

        cursor = self.collection.find(query, projection=projection, sort=sort, limit=limit, no_cursor_timeout=True)
        # try:
        # for doc in cursor:
        # print(doc)
        # except BaseException as exp:
        # print exp.message

        return cursor

    def get_open_licence_dataset_meta_from_mongo(self, mongo_collection_name,limit):
        mongo = Mongo()
        collection = mongo.connect(mongo_host, mongo_port, mongo_db, mongo_collection)

        # Created with Studio 3T, the IDE for MongoDB - https://studio3t.com/

        query = {}
        query["$or"] = [
            {
                u"dataset_full_metadata.licenseShortName": u"CC0"
            },
            {
                u"dataset_full_metadata.licenseShortName": u"GPL"
            },
            {
                u"dataset_full_metadata.licenseShortName": u"CC4"
            },
            {
                u"dataset_full_metadata.licenseShortName": u"ODbL"
            },
            {
                u"dataset_full_metadata.licenseShortName": u"CC3"
            }
        ]

        projection = {}
        projection["pageNumber"] = 1.0
        projection["datasetSize"] = 1.0
        projection["overview"] = 1.0
        projection["scriptCount"] = 1.0
        projection["scriptsUrl"] = 1.0
        projection["ownerName"] = 1.0
        projection["datasetUrl"] = 1.0
        projection["dateUpdated"] = 1.0
        projection["commonFileTypes"] = 1.0
        projection["type"] = 1.0
        projection["datasetId"] = 1.0
        projection["isDatasetHarvested"] = 1.0
        projection["isKernelsHarvested"] = 1.0
        projection["dataset_full_metadata"] = 1.0
        #projection["dataset_full_metadata.licenseShortName"] = 1.0
        #projection["dataset_full_metadata.licenseName"] = 1.0

        sort = [(u"dateUpdated", -1)]

        cursor = collection.find(query, projection=projection, sort=sort, limit=limit, no_cursor_timeout=True)
        # try:
        # for doc in cursor:
        # print(doc)
        # except BaseException as exp:
        # print exp.message

        return cursor

    def update_one(self, datasetId, isDataset, isKernel):
        filter = {}
        filter['_id'] = datasetId

        update = {}

        if isDataset == True:
            update['$set'] = \
                {
                    u"isDatasetHarvested": True
                }
        if isKernel == True:
            update['$set'] = \
                {
                    u"isKernelsHarvested": True
                }

        cursor = self.collection.update_one(filter=filter, update=update, upsert=False)

        return cursor
