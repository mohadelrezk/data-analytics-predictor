# kaggle GET url request
import json
import urllib2
import urllib
from util.config import dataset_search_url, dataset_params
from util.config import kernel_search_url, search_kernel_params
from util.config import user_agent

# mongo
from util.mongo import Mongo
from util.config import mongo_db, mongo_collection_name as dataset_collection, \
    mongo_collection_name_for_kernels as kernels_collection, mongo_collection_name_for_opendatasets
from util.config_cred import mongo_host, mongo_port
from collections import defaultdict

# time sleep
import time

# garbage colector
import gc

# import customized queries
from customized_queries import queries

# kaggle api command line
from subprocess import call
from util.config import kaggle_cmd_list_param

# import os for directory creation
import os

# download folder
from util.config import dataset_download_dir

# for login
import requests


class kaggle(object):
    kaggle = 'kaggle harvester!'
    # mongo instance, connection and collection return
    mongo = Mongo()
    collectionObject = mongo.connect(mongo_host, mongo_port, mongo_db, dataset_collection)
    kernels_collectionObject = mongo.connect(mongo_host, mongo_port, mongo_db, kernels_collection)

    def _init__(self):
        print self.kaggle

    def get_datasets_info(self, page, pageSize):
        print 'get_datasets_info'
        # configure parameters
        dataset_params['page'] = page
        dataset_params['pageSize'] = pageSize
        print dataset_params
        # get json
        dataset_response = urllib2.urlopen(self.construct_kaggle_request(dataset_search_url, dataset_params))
        datasets_list = json.loads(dataset_response.read())
        print datasets_list
        print json.dumps(datasets_list)
        return datasets_list

    def construct_kaggle_request(self, search_url, parameters):
        kaggle_search_params = urllib.urlencode(parameters)
        kaggle_search_url = search_url + '?' + kaggle_search_params
        # header variable
        headers = {'User-Agent': user_agent}
        # creating request
        kaggle_request = urllib2.Request(kaggle_search_url, None, headers)
        return kaggle_request

    def save_dataset_in_mongo(self, collectionObject, pageNumber, json_object, id_field):
        dataset_object = defaultdict(list)
        dataset_object['page'] = pageNumber  # page number of response from kaggle
        dataset_object['dataset_full_metadata'] = json_object  # json response from kaggle
        dataset_object['overview'] = json_object['overview']
        dataset_object['ownerName'] = json_object['ownerName']
        dataset_object['commonFileTypes'] = []
        for file_type in json_object['commonFileTypes']:
            dataset_object['commonFileTypes'].append(file_type)
        dataset_object['scriptsUrl'] = json_object['scriptsUrl']
        dataset_object['datasetId'] = json_object['datasetId']
        dataset_object['dateUpdated'] = json_object['dateUpdated']
        dataset_object['datasetUrl'] = json_object['datasetUrl']
        dataset_object['scriptCount'] = json_object['scriptCount']
        dataset_object['type'] = json_object['type']
        dataset_object['datasetSize'] = json_object['datasetSize']
        # not included in previous meta data harvest, but in full meta data
        dataset_object['isDatasetHarvested'] = False
        dataset_object['isKernelHarvested'] = False
        dataset_object['currentDatasetVersionNumber'] = json_object[
            'currentDatasetVersionNumber']
        dataset_object['licenseShortName'] = json_object[
            'licenseShortName']
        dataset_object['licenseName'] = json_object[
            'licenseName']

        try:
            # print json.dumps(dataset_object)
            self.mongo.appendDataListToMongo(collectionObject, dataset_object, id_field)

        except BaseException as e:
            print e.message, e.args

    def save_kernel_in_mongo(self, collectionObject, json_object, id_field):
        kernel_object = defaultdict(list)
        kernel_object['kernel_full_metadata'] = json_object  # json response from kaggle
        kernel_object['id'] = json_object['id']
        kernel_object['author'] = json_object['author']
        kernel_object['datasetIds'] = []  # could be multible datasets
        for datasource in json_object['dataSources']:
            kernel_object['datasetIds'].append(datasource)
        kernel_object['scriptUrl'] = json_object['scriptUrl']
        kernel_object['scriptVersionDateCreated'] = json_object['scriptVersionDateCreated']
        kernel_object['lastRunTime'] = json_object['lastRunTime']
        kernel_object['versionNumber'] = json_object['versionNumber']
        kernel_object['languageName'] = json_object['languageName']
        kernel_object['isPrivate'] = json_object['isPrivate']
        kernel_object['scriptVersionId'] = json_object['scriptVersionId']
        kernel_object['isKernelHarvested'] = False

        try:
            # print json.dumps(dataset_object)
            self.mongo.appendDataListToMongo(collectionObject, kernel_object, id_field)

        except BaseException as e:
            print e.message, e.args

    # filter datastes metadata to only open * to be done only one time
    def save_cursor_in_mongo(self, collectionObject, cursor, id_field):
        dataset_object = defaultdict(list)
        # dataset_object['page'] = cursor ['pageNumber']  # page number of response from kaggle
        dataset_object['dataset_full_metadata'] = cursor['dataset_full_metadata']  # json response from kaggle
        print cursor['dataset_full_metadata']
        dataset_object['overview'] = cursor['overview']
        # print cursor['overview']
        dataset_object['ownerName'] = cursor['ownerName']
        dataset_object['commonFileTypes'] = []
        for file_type in cursor['commonFileTypes']:
            dataset_object['commonFileTypes'].append(file_type)
        dataset_object['scriptsUrl'] = cursor['scriptsUrl']
        dataset_object['datasetId'] = cursor['datasetId']
        dataset_object['dateUpdated'] = cursor['dateUpdated']
        dataset_object['datasetUrl'] = cursor['datasetUrl']
        dataset_object['scriptCount'] = cursor['scriptCount']
        dataset_object['type'] = cursor['type']
        dataset_object['datasetSize'] = cursor['datasetSize']
        # not included in previous meta data harvest, but in full meta data
        if 'isDatasetHarvested' in cursor.keys():
            dataset_object['isDatasetHarvested'] = cursor['isDatasetHarvested']
        else:
            dataset_object['isDatasetHarvested'] = False
        if 'isKernelHarvested' in cursor.keys():
            dataset_object['isKernelHarvested'] = cursor['isKernelHarvested']
        else:
            dataset_object['isKernelHarvested'] = False
        try:
            dataset_object['currentDatasetVersionNumber'] = cursor["dataset_full_metadata.currentDatasetVersionNumber"]
            dataset_object['licenseShortName'] = cursor[
                'dataset_full_metadata.licenseShortName']
            dataset_object['licenseName'] = cursor[
                'dataset_full_metadata.licenseName']
        except KeyError:
            pass



        try:
            # print json.dumps(dataset_object)
            self.mongo.appendDataListToMongo(collectionObject, dataset_object, id_field)

        except BaseException as e:
            print e.message, e.args

    def harvest_datsets_metadata(self, startingPage, endingPage):

        # check garbage collector
        if gc.isenabled() == False:
            gc.enable()
        # initiate kaggle class instance
        # kag = kaggle()

        for page in range(startingPage, endingPage):  # limit is execluded

            kaggle_response = self.get_datasets_info(str(page), '20')
            datasetListItems = kaggle_response['datasetListItems']
            for datasetItem in datasetListItems:
                print datasetItem['datasetId']
                # print json.dumps(datasetItem)
                self.save_dataset_in_mongo(collectionObject=self.collectionObject, pageNumber=page,
                                           json_object=datasetItem,
                                           id_field='datasetId')

            # Wait for 5 seconds
            time.sleep(15)

    # filter datastes metadata to only open * to be done only one time
    def get_open_licence_datasets(self, originCollection, destinationCollection):
        # run open dataset filter
        quer = queries()
        open_licence_datasets_cursor = quer.get_open_licence_dataset_meta_from_mongo(mongo_collection_name=originCollection,
                                                                                     limit=6500)

        destinationCollection_obj = self.mongo.connect(mongo_host, mongo_port, mongo_db, destinationCollection)

        for open_dataset in open_licence_datasets_cursor:
            #print open_dataset
            self.save_cursor_in_mongo(collectionObject=destinationCollection_obj, cursor=open_dataset,
                                     id_field='datasetId')

    # dataset download
    def harvest_datasets(self, limit):
        quer = queries()
        datasets_cursor = quer.get_dataset_meta_from_mongo(limit=limit)
        # print datasets_cursor
        for item in datasets_cursor:
            # for type in item['commonFileTypes']:
            #   print  type['fileType']C
            # if type['fileType'] == 'csv':
            # check if harvested before
            if item['isDatasetHarvested'] == False:
                if item['scriptCount'] > 0:
                    # create directory with dataset id
                    dir = self.create_download_path(downloadFolder=dataset_download_dir, datasetId=item['datasetId'])
                    # pass it to kaggle cmd api with dataset url
                    self.run_kaggle_api_shell_commands(datasetUrl=item['datasetUrl'], path=dir)
                    # change dataset flag to harvested
                    self.change_isHarvested_attr(datasetId=item['datasetId'], isDataset=True, isKernel=False)

    def run_kaggle_api_shell_commands(self, datasetUrl, path):
        datasetUrl_after_backslash_removed = str(datasetUrl)[1:]
        print datasetUrl_after_backslash_removed
        kaggle_cmd_list_param[4] = datasetUrl_after_backslash_removed
        kaggle_cmd_list_param[6] = str(path)
        print kaggle_cmd_list_param
        # run shell command to download dataset
        call(kaggle_cmd_list_param)
        time.sleep(30)

    def create_download_path(self, downloadFolder, datasetId):
        directory = os.path.dirname(downloadFolder + '/' + str(datasetId) + '/')
        if not os.path.exists(directory):
            os.makedirs(directory)

        return directory

    def login(self):
        username = ''
        password = ''
        competition_id = '3136'  # the code for titanic

        session = requests.Session()
        get_me = 'https://www.kaggle.com/account/login?ReturnUrl=%2fc%2f' + competition_id + '%2fpublicleaderboarddata.zip'
        response = session.get(get_me)  # call it once to get the request verification cookie
        payload = {'username': username, ' password': password,
                   '__RequestVerificationToken': session.cookies.get('__RequestVerificationToken')}
        r = session.post(get_me, data=payload)
        with open('the-zip.zip', 'wb') as f:
            f.write(r.content)

    def cookies_login(self):
        # https://github.com/Kaggle/kaggle-api/issues/8
        """
        wget - -load - cookies.. / Downloads / cookies.txt
        https: // www.kaggle.com / c / 8310 / download / MasseyOrdinals.zip
        """

    def change_isHarvested_attr(self, datasetId, isDataset=False, isKernel=False):
        quer = queries()
        datasets_cursor = quer.update_one(datasetId=datasetId, isDataset=isDataset, isKernel=isKernel)

    def get_kernels_info(self, lastKernelId):

        print 'get kernels'
        # configure parameters
        search_kernel_params['datasetId'] = ''
        search_kernel_params['after'] = lastKernelId
        print search_kernel_params
        # get json
        kernel_response = urllib2.urlopen(self.construct_kaggle_request(kernel_search_url, search_kernel_params))
        kernel_list = json.loads(kernel_response.read())
        print kernel_list
        print json.dumps(kernel_list)
        return kernel_list

    # @TODO stoped here!
    def harvest_kernel_metadata(self, maxKernelsPerRun=500):
        # claculate number of kaggle server requests
        maxResponseBatches = maxKernelsPerRun // 20  # 20 is list size per response

        # check garbage collector
        if gc.isenabled() == False:
            gc.enable()

        # holding last kernel Id
        lastKernelId = ''

        for batch in range(0, maxResponseBatches):  # limit is excluded
            kaggle_response = self.get_kernels_info(lastKernelId=lastKernelId)
            kernelList = kaggle_response
            for kernel in kernelList:
                print kernel['id']
                # print json.dumps(datasetItem)
                self.save_kernel_in_mongo(collectionObject=self.kernels_collectionObject,
                                          json_object=kernel,
                                          id_field='id')
            lastKernelId = kernelList[len(kernelList) - 1]['id']

            # Wait for 5 seconds
            time.sleep(15)

    def download_kernel(self, kernelId):
        print 'download_dataset'


"""
        experiments
        """
if __name__ == '__main__':
    kag = kaggle()
    # kag.harvest_datsets_metadata(startingPage=420, endingPage=500)
    kag.harvest_kernel_metadata(500)
