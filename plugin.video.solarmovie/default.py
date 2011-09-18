import re, string, sys, os
from urllib2 import Request, urlopen, URLError, HTTPError
from t0mm0.common.addon import Addon
from t0mm0.common.addon import ContextMenu
from t0mm0.common.net import Net
import urlresolver
import xbmcaddon,xbmc,xbmcgui
from random import SystemRandom

REMOTE_DBG = False

# append pydev remote debugger
if REMOTE_DBG:
    # Make pydev debugger works for auto reload.
    # Note pydevd module need to be copied in XBMC\system\python\Lib\pysrc
    try:
        import pysrc.pydevd as pydevd
        # stdoutToServer and stderrToServer redirect stdout and stderr to 
        #eclipse console
        pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True)
    except ImportError:
        sys.stderr.write("Error: " +
            "You must add org.python.pydev.debug.pysrc to your PYTHONPATH.")
        sys.exit(1)
        
numpagesindex = { '0' : 1, '1' : 2, '2' : 3, '3' : 4, '4' : 5, '5' : 6,
                  '6' : 7, '7' : 8, '8' : 9, '9' : 10 }

catagories = [ 'Action', 'Adult', 'Adventure', 'Animation', 'Biography',
               'Comedy', 'Crime', 'Documentary', 'Drama', 'Family', 
               'Fantasy', 'Film Noir', 'Game Show', 'History', 'Horror', 
               'Music', 'Mystical', 'News', 'Reality TV', 'Romance', 
               'Sci-Fi', 'Short', 'Sport', 'Talk Show', 'Thriller', 
               'War', 'Western' ]


addon = Addon('plugin.video.solarmovie', sys.argv)
cm = ContextMenu(addon)
net = Net()
net.set_user_agent('Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; yie9)')

base_url = 'http://www.solarmovie.eu'
mode = addon.queries['mode']
play = addon.queries.get('play', None)

solarpath = addon.get_path()
smallimage = os.path.join(xbmc.translatePath(solarpath), \
                          'art','logo_in_gold_black.jpg')

numpages = numpagesindex[addon.get_setting('numpages')]
maxlinks = int(addon.get_setting('maxlinks'))
hideadult = addon.get_setting('hideadult')
enableproxy = addon.get_setting('proxy_enable')
proxyserver = addon.get_setting('proxy_server')
proxyport = addon.get_setting('proxy_port')
proxyuser = addon.get_setting('proxy_user')
proxypass = addon.get_setting('proxy_pass')


if enableproxy == 'true':
    proxy = 'http://'
    if proxyuser:
        proxy = '%s%s:%s@%s:%s' %(proxy, proxyuser, proxypass,
                                  proxyserver, proxyport)
    else:
        proxy = '%s%s:%s' % (proxy, proxyserver, proxyport)
    net.set_proxy(proxy)
    try:
        html = net.http_GET('http://www.google.com').content
    except HTTPError, e:

        heading = '%s %d' % ('Proxy Error', e.code)
        addon.show_small_popup(heading,'Change your proxy settings',5000,
                               smallimage)
        net.set_proxy('')


def MatchMovieEntries(html):
    match=re.compile('<img src="(.+?)"\n            width="150"' +
                     ' height="220" alt="" />\n    </a>\n    ' +
                     '<span class="movieName">\n        <a title="(.+?)"' +
                     '\n            href="(.+?)">').findall(html)
    return match


def MatchTvEntries(html):
    match=re.compile('<img src="(.+?)"\n.*width.+?\n\s+</a>\n\s+<span.+?\n' +
                     '\s+<a title="(.+?)"\n\s+href="(.+?)"').findall(html)
    return match


def GetSeachHTML(url):
    req = Request(url)
    try:
        urlopen(req)
    except HTTPError, e:
        html = e.read()
    return html
                     

