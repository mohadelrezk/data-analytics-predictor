import os



mongo_db = "dataAnalytical_db"
mongo_collection_name = "dataAnalytical_collection_from_op_2"
mongo_collection_name_with_repo_data = "dataAnalytical_collection_from_op_2_with_repo"
mongo_collection_name_for_datasets = "ds_dataAnalytical_collection_1"

rapiminer_files_direct = str('Harvesting/rapidminer_files_from_op_2/')

#search_keys = ["connect from_op in:*.rpm language:xml", "connect from_op in:*.xml language:xml", "connect from_op in:*.rpm", "connect from_op in:*.xml","connect from_op in:*.rmp language:xml","connect from_op in:*.rmp", "connect from_op"]
#search_keys = ["connect from_op"]
#search_keys = ['key="repository_entry"']
#search_keys = ['key="csv_file" language:xml extension:rmp']
#search_keys = ['key="repository_entry" language:xml']
#search_keys = ['key="source entry" language:xml in:*.rmp']

#search_keys = ["connect from_op"] #5219
file_size = "size:>40000" #in bytes
repository_pushed = "pushed:2016-04-30..2016-07-04"
search_keys = [ "connect from_op", "connect from_op size:>=40000", "connect from_op size:<=1000",
                "connect from_op size:1000..2000","connect from_op size:2000..3000","connect from_op size:3000..4000","connect from_op size:4000..5000" , "connect from_op size:5000..6000",
                "connect from_op size:6000..7000", "connect from_op size:7000..8000","connect from_op size:8000..9000","connect from_op size:9000..10000",
                "connect from_op size:10000..15000", "connect from_op size:15000..20000", "connect from_op size:20000..25000",
                "connect from_op size:25000..30000", "connect from_op size:30000..35000", "connect from_op size:35000..40000",
                "connect from_op size:2000","connect from_op size:3000", "connect from_op size:4000",  "connect from_op size:5000","connect from_op size:6000", "connect from_op size:7000", "connect from_op size:8000",
                "connect from_op size:9000","connect from_op size:10000", "connect from_op size:15000",
                "connect from_op size:20000", "connect from_op size:25000", "connect from_op size:30000", "connect from_op size:35000"]
#search_keys = ["connect from_op in:*.rpm language:xml "] #293
#search_keys = ["connect from_op language:xml "] #293

search_file_in_repo = "repo:"

# counter and trials for testing goals
config_counter = 0
config_positive_counter = 0
config_negative_counter = 0
config_trials = 6000




log_dir = os.path.abspath( os.path.join(os.path.dirname(__file__),os.pardir,'logs'))
log_file=log_dir+"/service.log"
log_name="sci-analytics-crowler"


analysis_output_folder = "analysis_output/"




#steps

"""
harvest

"""