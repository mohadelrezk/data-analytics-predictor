p

"""connect to mongo"""

"""query dataset locations"""
"""
db.dataAnalytical_collection_from_op_2.find( { "parameter.key": "repository_entry"} )
db.dataAnalytical_collection_from_op_2.find( { "$and": [ {"operator.class": "read_csv"},{ "parameter.key": "csv_file"}]} )
"""

""" re-create full dataset path"""

"""get dataset either using curl or github api repository.get file content function"""

"""attatch dataset to the process file in mongo """

"""detect dataset features/properties (size, datas types, source)"""

import copy
import csv
import urllib2
import urlparse
from urlparse import urljoin

from util.loggiingg import logee
from util.mongo import Mongo

import os
from util.config import mongo_db as main_db, mongo_collection_name_with_repo_data, log_dir, log_file, log_name, \
    analysis_output_folder
from util.config_cred import mongo_host, mongo_port


class Retrieve_DS:

    def __init__(self):

        # initiate logger object
        global log
        log = logee(log_dir, log_file, log_name)

        # connect
        global mongo
        mongo = Mongo()

        # analysis output folder
        if not os.path.exists(analysis_output_folder):
            os.makedirs(analysis_output_folder)

    # get **** in csv
    def get_dataset_paths_into_csv(self, operator_class, parameter_key):

        # datasetcollecion = mongo.connect('localhost', 27017, 'rtpa', 'datagovie_1_PubllishersNetwork')
        # NetworkCollectionName = collection_name + '_Network_CF_'+comparsionfieldd
        datasetcollecion = mongo.connect(mongo_host, mongo_port, main_db, mongo_collection_name_with_repo_data)

        # datasetCursor = mongo.getfromMongo(datasetcollecion, "")#.sort("relationStrength", -1)
        mongo_query = {}
        mongo_query['$and'] = []

        args1 = {}
        args1["operator.class"] = operator_class
        args2 = {}
        args2["parameter.key"] = parameter_key

        mongo_query['$and'].append(args1)
        mongo_query['$and'].append(args2)

        try:
            datasetCursor = datasetcollecion.find(mongo_query)
        except:
            print
            'parameter key not provided or not supported.'

        header = ['_id', 'download_url', 'git_url', 'html_url', 'path', 'type', 'repo_language', 'repo_created_at',
                  'repo_updated_at', 'full_name', 'operator_class', 'parameter_key', 'parameter_value_link_to_ds']
        datasetRecord_r = []
        with open(analysis_output_folder + "/" + operator_class + "_AND_" + parameter_key + "_" + "datasets.csv",
                  'w+') as output:
            outputwriter = csv.writer(output, delimiter=',', quotechar='\"')
            # putting the header
            outputwriter.writerow(header)

            parameters_have_datasets = []
            parameter_entry = {}
            for relationrecord in datasetCursor:
                if '_id' in relationrecord:
                    datasetRecord_r.append(relationrecord['_id'].encode('utf-8'))
                if 'download_url' in relationrecord:
                    datasetRecord_r.append(relationrecord['download_url'].encode('utf-8'))
                if 'git_url' in relationrecord:
                    datasetRecord_r.append(relationrecord['git_url'].encode('utf-8'))
                if 'html_url' in relationrecord:
                    datasetRecord_r.append(relationrecord['html_url'].encode('utf-8'))
                if 'path' in relationrecord:
                    datasetRecord_r.append(relationrecord['path'].encode('utf-8'))
                if 'type' in relationrecord:
                    datasetRecord_r.append(relationrecord['type'].encode('utf-8'))
                if 'repository_info' in relationrecord:
                    datasetRecord_r.append(relationrecord['repository_info']['language'])
                    datasetRecord_r.append(relationrecord['repository_info']['created_at'])
                    datasetRecord_r.append(relationrecord['repository_info']['updated_at'])
                    datasetRecord_r.append(relationrecord['repository_info']['full_name'].encode('utf-8'))

                datasetRecord_r.append(operator_class)

                if 'parameter' in relationrecord:
                    # params_list =   relationrecord['parameter'
                    for param in relationrecord['parameter']:
                        # print param
                        # keey= u'key'
                        if 'key' in param:

                            if param['key'] == parameter_key:
                                parameter_entry['key'] = param['key']
                                parameter_entry['value'] = param['value']
                                parameters_have_datasets.append(copy.deepcopy(parameter_entry))
                                parameter_entry.clear()
                    for parameter in parameters_have_datasets:
                        datasetRecord_r.append(parameter['key'].encode('utf-8'))
                        datasetRecord_r.append(parameter['value'].encode('utf-8'))
                        outputwriter.writerow(copy.deepcopy(datasetRecord_r))

                        del datasetRecord_r[:]
                        del parameters_have_datasets[:]

    def download_dataset_file(self, url):

        # url = "http://kmmc.in/wp-content/uploads/2014/01/lesson2.pdf"

        file_name = url.split('/')[-1]
        u = urllib2.urlopen(url)
        f = open(file_name, 'wb')
        meta = u.info()
        file_size = int(meta.getheaders("Content-Length")[0])
        print
        "Downloading: %s Bytes: %s" % (file_name, file_size)

        file_size_dl = 0
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break

            file_size_dl += len(buffer)
            f.write(buffer)
            status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
            status = status + chr(8) * (len(status) + 1)
            print
            status,

        f.close()

    def build_download_url(self, datasetRecord_r):

        download_url = ""
        for field in datasetRecord_r:
            print
            field
            """logic"""

        return download_url

    def is_absolute(self, url):
        return bool(urlparse.urlparse(url).netloc)

    def joinurl(self, urla, urlb):
        return urljoin(urla, urlb)


"""experiments"""
if __name__ == '__main__':
    rs = Retrieve_DS()
    rs.get_dataset_paths_into_csv("retrieve", "repository_entry")
    rs.get_dataset_paths_into_csv("read_csv", "csv_file")
    rs.get_dataset_paths_into_csv("read_excel", "excel_file")
    rs.get_dataset_paths_into_csv("read_arff", "data_file")