def FindIframeLink(url):
    html = net.http_GET(url).content
    r = re.search('<iframe name=\'svcframe\' id=\'svcframe\' src="(.+?)"' +
                  ' allowtransparency', html)
    if r:
        return r.group(1)
    r = re.search('<center><iframe src="(.+)" width', html)
    if r:
        return r.group(1)
    r = re.search('</param><embed src="(.+?)" type="', html)
    if r:
        return r.group(1)
    r = re.search('px\' src=\'(.+?)\' scrolling=\'', html)
    if r:
        return r.group(1)


if play:
    html = net.http_GET(play).content
    mydict = addon.parse_query(sys.argv[2])
    count = 0
    sources = {}
    expr = re.compile('[a|;"]\s\shref="/link/.+/(\d+)/">(.+)</a>\n.*</td>\n.*verionFavoriteCell.*\n.*</td>\n\n.*oddCell">\n.*centered">(.+?)&.*title="(.+?)" />')
    match = expr.findall(html)
    if match:
        for linkid, title, rating, votes in match:
            url = base_url + '/movie/playlink/id/' + linkid + '/part/1/'
            hosting_url = FindIframeLink(url)
            if hosting_url:
                mymsg = 'Trying to resolve' + hosting_url
                addon.log_debug(mymsg)
                title = addon.decode(title)
                displayname = '%s %s (%s)' % (title, votes, rating)
                sources[hosting_url] = displayname
                count += 1
                if count == maxlinks:
                    break
        stream_url = urlresolver.choose_source(sources)
        addon.resolve_url(stream_url)
    else:
        addon.show_small_popup('SolarMovie','No sources available',3000,
                               smallimage)


elif mode == 'findsolarmovies':
    cm.add_context('Jump to favorites', { 'mode' : 'showfavorites' }, True)
    cm.add_context('Go to addon main screen', { 'mode' : 'main' }, True)
    cm.add_favorite('Save solarmovie favorite', 
                                  { 'mode' : 'play' },'savefavorite', 
                                  'movie')
    page = 1
    url = addon.queries['url']
    while page <= numpages:
        if addon.queries['multipage'] == 'yes':
            url = ('%s?page=%s') % (addon.queries['url'], page)
        else:
            page = 9998
        html = net.http_GET(url).content
        match = MatchMovieEntries(html)        
        for thumbnail, title, url in match:
            url = base_url + url
            addon.add_video_item( url, { 'title' : title }, thumbnail, cm=cm)
        page = page + 1


elif mode == 'findsolartvshows':
    cm.add_context('Jump to favorites', { 'mode' : 'showfavorites' }, True)
    cm.add_context('Go to addon main screen', { 'mode' : 'main' }, True)
    cm.add_favorite('Save solarmovie favorite', 
                                  { 'mode' : 'findtvseason' },'savefavorite', 
                                  'tv')
    page = 1
    url = addon.queries['url']
    while page <= numpages:
        if addon.queries['multipage'] == 'yes':
            if page == 1:
                url = addon.queries['url']
            else:
                url = ('%s?page=%s') % (addon.queries['url'], page)
        else:
            page = 9998
        html = net.http_GET(url).content
        match = MatchTvEntries(html)
        for thumbnail, title, url in match:
            url = base_url + url
            addon.add_directory( { 'mode' : 'findtvseasons', 'type' : 'tv',
                                  'url' : url}, title, thumbnail, cm=cm)
        page = page + 1
        

elif mode == 'findtvseasons':
    cm.add_context('Jump to favorites', { 'mode' : 'showfavorites' }, True)
    cm.add_context('Go to addon main screen', { 'mode' : 'main' }, True)
    cm.add_favorite('Save solarmovie favorite', 
                                  { 'mode' : 'findepisodes' },'savefavorite', 
                                  'tv')
    html = net.http_GET(addon.queries['url']).content
    match=re.compile('<h4><a href="(.+?)">\n\s+Season\s(.+?)</a>').findall(html)
    if match:
        dict = {}
        for url, season in match:
            season = season.rjust(2,'0')
            title = 'Season %s' % (season)
            url = '%s%s' % (base_url, url)
            dict[season] = { 'url' : url, 'title' : title }
        for key in sorted(dict.iterkeys()):
            addon.add_directory( { 'mode' : 'findepisodes' , 'type' : 'tv', 
                                  'url' : dict[key]['url']}, dict[key]['title'], 
                                cm=cm)
    

