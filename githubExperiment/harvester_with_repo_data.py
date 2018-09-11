from github import Github
from util.persCred import user, password, token
import csv
from time import gmtime, strftime
import urllib2
import xml.etree.ElementTree as ET  
from xml.dom import minidom
import re
import traceback
from util.loggiingg import logee
from util.config import log_dir, log_file, log_name
import os
from util.mongo import Mongo
from util.config import mongo_db, mongo_collection_name_with_repo_data, rapiminer_files_direct,search_keys, config_counter, config_positive_counter, config_negative_counter, config_trials
from util.config_cred import mongo_host, mongo_port
import time
from collections import defaultdict


class Harvest:



    log = logee(log_dir, log_file, log_name)
    xml_comment_regex = r'\<\!\-\-.{1,1000}\-\-\>'
    # rapiminer_files_direct = str('rapidminer_files_2/')

    # rapiminer_files_direct.encode("utf-8")

    # mongo instance, connection and collection return
    mongo = Mongo()
    collectionObject = mongo.connect(mongo_host, mongo_port, mongo_db, mongo_collection_name_with_repo_data)

    counter = config_counter
    positive_counter = config_positive_counter
    negative_counter = config_negative_counter
    trials = config_trials

    flag = 0

    def __init__(self):
        pass

    """Adding XML contents retrieved from GITHUB API to MongoDB"""
    def putInMongo(self, collectionObject, ET_root_object, id_field):
        try:

            self.mongo.appendDataListToMongo(collectionObject, ET_root_object, id_field)

        except BaseException as e:
            print e.message, e.args
            self.log.logger.error(traceback.format_exc())
            # Logs the error appropriately.
            self.negative_counter = self.negative_counter + 1


    """Parsing XML contents retrieved from GITHUB API"""
    def parseXML(self, type ,xml_content):
            root = -1
            #xml_url_raw= xml_url.replace("https://github.com", "https://raw.githubusercontent.com")
            #print xml_url_raw
            #file = urllib2.urlopen(xml)
            #xml_content = file.read()
            #file.close()
            #print xml_content
            try:
                """minidom"""
                # xml = minidom.parse(xml_content)

                # itemlist = xml.getElementsByTagName('item')
                # print(len(itemlist))
                """element tree"""
                if type == 'file':
                    xml = ET.parse(xml_content)
                    print "ok: XML parsed from a file!"
                    root = xml.getroot()
                if type == 'string':
                    root = ET.fromstring(xml_content)
                    print "ok: XML parsed from a string!"
                """
                # managing XML content
                print len(root[0])
                print root.tag
                print root.attrib
                for child in root:
                    print child.tag, child.attrib

                for neighbor in root.iter('neighbor'):
                    print neighbor.tag, neighbor.attrib
                """
                return root
            except:
                #self.log.logger.error(traceback.format_exc())
                print 'error in parsing xml'
                return root




    """ Dummy ** Harvesting XML contents from GITHUB API"""
    def harvest_a(self):
        # First create a Github instance:
        g = Github(token)
        
        # CSV to store harvested data:
        
        with open('dataset.csv', 'wb') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
            filewriter.writerow(['date', 'html_url','url','git_url','size','path','name','decoded_content','encoding','type'])
            c=0
            for contentFile in g.search_code("connect from_op in:*.rmp language:xml"):
                filewriter.writerow([strftime("%Y-%m-%d %H:%M:%S", gmtime()), contentFile.html_url,contentFile.url,contentFile.git_url,contentFile.size,contentFile.path,contentFile.name,contentFile.decoded_content,contentFile.encoding,contentFile.type])
                c=c+1
                print c

    """ Harvesting XML contents from GITHUB API"""
    def harvest_b(self, search_key):



            # First create a Github instance:
            g = Github(token)
            # CSV to store harvested data:
            paginated_list_of_search_results = g.search_code(query=search_key, sort="indexed", order="asc")



            if not paginated_list_of_search_results:
                print search_key
                print '0 results'
            if str(paginated_list_of_search_results.totalCount) == '0':
                print search_key
                print '0 results'
                return 0
            else:
                print search_key
                print str(paginated_list_of_search_results.totalCount)

                """
                if paginated_list_of_search_results.totalCount < self.trials:
                    self.trials = paginated_list_of_search_results.totalCount
                """

                #if paginated_list_of_search_results.totalCount > 0:
                try:
                    for contentFile in paginated_list_of_search_results:

                        # @TODO enable logging
                        self.counter = self.counter + 1
                        print 'counter : ' + str(self.counter)


                        #check github api status
                        print (g.get_last_api_status_message())
                        print (g.get_api_status_messages())
                        print (g.get_api_status())


                        #print contentFile.html_url
                        #print contentFile.decoded_content

                        #@TODO might have errors some time, check later this part
                        """decoding API message"""
                        xml = contentFile.decoded_content

                        """cleaning  xml content to enable python parser! * this is stupid"""
                        xml_cleaned = re.sub(self.xml_comment_regex, '', xml)
                        xml_cleaned = re.sub('\n', '', xml_cleaned)
                        print xml_cleaned

                        """create directory for xml files if not exist"""
                        if not os.path.exists(rapiminer_files_direct):
                            os.makedirs(rapiminer_files_direct)

                        # @TODO might have errors some time, check later this part
                        """writing xml into files"""
                        xml_file = open(os.path.join(rapiminer_files_direct, contentFile.name), "wb")
                        #f = open(contentFile.name, "wb")
                        xml_file.write(xml_cleaned)
                        xml_file.close()





                        """ parsing xml"""
                        ET_object = self.parseXML('file', rapiminer_files_direct + contentFile.name)
                        if ET_object != -1:
                            # managing XML content
                            print len(ET_object[0])
                            #print ET_object.tag
                            #print ET_object.attrib

                            #for child in ET_object:
                             #   print child.tag, child.attrib
                            """ https://stackoverflow.com/questions/18595791/parse-xml-file-to-fetch-required-data-and-store-it-in-mongodb-database-in-python """
                            """ https://eli.thegreenplace.net/2012/03/15/processing-xml-in-python-with-elementtree/ """
                            for elem in ET_object.iter():
                                print elem.tag, elem.attrib

                            #convert ET to bson / dict for mongo consumbtion
                            """ this will solve redunduncy issue"""
                            ET_object_mongo = defaultdict(list)

                            ET_object_mongo['content'] = contentFile.content

                            ET_object_mongo['download_url'] = contentFile.download_url
                            ET_object_mongo['encoding'] = contentFile.encoding
                            ET_object_mongo['git_url'] = contentFile.git_url
                            ET_object_mongo['html_url'] = contentFile.html_url
                            #ET_object_mongo['license'] = contentFile.license
                            ET_object_mongo['name'] = contentFile.name
                            ET_object_mongo['path'] = contentFile.path
                            # ET_object_mongo['repository'] = contentFile.repository
                            ET_object_mongo['size'] = contentFile.size
                            ET_object_mongo['type'] = contentFile.type
                            ET_object_mongo['url'] = contentFile.url
                            ET_object_mongo['decoded_content'] = contentFile.decoded_content
                            """ repository features """
                            ET_object_mongo['repository_info'] = {}
                            ET_object_mongo['repository_info']['created_at'] = contentFile.repository.created_at
                            ET_object_mongo['repository_info']['description'] = contentFile.repository.description
                            ET_object_mongo['repository_info']['forks_count'] = contentFile.repository.forks_count
                            ET_object_mongo['repository_info']['full_name'] = contentFile.repository.full_name
                            ET_object_mongo['repository_info']['homepage'] = contentFile.repository.homepage
                            ET_object_mongo['repository_info']['language'] = contentFile.repository.language
                            ET_object_mongo['repository_info']['name'] = contentFile.repository.name
                            ET_object_mongo['repository_info']['network_count'] = contentFile.repository.network_count
                            ET_object_mongo['repository_info']['pushed_at'] = contentFile.repository.pushed_at
                            ET_object_mongo['repository_info']['stargazers_count'] = contentFile.repository.stargazers_count
                            ET_object_mongo['repository_info']['updated_at'] = contentFile.repository.updated_at
                            ET_object_mongo['repository_info']['network_count'] = contentFile.repository.network_count
                            ET_object_mongo['repository_info']['watchers_count'] = contentFile.repository.watchers_count

                            """flatening the xml file"""
                            # @TODO might need to keep the nesting?
                            for elem in ET_object.iter():
                                print elem.tag, elem.attrib
                                ET_object_mongo[elem.tag].append(elem.attrib)

                            try:
                                # appending to mongo
                                self.putInMongo(self.collectionObject, ET_object_mongo, "html_url")
                                # appending to mongo
                                # self.putInMongo( self.collectionObject, ET_object)

                                self.positive_counter = self.positive_counter + 1
                                print 'positive_counter : ' + str(self.positive_counter)
                            except:
                                print 'didint go to mongo'
                                # @TODO enable logging
                                self.negative_counter = self.negative_counter + 1
                                print 'negative counter : ' + str(self.negative_counter)
                                #  print 'error in xml file parsing : ' + contentFile.name
                        else:
                            print 'didint parse'
                            # @TODO enable logging
                            self.negative_counter = self.negative_counter + 1
                            print 'negative counter : ' + str(self.negative_counter)
                            #  print 'error in xml file parsing : ' + contentFile.name
                        """
                        #limit to sample size if search results are bigger than sample size
                        if self.counter == self.trials:
                            print 'Totals ... '
                            print 'counter : ' + str(self.counter)
                            print 'negative counter : ' + str(self.negative_counter)
                            print 'positive_counter : ' + str(self.positive_counter)
                            break
                        """
                    print 'Totals ... '
                    print 'counter : ' + str(self.counter)
                    print 'negative counter : ' + str(self.negative_counter)
                    print 'positive_counter : ' + str(self.positive_counter)

                except:
                    # @TODO enable logging
                    self.negative_counter = self.negative_counter + 1
                    print 'negative counter : ' + str(self.negative_counter)
                    #  print 'error in xml file parsing : ' + contentFile.name






"""experiments"""
if __name__ == '__main__':
    harvest = Harvest()
    for search_key in search_keys:
        #print search_key
        harvest.harvest_b(search_key)
        # Wait for 10 seconds [see github search rate limits in notes.txt]
        time.sleep(10)
