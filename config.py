config['debug'] = False

if '/boot' in config['filesystems']:
    config['filesystems'].remove('/boot')

config['filesystems'].append('/tmp')

config['torrents_host'] = 'nil'