elif mode == 'findepisodes':
    cm.add_context('Jump to favorites', { 'mode' : 'showfavorites' }, True)
    cm.add_context('Go to addon main screen', { 'mode' : 'main' }, True)
    cm.add_favorite('Save solarmovie favorite', 
                                  { 'mode' : 'play' },'savefavorite', 
                                  'tv')
    html = net.http_GET(addon.queries['url']).content
    match=re.compile('">Episode\s(\d+)</a>\n\s+</span>\n\n\s+<span class.+?\n' +
                     '\s+<span class.+?\n\n\s+<a href="(.+?)">(.+?)</a>\n').findall(html)
    if match:
        dict = {}
        for episode, url, title in match:
            episode = episode.rjust(2,'0')
            url = '%s%s' % (base_url, url)
            title = 'Episode %s  (%s)' % (episode, title)
            dict[episode] = {'url' : url, 'title' : title }
        for key in sorted(dict.iterkeys()):
            addon.add_video_item(dict[key]['url'], { 'title' : dict[key]['title'] }, cm=cm)


elif mode == 'genres':
    for catagori in catagories:
        
        title = catagori
        if title == 'Adult' and hideadult == 'true':
            pass
        else:
            if addon.queries['type'] == 'movies':
                url = 'http://www.solarmovie.eu/watch-%s-movies.html' % (catagori)
                addon.add_directory({'mode' : 'findsolarmovies', 'url' : url, 
                                     'multipage' : 'yes' }, title, cm=cm)
            else:
                url = 'http://www.solarmovie.eu/tv/watch-%s-tv-shows.html/' % (catagori)
                addon.add_directory({'mode' : 'findsolartvshows', 'url' : url, 
                                     'multipage' : 'yes' }, title, cm=cm)


elif mode == 'main':
    html = net.http_GET('http://www.solarmovie.eu/movies/').content
    r = re.search('The website is temporally down', html)
    if r:
        addon.show_small_popup('SolarMovie','Website is temporally down', 5000, 
                               smallimage)
    else:
        #addon.show_small_popup('SolarMovie','Is now loaded enjoy',5000,
        #                       smallimage)
        
        cm.add_context('Go to addon main screen', { 'mode' : 'main' }, True)
        cm.add_favorite('Save solarmovie favorite', 
                                  { 'mode' : 'findsolarmovies' },'savefavorite', 
                                  'movie')
        addon.add_directory( { 'mode' : 'movies'}, 'Movies')
        addon.add_directory( { 'mode' : 'tv'}, 'Tv shows')
        addon.add_directory({'mode' : 'showfavorites' }, 'Favorites')
        

elif mode == 'movies':
    cm.add_context('Go to addon main screen', { 'mode' : 'main' }, True)
    cm.add_favorite('Save solarmovie favorite', { 'mode' : 'findsolarmovies' },
                    'savefavorite', 'movie')
    addon.add_directory({'mode' : 'findsolarmovies', 
                     'url' : 'http://www.solarmovie.eu/movies/', 
                     'multipage' : 'no'}, 'Most Popular Movies Today',
                    cm=cm)
    addon.add_directory( { 'mode' : 'genres', 'type' : 'movies'}, 'Genres')
    addon.add_directory( {'mode' : 'moviesearch'}, 'Search')


elif mode == 'tv':
    cm.add_context('Go to addon main screen', { 'mode' : 'main' }, True)
    cm.add_favorite('Save solarmovie favorite', { 'mode' : 'findsolarmovies' },
                    'savefavorite', 'tv')
    
    addon.add_directory({'mode' : 'findsolartvshows', 
                         'url' : 'http://www.solarmovie.eu/tv/', 
                         'multipage' : 'no'}, 'Most Popular TV shows Today',
                        cm=cm)
    addon.add_directory( { 'mode' : 'genres', 'type' : 'tv'}, 'Genres')
    addon.add_directory( {'mode' : 'tvsearch'}, 'Search')


