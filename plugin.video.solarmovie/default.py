import re
import string
import sys
import os
from t0mm0.common.addon import Addon
from t0mm0.common.net import Net
# from t0mm0.common.proxyscraper import Proxyscraper
import urlresolver
import xbmcaddon,xbmc

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


addon = Addon('plugin.video.solarmovie', sys.argv)
#proxyscraper = Proxyscraper(1,4)
#proxy, location, proxytype = proxyscraper.find_proxy('us',False,'ANM')
#net = Net('',proxy)
net = Net()

addondata = xbmcaddon.Addon(id='plugin.video.solarmovie')
solarpath = addondata.getAddonInfo('path')
smallimage = os.path.join(xbmc.translatePath(solarpath), \
                          'art','logo_in_gold_black.jpg')

base_url = 'http://www.solarmovie.eu'

mode = addon.queries['mode']
play = addon.queries.get('play', None)



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
    
    r = re.search('px src=\'(.+?)\' scrolling=\'', html)
    if r:
        return r.group(1)




if play:
    html = net.http_GET(play).content
    count = 0
    total = 10
    sources = {}
    expr = re.compile('[a|;"]\s\shref="/link/.+/(\d+)/">(.+)</a>\n.*</td>\n.*verionFavoriteCell.*\n.*</td>\n\n.*oddCell">\n.*centered">(.+?)&.*title="(.+?)" />')
    match = expr.findall(html)
    if len(match) > 0:
        for linkid, title, rating, votes in match:
            url = base_url + '/movie/playlink/id/' + linkid + '/part/1/'
            hosting_url = FindIframeLink(url)
            if hosting_url:
                verified = urlresolver.resolve(hosting_url)
                if verified:
                    displayname = '%s %s (%s)' % (
                                                        title, votes, rating)
                    mymsg = 'Adding hosting_url to sources: ' + hosting_url
                    addon.log_error(mymsg)
                    sources[hosting_url] = displayname
                    count += 1
                    if count == total:
                        break
        stream_url = urlresolver.choose_source(sources)
        addon.resolve_url(stream_url)
    else:
        addon.log_error('No matching source links')


elif mode == 'resolver_settings':
    urlresolver.display_settings()

elif mode == 'search':
    pass

            

elif mode == 'findsolarmovies':
    print 'Called find the movies on the solarmovies page'
    html = net.http_GET(addon.queries['url']).content
    try:
        match=re.compile('<img src="(.+?)"\n            width="150"' +
                         ' height="220" alt="" />\n    </a>\n    ' +
                         '<span class="movieName">\n        <a title="(.+?)"' +
                         '\n            href="(.+?)">').findall(html)
        for thumbnail, title, url in match:
            url = base_url + url
            # This should be add_movie_item
            addon.add_video_item( url, { 'title' : title }, img=thumbnail)
            
    except:
        pass

    
elif mode == 'main':
    addon.show_small_popup('SolarMovie','Is now loaded enjoy','5000',smallimage)
    addon.add_directory({'mode' : 'findsolarmovies', 'url' : 'http://www.solarmovie.eu/movies/'}, 'Most Popular Movies Today')
    addon.add_directory({'mode' : 'findsolarmovies', 'url' : 'http://www.solarmovie.eu/tv/'}, 'Most Popular TV shows Today')
    addon.add_directory({'mode' : 'findsolarmovies', 'url' : 'http://www.solarmovie.eu/watch-action-movies.html'}, 'Action')
    addon.add_directory({'mode' : 'findsolarmovies', 'url' : 'http://www.solarmovie.eu/watch-adult-movies.html'}, 'Adult')    
    addon.add_directory({'mode' : 'findsolarmovies', 'url' : 'http://www.solarmovie.eu/watch-adventure-movies.html'}, 'Adventure')
    addon.add_directory({'mode' : 'findsolarmovies', 'url' : 'http://www.solarmovie.eu/watch-animation-movies.html'}, 'Animation')
    addon.add_directory({'mode' : 'findsolarmovies', 'url' : 'http://www.solarmovie.eu/watch-biography-movies.html'}, 'Biography')
    addon.add_directory({'mode' : 'findsolarmovies', 'url' : 'http://www.solarmovie.eu/watch-comedy-movies.html'}, 'Comedy')
    addon.add_directory({'mode' : 'findsolarmovies', 'url' : 'http://www.solarmovie.eu/watch-crime-movies.html'}, 'Crime')
    addon.add_directory({'mode' : 'findsolarmovies', 'url' : 'http://www.solarmovie.eu/watch-documentary-movies.html'}, 'Documentary')
    addon.add_directory({'mode' : 'findsolarmovies', 'url' : 'http://www.solarmovie.eu/watch-drama-movies.html'}, 'Drama')
    addon.add_directory({'mode' : 'findsolarmovies', 'url' : 'http://www.solarmovie.eu/watch-family-movies.htm'}, 'Family')
    addon.add_directory({'mode' : 'findsolarmovies', 'url' : 'http://www.solarmovie.eu/watch-fantasy-movies.html'}, 'Fantasy')
    addon.add_directory({'mode' : 'findsolarmovies', 'url' : 'http://www.solarmovie.eu/watch-film-noir-movies.html'}, 'Film Noir')
    addon.add_directory({'mode' : 'findsolarmovies', 'url' : 'http://www.solarmovie.eu/watch-game-show-movies.html'}, 'Game Show')
    addon.add_directory({'mode' : 'findsolarmovies', 'url' : 'http://www.solarmovie.eu/watch-history-movies.html'}, 'History')
    addon.add_directory({'mode' : 'findsolarmovies', 'url' : 'http://www.solarmovie.eu/watch-horror-movies.html'}, 'Horror')
    addon.add_directory({'mode' : 'findsolarmovies', 'url' : 'http://www.solarmovie.eu/watch-musical-movies.html'}, 'Music')
    addon.add_directory({'mode' : 'findsolarmovies', 'url' : 'http://www.solarmovie.eu/watch-action-movies.html'}, 'Mystical')
    addon.add_directory({'mode' : 'findsolarmovies', 'url' : 'http://www.solarmovie.eu/watch-news-movies.html'}, 'News')
    addon.add_directory({'mode' : 'findsolarmovies', 'url' : 'http://www.solarmovie.eu/watch-reality-tv-movies.html'}, 'Reality TV')
    addon.add_directory({'mode' : 'findsolarmovies', 'url' : 'http://www.solarmovie.eu/watch-romance-movies.html'}, 'Romance')
    addon.add_directory({'mode' : 'findsolarmovies', 'url' : 'http://www.solarmovie.eu/watch-sci-fi-movies.html'}, 'Sci-Fi')
    addon.add_directory({'mode' : 'findsolarmovies', 'url' : 'http://www.solarmovie.eu/watch-short-movies.html'}, 'Short')
    addon.add_directory({'mode' : 'findsolarmovies', 'url' : 'http://www.solarmovie.eu/watch-sport-movies.html'}, 'Sport')
    addon.add_directory({'mode' : 'findsolarmovies', 'url' : 'http://www.solarmovie.eu/watch-talk-show-movies.html'}, 'Talk Show')
    addon.add_directory({'mode' : 'findsolarmovies', 'url' : 'http://www.solarmovie.eu/watch-thriller-movies.html'}, 'Thriller')
    addon.add_directory({'mode' : 'findsolarmovies', 'url' : 'http://www.solarmovie.eu/watch-war-movies.html'}, 'War')
    addon.add_directory({'mode' : 'findsolarmovies', 'url' : 'http://www.solarmovie.eu/watch-western-movies.html'}, 'Western')



    
if not play:
    addon.end_of_directory()



