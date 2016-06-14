# -*- coding: utf-8 -*-
import urllib,urllib2,re,xbmcplugin,xbmcgui,xbmcaddon,string,random,cookielib,xbmcvfs

import time
import json
import libMediathek
import resources.lib._utils as _utils

baseUrl = 'http://em.zdf.de/'
baseFeed = 'http://em.zdf.de/feeds/myviewfilter/'
feed = 'http://em.zdf.de/feeds/myviewfilter/myviewlatest/'
pluginhandle = int(sys.argv[1])

def main():
	libMediathek.addEntry({'name':'Neuste Videos',         'mode':'listVideos', 'type': 'dir', 'url' : 'http://em.zdf.de/feeds/myviewfilter/myviewlatest/'})
	libMediathek.addEntry({'name':'Spielbegegnungen',      'mode':'listFilter', 'type': 'dir', 'filtertype' : 'match'})
	libMediathek.addEntry({'name':'Teams',                 'mode':'listFilter', 'type': 'dir', 'filtertype' : 'team'})
	libMediathek.addEntry({'name':'Highlights',            'mode':'listFilter', 'type': 'dir', 'filtertype' : 'action'})
	libMediathek.addEntry({'name':'Spieler',               'mode':'listFilter', 'type': 'dir', 'filtertype' : 'player'})
	
	
def listFilter():
	list = []
	response = _utils.getUrl(feed)
	j = json.loads(response)
	for filter in j['myviewfilter']['data']:
		if filter['type'] == params['filtertype'] and filter['enabled']:
			dict = {}
			if filter['type'] == 'match':
				dict['name'] = filter['round_name'] + ': ' + filter['home_team']['name'] + ' - ' + filter['away_team']['name']
				dict['plot'] = filter['round_name'] + '\n' + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(filter['start']))
				dict['url'] = baseFeed + filter['value']
			elif filter['type'] == 'team' or filter['type'] == 'player':
				dict['name'] = filter['name']
			elif filter['type'] == 'action':
				dict['name'] = filter['action_title']
				
			dict['url'] = baseFeed + filter['value']
			dict['type'] = 'dir'
			dict['mode'] = 'listVideos'
			list.append(dict)
	libMediathek.addEntries(list)
	
def listVideos():
	list = []
	response = _utils.getUrl(params['url'])
	j = json.loads(response)
	#xbmc.log(str(j))
	for k in j:
		if k != 'myviewfilter':
			key = k
	for data in j[key]['data']:
		dict = {}
		dict['url'] = baseUrl + data["url"]
		dict['name'] = data["title"] + ' (' + str(data['video_count']) + ')'
		dict['nameclean'] = data["title"]
		dict['myview_id'] = data["myview_id"]
		dict['thumb'] = data["thumbnails"][0]["url"]
		
		if data['video_count'] == 1:
			dict['plot'] = '1 Kameraperspektive'
			dict['type'] = 'video'
			dict['mode'] = 'play'
		else:
			dict['plot'] = str(data['video_count']) + 'Kameraperspektiven'
			dict['type'] = 'dir'
			dict['mode'] = 'listViews'
		list.append(dict)
	libMediathek.addEntries(list)
	
def listViews():
	list = []
	response = _utils.getUrl(params['url'])
	cameras = re.compile('<div class="cameras">(.+?)</div>', re.DOTALL).findall(response)[0]
	perspectives = re.compile('<a(.+?)</a>', re.DOTALL).findall(cameras)
	for persp in perspectives:
		dict = {}
		#dict['name'] = re.compile('title="(.+?)"', re.DOTALL).findall(persp)[0]
		dict['perspective'] = re.compile('<span>(.+?)</span>', re.DOTALL).findall(persp)[0].replace('tv','TV')
		dict['name'] = 'Perspektive "'+ dict['perspective'] + '"'
		dict['url'] = baseUrl + re.compile('href="(.+?)"', re.DOTALL).findall(persp)[0]
		dict['thumb'] = params['thumb']
		
		dict['mode'] = 'play'
		dict['type'] = 'video'
		dict['orgName'] = params['nameclean']
		list.append(dict)
	libMediathek.addEntries(list)
	
def play():
	response = _utils.getUrl(params['url'])
	mp4 = re.compile('<meta name="assetmp4" content="(.+?)"', re.DOTALL).findall(response)[0]
	response = _utils.getUrl('http://em.zdf.de/myview/token/')
	token = re.compile('"(.+?)"', re.DOTALL).findall(response)[-1]
	
	url = mp4 + '?' + token
	
	listitem = xbmcgui.ListItem(path=url)
	if 'orgName' in params:
		listitem.setInfo( type="Video", infoLabels={"Title": params['orgName'] + ' - Perspektive "' + params['perspective'] + '"'})
	xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
	
	
	
	



params=libMediathek.get_params()
if not params.has_key('mode'):
	main()
elif params['mode'] == 'listFilter':
	listFilter()
elif params['mode'] == 'listVideos':
	listVideos()
elif params['mode'] == 'listViews':
	listViews()
elif params['mode'] == 'play':
	play()
xbmcplugin.endOfDirectory(int(sys.argv[1]))
