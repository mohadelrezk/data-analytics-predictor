from github import Github
from util.persCred import user, password, token
from util.config import mongo_db, mongo_collection_name_for_datasets, analysis_output_folder
from util.config_cred import mongo_host, mongo_port

from util.mongo import Mongo
from collections import defaultdict

import csv
import ntpath
import time
import copy


class repo_search:
    # mongo instance, connection and collection return
    mongo = Mongo()
    collectionObject = mongo.connect(mongo_host, mongo_port, mongo_db, mongo_collection_name_for_datasets)

    def search_repo_for_file(self, repo_name, file_name, filetype):

        # First create a Github instance:
        g = Github(token)
        # constrct repositiry search key
        search_key = file_name + ' repo:' + repo_name + ' language:' + filetype
        # search github and store paginated list response
        paginated_list_of_search_results = g.search_code(query=search_key, sort="indexed", order="asc")
        # output rows starting with constrcted search key
        csv_row_for_analysis = []
        csv_row_for_analysis.append(search_key)
        # check if response / search results is embty
        if not paginated_list_of_search_results:
            print search_key
            print '0 results'
            csv_row_for_analysis.append(0)
        if str(paginated_list_of_search_results.totalCount) == '0':
            print search_key
            print '0 results'
            csv_row_for_analysis.append(0)
        # check if search results not empty
        else:
            print search_key
            csv_row_for_analysis.append(paginated_list_of_search_results.totalCount)

            """
            if paginated_list_of_search_results.totalCount < self.trials:
                self.trials = paginated_list_of_search_results.totalCount
            """

            # if search results not empty -- > paginated_list_of_search_results.totalCount > 0:
            try:
                # loop through rsearch esults
                for contentFile in paginated_list_of_search_results:
                    print contentFile.path
                    # look for the path to the dataset file found, if it ends with the right file extension
                    if contentFile.path.endswith('.' + filetype) or contentFile.path.endswith('.' + filetype.lower()):
                        print contentFile.path
                        csv_row_for_analysis.append(contentFile.path)

            except:
                print 'error in paginated list looping'

        return csv_row_for_analysis

    def get_file_name(self, path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)

    def start_search(self, csv_input, repo_row, file_row, filetype):

        header = ['search query', 'total_found', filetype + 's found', 'path']

        with open(
                csv_input) as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            next(readCSV)  # skip header
            c = 0

            with open(csv_input + "_whatsongithub_.csv",
                      'w+') as output:
                outputwriter = csv.writer(output, delimiter=',', quotechar='\"')
                # putting the header
                outputwriter.writerow(header)

                row_list = []
                for row in readCSV:
                    # print c
                    # print row[9]
                    # print repo_s.get_file_name(row[12])
                    # print str(len(row))
                    # print "repo_row = " + str(repo_row)
                    # print "file_row = " + str(file_row)
                    row_list = self.search_repo_for_file(row[repo_row], repo_s.get_file_name(row[file_row]), filetype)
                    row_list.append(row[file_row])
                    outputwriter.writerow(copy.deepcopy(row_list))
                    del row_list[:]
                    c += 1
                    # Wait for 10 seconds [see github search rate limits in notes.txt]
                    time.sleep(30)


"""experiments"""
if __name__ == '__main__':
    files = \
        [
            ['analysis_output/read_arff_AND_data_file_datasets.csv', 9, 12, 'ARFF']
            , ['analysis_output/read_csv_AND_csv_file_datasets.csv', 9, 12, 'CSV']
            , ['analysis_output/read_excel_AND_excel_file_datasets.csv', 9, 12, 'EXCEL']
            # ,['/Users/mohade/GoogleDrive/workspace/data-analytics-predictor/analysis_output_bk/retrieve_AND_repository_entry_datasets.csv',9,12, '']
        ]

    repo_s = repo_search()

    for input_csv in files:
        repo_s.start_search(input_csv[0], input_csv[1], input_csv[2], input_csv[3])
