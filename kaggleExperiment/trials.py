from kaggle import kaggle

# mongo
from util.mongo import Mongo
from util.config import mongo_db, mongo_collection_name as dataset_collection, \
    mongo_collection_name_for_kernels as kernels_collection, mongo_collection_name_for_opendatasets
from util.config_cred import mongo_host, mongo_port



kag = kaggle()
# kag.harvest_datasets()
#kag.get_open_licence_datasets(originCollection=dataset_collection,
#                              destinationCollection=mongo_collection_name_for_opendatasets)
