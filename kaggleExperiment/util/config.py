# dataset search http GET request
# https://www.kaggle.com/datasets_v2.json?sortBy=votes&group=public&page=1&pageSize=20&size=all&filetype=all&license=all
dataset_search_url = 'https://www.kaggle.com/datasets_v2.json'

dataset_params = {}
dataset_params['sortBy'] = 'hottest'
dataset_params['group'] = 'public'
dataset_params['page'] = '1'
dataset_params['pageSize'] = '20'
dataset_params['size'] = 'all'
dataset_params['filetype'] = 'all'
dataset_params['license'] = 'all'

# kernel search http GET request
# https://www.kaggle.com/kernels.json?sortBy=voteCount&group=everyone&pageSize=20&datasetId=310
kernel_search_url = 'https://www.kaggle.com/kernels.json'

search_kernel_params = {}
search_kernel_params['sortBy'] = 'voteCount'  # '','','',''
search_kernel_params['group'] = 'everyone'  # '',''
search_kernel_params['pageSize'] = '20'
search_kernel_params['datasetId'] = ''
search_kernel_params['after'] = ''  # last script/kernel in the response array Id

# request header
user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36'

# mongo config
mongo_db = "kaggle_exper_db"
mongo_collection_name = "kaggle_datasets_a"  # for dataset metadata
mongo_collection_name_for_kernels = "kaggle_kernels_a"  # for kernel metadata
mongo_collection_name_for_opendatasets = "kaggle_datasets_a_open"  # for open datasets metadata

# Kaggle api for dataset downloading
kaggle_cmd_list_param = ['kaggle', 'datasets', 'download', '-d', 'datasetUrl', '-p', 'newDirNamedusingdatasetID', '-o',
                         '-q']
"""

usage: kaggle datasets download [-h] -d DATASET [-f FILE] [-p PATH] [-w] [-o]
                                [-q]

required arguments:
  -d DATASET, --dataset DATASET
                        Dataset URL suffix in format <owner>/<dataset-name> (use "kaggle datasets list" to show options)

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  File name, all files downloaded if not provided
                        (use "kaggle datasets files -d <dataset>" to show options)
  -p PATH, --path PATH  Folder where file(s) will be downloaded, defaults to ~/.kaggle
  -w, --wp              Download files to current working path
  -o, --force           Skip check whether local version of file is up to date, force file download
  -q, --quiet           Suppress printing information about download progress
  
  ex: 'kaggle datasets download -d singhneha/digit-recognizer-using-tensorflow'

"""

# how download link is structued (will not use due to authorization requirments)
download_params = ['owner_slug', 'dataset_slug', 'file_name', 'dataset_version_number']  # noqa: E501

# dataset download folder
dataset_download_dir = 'datasets'

# related research
"""https://github.com/Kaggle/kaggle-api/issues/20"""
