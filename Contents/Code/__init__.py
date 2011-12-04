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
	MediaContainer.viewGroup = 'List'
	MediaContainer.art = R(ART)
	DirectoryItem.thumb = R(ICON)
	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2) AppleWebKit/534.52.7 (KHTML, like Gecko) Version/5.1.2 Safari/534.52.7'


def MainMenu():
	dir = MediaContainer(viewGroup='Pictures')
	url = 'http://www.dagbladet.no/bildeserier/'
	# Get all links to articles
	links = HTML.ElementFromURL(url).xpath('//div[@id="rowDZ"]//div[contains(@class,"saveableWo")]/a/img/parent::a')

	for link in links:
		title = link.get('title')
		url = link.get('href')
		thumb = link.xpath('img')[0].get('src')
		dir.Append(Function(DirectoryItem(ImageViewer, title=title, thumb=thumb), title=title, url=url))

	return dir


def ImageViewer(sender, title, url):
	dir = MediaContainer()
	photos = HTML.ElementFromURL(url).xpath('//div[@id="galleryViewPhotos"]//div[@class="panel"]')
	# Check if it's the new gallery, otherwise scrape the old
	if len(photos):
		for photo in photos:
			summary = photo.xpath('./div[@class="panel-overlay"]//text()')
			summary = ' '.join(summary).strip()
			summary = re.sub(r'Foto:', '\nFoto:', summary)
			title = summary.split(':')[0].strip()
			try:
				summary = summary.split(':')[1].strip()
			except:
				pass
			src = photo.xpath('./img[@class="slideImage"]')[0].get('src')
			dir.Append(PhotoItem(src, title=title, summary=summary))
	else:
		# Since the images is in JS code, we need to parse out what we need.
		# This can be removed when the old player is phased out.
		slideshow = HTML.ElementFromURL(url).xpath('//div[@id="dzImagesPano"]//script[@type="text/javascript"]/text()')[0]
		matches = re.findall(r'addToSlideshow\((.+?)\);', slideshow)

		for match in matches:
			item = match.split(',"')
			src = item[2].rstrip('"')

			text = HTML.ElementFromString( item[3].rstrip('"') )
			title = text.xpath('//b')[0].text.rstrip(': ').replace("\\'", "'")
			summary = text.xpath('//text()')[1].replace("\\'", "'")

			dir.Append(PhotoItem(src, title=title, summary=summary))

	return dir
