#
# Universal Data Plugin
#
#
import os
import hashlib
import requests
import time

import xbmcgui
import xbmcplugin
import xbmcaddon

from urlparse import urlparse, parse_qs
import xml.etree.ElementTree as ET

# ADDON
ADDON_NAME    = 'Universal Data'
ADDON_HEADER  = { 'User-Agent': 'OpenHT/18 (plugin.universal.data)' }
ADDON_CACHE   = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile')).decode('utf-8') + 'cache'
ADDON_CWD     = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')).decode('utf-8')
ADDON_PATH    = sys.argv[0]
ADDON_HANDLE  = int(sys.argv[1])

# TAGS
artwork = [ "icon", "thumb", "poster", "fanart", "clearart", "clearlogo", "banner", "landscape" ]

videos_content = [ "files", "movies", "tvshows", "episodes", "musicvideos", "videos" ]
videos_info = [ "count", "size", "date", "dateadded", "plot", "plotoutline", "duration", "genre", "country", "year", "episode", "season", "sortepisode", "sortseason", "episodeguide", "showlink", "top250", "setid", "tracknumber", "rating", "userrating", "playcount", "overlay", "cast", "castandrole", "director", "mpaa", "title", "originaltitle", "sorttitle", "studio", "tagline", "writer", "tvshowtitle", "premiered", "status", "set", "setoverview", "tag", "imdbnumber", "code", "aired", "credits", "lastplayed", "album", "artist", "votes", "trailer", "mediatype", "dbid" ]
videos_list = [ "cast", "castandrole", "artist" ]

music_content = [ "songs", "artists", "albums" ]
music_info = [ "count", "size", "date", "tracknumber", "discnumber", "duration", "year", "genre", "album", "artist", "title", "rating", "userrating", "lyrics", "playcount", "lastplayed", "mediatype", "dbid", "listeners", "musicbrainztrackid", "musicbrainzartistid", "musicbrainzalbumid", "musicbrainzalbumartistid", "comment" ]

pictures_content = [ "images" ]
pictures_info = [ "count", "size", "date", "title", "picturepath", "exif" ]

games_content = [ "games" ]
games_info = [ "count", "size", "date", "title", "platform", "genres", "publisher", "developer", "overview", "year", "gameclient" ]

internal_info = [ "inputstream", "isplayable", "mimetype", "resumetime", "startoffset", "totaltime", "startpercent", "stationname", "specialsort" ]

sort_tags = [ "date", "dateadded", "size", "duration" ]

def main():
	# ARGS
	args     = parse_qs(sys.argv[2][1:])
	url      = args.get('url', [])
	file     = args.get('file', [])
	id       = args.get('id', [])
	onclick  = args.get('onclick', [])
	action   = args.get('action', [])

	# ROUTER
	if url:
		xml_url(url[0],id)
	elif file:
		xmlfile = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')).decode('utf-8') + '/xml' + file[0]
		xml_file(xmlfile,id)
	elif onclick:
		xml_onclick(onclick)
	elif action:
		xml_action(action[0])
	else:
		xmlfile = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')).decode('utf-8') + '/xml/default.xml'
		xml_file(xmlfile, None)

def xml_action(action):
	if action == 'clearcache':

		for f in os.listdir(ADDON_CACHE):
			if not f.endswith(".xml"):
				continue
			os.remove(os.path.join(ADDON_CACHE, f))

		xbmc.executebuiltin('Notification(Universal Data,Cache cleared,5)')
		sys.exit(1)

	else:
		xbmc.executebuiltin('Notification(Universal Data,Invalid action,5)')
		sys.exit(1)

def xml_onclick(onclick):
	for click in onclick:
		action,condition = click.rsplit(',,,',1)

		if condition:
			if xbmc.getCondVisibility(condition):
				xbmc.executebuiltin(action, False)
		else:
			xbmc.executebuiltin(action, False)

def xml_file(xmlfile,id):
	try:
		with open(xmlfile, 'r') as file:
			xmldata = file.read()
	except:
		xbmc.executebuiltin('Notification(Universal Data,Can\'t open file!,5)')
		sys.exit(1)

	if id:
		xml_parse_id(xmldata,id)
	else:
		xml_parse(xmldata,xmlfile)

def xml_url(url,id):
	urlhash = hashlib.md5()
	urlhash.update(url)
	cachefile = ADDON_CACHE + '/' + urlhash.hexdigest() + '.xml'

	if os.path.isfile(cachefile):

		with open(cachefile, 'r') as file:
			xmldata = file.read()

		try:
			root = ET.fromstring(xmldata)
		except ET.ParseError:
			try:
				r = requests.get(url,headers=ADDON_HEADER)
			except:
				xbmc.executebuiltin('Notification(Universal Data,Can\'t connect to server!,5)')
			else:
				xmldata = r.content
				with open(cachefile, 'w') as file:
					file.write(xmldata)

				try:
					root = ET.fromstring(xmldata)
				except:
					xbmc.executebuiltin('Notification(Universal Data,Invalid XML on server,5)')
					sys.exit(1)
		except:
			xbmc.executebuiltin('Notification(Universal Data,Unknown error,5)')
			sys.exit(1)

		cachetime = int(root.attrib.get('cache', '0'))
		cachelast = int(os.path.getmtime(cachefile))
		unixtime = int(time.time())

		# Cache Expired
		if unixtime - cachelast > cachetime:
			try:
				r = requests.get(url,headers=ADDON_HEADER)
			except:
				xbmc.executebuiltin('Notification(Universal Data,Can\'t connect to server, using cachefile!,5)')
			else:
				xmldata = r.content
				with open(cachefile, 'w') as file:
					file.write(xmldata)
	else:
		try:
			r = requests.get(url,headers=ADDON_HEADER)
		except:
			xbmc.executebuiltin('Notification(Universal Data,Can\'t connect to server, try again later,5)')
			sys.exit(1)
		else:
			xmldata = r.content

		try:
			root = ET.fromstring(xmldata)
		except:
			xbmc.executebuiltin('Notification(Universal Data,Invalid XML,5)')
			sys.exit(1)

		cachetime = int(root.attrib.get('cache', '0'))

		if not cachetime == 0:
			if not os.path.isdir(ADDON_CACHE):
				os.makedirs(ADDON_CACHE)

			with open(cachefile, 'w') as file:
				file.write(xmldata)

	if id:
		xml_parse_id(xmldata,id)
	else:
		xml_parse(xmldata,url)

