#!/usr/bin/python3

import sys, http.client, re, json

STOPPED     = 0
DOWNLOADING = 4
UPLOADING   = 6

COLOR1 = '${color}'
COLOR2 = '${color0}'

def error(msg):
    print("Error: %s" % msg, file=sys.stderr)
    sys.exit(1)

def transmission_post(conn, headers={}):

	params = '{"arguments":{"fields":["error","errorString","eta","id","isFinished","leftUntilDone","name","peersGettingFromUs","peersSendingToUs","rateDownload","rateUpload","sizeWhenDone","status","uploadRatio"]},"method":"torrent-get","tag":4}'

	try:
		conn.request('POST', '/transmission/rpc/', params, headers)
	except Exception as e:
		error(e)

	response = conn.getresponse()

	return response.read().decode()

def transmission_list(host):

	conn = http.client.HTTPConnection(host, 9091, timeout=1)

	data = transmission_post(conn)

	matches = re.search('<code>X-Transmission-Session-Id: (.+)</code>', data)
	session_id = matches.group(1)
	headers = {'X-Transmission-Session-Id': session_id}

	data = transmission_post(conn, headers)

	parsed_data = json.loads(data)
	tag = parsed_data['tag']
	arguments = parsed_data['arguments']
	result = parsed_data['result']
	torrents = arguments['torrents']

	torrents_by_id = {}
	for t in torrents:
		if t['status'] != 0:
			torrents_by_id[t['id']] = t

	return torrents_by_id

def bandwidth(bps):
	if bps < 1024:
		return str(bps) + 'B'
	elif bps < 1048576:
		return str(round(bps/1024, 1)) + 'K'
	else:
		return str(round(bps/1048576, 1)) + 'M'

def time_left(s):
	days = int(s/86400)
	s -= days * 86400
	hours = int(s / 3600)
	s -= hours * 3600
	mins = int(s / 60)
	secs = s - mins * 60

	if days > 0:
		return '%dd %dh %02dm %02ds' % (days, hours, mins, secs)
	elif hours > 0:
		return '%dh %02dm %02ds' % (hours, mins, secs)
	elif mins > 0:
		return '%02dm %02ds' % (mins, secs)
	else:
		return '%ds' % secs

def print_torrent(t):
	id = t
	name = t['name']
	upload = bandwidth(t['rateUpload'])
	download = bandwidth(t['rateDownload'])
	if int(t['sizeWhenDone']) > 0:
		progress = round(100 - (int(t['leftUntilDone']) / int(t['sizeWhenDone']) * 100))
	else:
		progress = 0

	if t['eta'] != -1:
		eta = COLOR1 + "ETA " + COLOR2 + time_left(t['eta'])
	else:
		eta = ""

	print('%s%s\n%s%d%% %sUp %s%s %sDown %s%s %s\n' % (COLOR1, name, COLOR2, progress, COLOR1, COLOR2, upload, COLOR1, COLOR2, download, eta))

if __name__ == '__main__':

	if len(sys.argv) != 2:
		error('Usage: transmission-status <host>')
	else:
		host = sys.argv[1]

	torrents = transmission_list(host)

	if len(torrents) == 0:
		print(COLOR2 + "${alignc}No active torrents")
	else:
		for id in torrents:
			t = torrents[id]
			print_torrent(t)
