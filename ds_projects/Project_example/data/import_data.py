import kaggle
# You need kaggle ID for use this script. Please read https://github.com/Kaggle/kaggle-api
kaggle.api.authenticate()
# import dataset wine quality
url_download = 'rajyellow46/wine-quality'
path = './external'

kaggle.api.dataset_download_files(url_download,path= path, unzip=True)