def xml_parse(xmldata,url):
	try:
		root = ET.fromstring(xmldata)
	except:
		xbmc.executebuiltin('Notification(Universal Data,Invalid XML,5)')
		sys.exit(1)

	sort = root.attrib.get('sort', 'unsorted')
	content = root.attrib.get('type', 'files')
	xbmcplugin.setContent(ADDON_HANDLE,content)
	id = 0

	for item in root:

		# Listitem
		li = xbmcgui.ListItem()

		if url.startswith('http'):
			path = ADDON_PATH + '?url=' + url + '&amp;id=' + str(id)
		else:
			path = ADDON_PATH + '?file=' + url + '&amp;id=' + str(id)

		contextmenu = []
		isFolder = False
		onclick = False
		id = id + 1

		# Sort (Default)
		try:
			xbmcplugin.addSortMethod(ADDON_HANDLE, eval('xbmcplugin.SORT_METHOD_' + sort.upper()))
		except:
			xbmc.executebuiltin('Notification(Universal Data,Invalid Sort Method,5)')
			sys.exit(1)

		for data in item:

			# Label
			if data.tag.lower() == 'label':
				li.setLabel(xbmc.getInfoLabel(data.text.encode('utf-8')))
				#xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
				continue

			# Label2
			if data.tag.lower() == 'label2':
				li.setLabel2(xbmc.getInfoLabel(data.text.encode('utf-8')))
				continue

			# OnClick
			if data.tag.lower() == 'onclick':
				condition = data.attrib.get('condition', '')

				if onclick:
					path += '&amp;onclick=' + data.text + ',,,' + condition
					continue
				else:
					path = ADDON_PATH + '?onclick=' + data.text + ',,,' + condition
					onclick = True
					continue

			# Folder
			if data.tag.lower() == 'folder':
				if url.startswith('http'):
					parsed_url = urlparse(url)
					path = '%s?url=%s://%s%s' % (ADDON_PATH, parsed_url.scheme, parsed_url.netloc, data.text)
				else:
					path = '%s?file=%s' % (ADDON_PATH, data.text)

				isFolder = True
				continue

			# Path
			if data.tag.lower() == 'path':
				path = xbmc.getInfoLabel(data.text.encode('utf-8'))
				continue

			# Properties
			if data.tag.lower() == 'property':
				li.setProperty(data.attrib['name'], xbmc.getInfoLabel(data.text.encode('utf-8')))
				continue

			# Artwork
			if data.tag.lower() in artwork:
				li.setArt({data.tag: xbmc.getInfoLabel(data.text.encode('utf-8'))})
				continue

			# Properties (interal)
			if data.tag.lower() in internal_info:
				li.setProperty(data.tag, xbmc.getInfoLabel(data.text.encode('utf-8')))
				continue

			# Sort
			if data.tag.lower() in sort_tags:
				xbmcplugin.addSortMethod(ADDON_HANDLE, eval('xbmcplugin.SORT_METHOD_' + data.tag.upper()))

			# Info
			if content in videos_content:
				if data.tag.lower() in videos_info:
					li.setInfo('video', {data.tag: xbmc.getInfoLabel(data.text.encode('utf-8'))})
					continue
			elif content in music_content:
				if data.tag.lower() in music_info:
					li.setInfo('music', {data.tag: xbmc.getInfoLabel(data.text.encode('utf-8'))})
					continue
			elif content in pictures_content:
				if data.tag.lower() in pictures_info:
					li.setInfo('pictures', {data.tag: xbmc.getInfoLabel(data.text.encode('utf-8'))})
					continue
			elif content in games_content:
				if data.tag.lower() in games_info:
					li.setInfo('game', {data.tag: xbmc.getInfoLabel(data.text.encode('utf-8'))})
					continue

			# Context
			if data.tag.lower() == 'contextmenu':
				context = data.text.split(",",1)
				try:
					contextmenu.append((context[0], context[1]))
				except:
					xbmc.executebuiltin('Notification(Universal Data,Invalid contextmenu,5)')
					sys.exit(1)

		# Context Menu
		li.addContextMenuItems(contextmenu)

		# Add item
		xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=path, listitem=li, isFolder=isFolder)

	# EndOfDirectory
	xbmcplugin.endOfDirectory(ADDON_HANDLE, cacheToDisc=False)

def xml_parse_id(xmldata,id):
	try:
		root = ET.fromstring(xmldata)
	except:
		xbmc.executebuiltin('Notification(Universal Data,Invalid XML,5)')
		sys.exit(1)

	xbmc.executebuiltin("Dialog.Close(busydialog, true)")
	ui = xbmcgui.WindowXML('script-universaldata-info.xml', ADDON_CWD, 'default', '1080p', False)
	ui.setProperty('content', root.attrib.get('type', 'files'))

	for data in root[int(id[0])]:
		if data.tag == 'property':
			ui.setProperty(data.attrib['name'], data.text)
		else:
			ui.setProperty(data.tag, data.text)

	ui.doModal()
	del ui

if __name__ == "__main__":
	main()