elif mode == 'resolver_settings':
    urlresolver.display_settings()


elif mode == 'savefavorite':
    test = addon.save_favorite()
    if test is False:
        addon.show_small_popup(msg='Unable to save favorite')
    else:
        addon.show_small_popup(msg='Favorite saved')


elif mode == 'moviesearch':
    html = ''
    cm.add_context('Jump to favorites', { 'mode' : 'showfavorites' }, True)
    cm.add_context('Go to addon main screen', { 'mode' : 'main' }, True)
    cm.add_favorite('Save solarmovie favorite', 
                                  { 'mode' : 'play' },'savefavorite', 
                                  'movie')
    kb = xbmc.Keyboard('', 'Search Solarmovies', False)
    kb.doModal()
    if kb.isConfirmed():
        text = kb.getText()
        if text != '':
            dict = {}
            searchurl = '%s/movie/search/?query=%s' % (base_url, text)
            page = 1
            while page <= 3:
                if page == 1:
                    url = searchurl
                else:
                    url = '%s&page=%s' % (searchurl, page)
                    
                html = GetSeachHTML(url)
                r = re.search('Nothing was found by your request', html)
                if r:
                    page = 9998
                else:
                    match = MatchMovieEntries(html)
                    for thumbnail, title, url in match:
                        url = base_url + url
                        dict[title] = { 'thumbnail' : thumbnail, 
                                       'title' : title, 'url' : url }
                page = page + 1
            # Do key stuff and add video items.
            for key in sorted (dict.iterkeys()):
                addon.add_video_item( dict[key]['url'], 
                                      { 'title' : dict[key]['title'] }, 
                                      dict[key]['thumbnail'], cm=cm)


elif mode == 'tvsearch':
    html = ''
    cm.add_context('Jump to favorites', { 'mode' : 'showfavorites' }, True)
    cm.add_context('Go to addon main screen', { 'mode' : 'main' }, True)
    cm.add_favorite('Save solarmovie favorite', 
                                  { 'mode' : 'findtvseasons' },'savefavorite', 
                                  'tv')
    kb = xbmc.Keyboard('', 'Search Solarmovies', False)
    kb.doModal()
    if kb.isConfirmed():
        text = kb.getText()
        if text != '':
            url = '%s/movie/search/?query=%s&part=series' % (base_url, text)
            html = GetSeachHTML(url)
            r = re.search('Nothing was found by your request', html)
            if r:
                pass
            else:
                match = MatchTvEntries(html)
                if match:
                    dict = {}
                    for thumbnail, title, url in match:
                        url = base_url + url
                        dict[title] = {'title' : title, 'url' : url, 'thumbnail' : thumbnail}
                    for key in sorted(dict.iterkeys()):
                        addon.add_directory( { 'mode' : 'findtvseasons', 
                                              'type' : 'tv', 
                                              'url' : dict[key]['url'], 
                                              'multipage' : 'no'}, 
                                            dict[key]['title'], 
                                            dict[key]['thumbnail'], cm=cm)


elif mode == 'deletefavorite':
    addon.del_favorite()


elif mode == 'showfavorites':
    favorites = addon.show_favorites( {'movies' : 'Movies', 'tv' : 'TV Shows' } )
    if favorites:
        cm.add_favorite('Delete favorite',{ 'mode' : 'deletefavorite'}, 
                        'deletefavorite', addon.queries['favtype'] )
        for data in favorites:
            if data['callback'] == 'play':
                addon.add_item(data['url'], { 'title' : data['title']}, 
                              item_type=data['item_type'], cm=cm)
            else:
                addon.add_directory(data['queries'], data['title'], cm=cm)


if not play:
    addon.end_of_directory()




