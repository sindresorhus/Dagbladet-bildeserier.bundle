from datetime import date
import lxml
import re


PLUGIN_PREFIX = '/photos/db-bildeserier'
PLUGIN_TITLE = 'Dagbladet bildeserier'
ICON = 'icon-default.png'
ART = 'art-default.jpg'


def Start():
	Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, PLUGIN_TITLE, ICON, ART)
	Plugin.AddViewGroup('Pictures', viewMode='Coverflow', mediaType='photos')
	Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
	MediaContainer.title1 = PLUGIN_TITLE
	MediaContainer.viewGroup = 'InfoList'
	MediaContainer.art = R(ART)
	DirectoryItem.thumb = R(ICON)


def MainMenu():
	dir = MediaContainer(viewGroup='Pictures')
	url = 'http://www.dagbladet.no/bildeserier/'
	# Get all links to articles
	links = HTML.ElementFromURL(url).xpath('//div[@id="rowDZ"]//div[contains(@class,"saveableWo")]/a')
	for link in links:
		title = link.get('title')
		url = link.get('href')
		# Only get galleries with thumbs
		try:
			thumb = link.xpath('img')[0].get('src')
			dir.Append(Function(DirectoryItem(ImageViewer, title=title, thumb=thumb), title=title, url=url))
		except:
			pass
	return dir


def ImageViewer(sender, title='', url=''):
	dir = MediaContainer(viewGroup='List')
	photos = HTML.ElementFromURL(url).xpath('//div[@id="galleryViewPhotos"]//div[@class="panel"]')
	# Check if it's the new gallery, otherwise scrape the old
	if len(photos):
		for photo in photos:
			summary = photo.xpath('div[@class="panel-overlay"]')[0].text_content().strip()
			summary = re.sub(r'Foto:', '\nFoto:', summary)
			title = summary.split(':')[0]
			src = photo.xpath('img[@class="slideImage"]')[0].get('src')
			dir.Append(PhotoItem(src, title=title, summary=summary))
		return dir
	else:
		# Since the images is in JS code, we need to parse out what we need.
		# This can be removed when the old player is phased out.
		html = HTML.ElementFromURL(url).xpath('//div[@id="dzImagesPano"]//script[@type="text/javascript"]')
		html_string = lxml.html.tostring(html[0])
		matches = re.findall(r'addToSlideshow\((.+?)\)', html_string)
		for match in matches:
			item = match.split(',')
			frag = lxml.html.fragment_fromstring(item[3], create_parent='div')
			title = frag.xpath('b')[0].text_content()
			src = item[2].replace('"', '')
			summary = frag.xpath('text()')[1]
			dir.Append(PhotoItem(src, title=title, summary=summary))
		return dir