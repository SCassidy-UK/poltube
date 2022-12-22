import rootpath

root = rootpath.detect(pattern='requirements.txt')

filepaths = {
        'cookie': f'{root}/cookie.json',
        'api-key': f'{root}/.api-key.txt',
        'output': f'{root}/data/raw/rawchanneldata.json',
        'channels': f'{root}/data/channels.csv',
        'cache': f'{root}/data/idcache.csv',
        }
