import xbmcplugin, xbmcgui
import time
from lib import routing
from lib import  vader
from lib import utils
from lib import pytz
from xbmcplugin import addDirectoryItem, endOfDirectory
from xbmcgui import ListItem
import xbmc
from unidecode import unidecode
from datetime import datetime
from datetime import timedelta
import traceback
import plugintools
import json
import calendar
import base64
import requests
import re
import urllib
import urlresolver
import urlparse
import xbmcaddon
import os


firstrun = plugintools.get_setting('first')

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

plugin = routing.Plugin()

jsonGetTVEpisodes = '''{
        "jsonrpc": "2.0",
        "method": "VideoLibrary.GetEpisodes",
        "params": {

"filter": {"and": [{"operator": "contains", "field": "title", "value": "%s"}, {"operator": "contains", "field": "path", "value": "%s"}]},
         "properties": ["tvshowid", "plot", "showtitle", "title", "rating", "thumbnail", "playcount"]
        },
        "id": "mybash"
}'''

@plugin.route('/')
def index():
    try:
        authString = vaderClass.get_auth_status()
        if authString == 'Active':
            if vaderClass.show_categories:
                addDirectoryItem(plugin.handle, plugin.url_for(show_livetv_cat, 'all'), ListItem("Live TV"), True)
            else:
                addDirectoryItem(plugin.handle, plugin.url_for(show_livetv_all), ListItem("Live TV"), True)

            if vaderClass.enable_pvr == True:
                addDirectoryItem(plugin.handle, plugin.url_for(tvguide), ListItem("Kodi Guide"), False)
            addDirectoryItem(plugin.handle, plugin.url_for(vaderguide), ListItem("Addon Guide ~Beta~"), False)

            addDirectoryItem(plugin.handle, plugin.url_for(show_livetv_cat, '26'), ListItem("Live Sports #s"), True)
            addDirectoryItem(plugin.handle, plugin.url_for(show_mc), ListItem(vaderClass.MatchCenterName), True)
            if vaderClass.vodCapable == True:
                addDirectoryItem(plugin.handle, plugin.url_for(show_vod,'all'), ListItem("Video On Demand"), True)
            addDirectoryItem(plugin.handle, plugin.url_for(show_catchup_menu,'all'), ListItem(vaderClass.TVCatchupName), True)

            addDirectoryItem(plugin.handle, plugin.url_for(index), ListItem(""), False)
            if vaderClass.embedded == False:
                addDirectoryItem(plugin.handle, plugin.url_for(accountInfo), ListItem("My Account"), True)
            addDirectoryItem(plugin.handle, plugin.url_for(settings), ListItem("Settings"), True)
            addDirectoryItem(plugin.handle, plugin.url_for(show_tools), ListItem("Tools"), False)
        else:
            addDirectoryItem(plugin.handle, plugin.url_for(settings), ListItem("Unable to Login - {auth}".format(auth=authString)), True)
            addDirectoryItem(plugin.handle, plugin.url_for(show_tools),
                             ListItem("- Please send your log file for analysis if you think this was an error"), False)

            addDirectoryItem(plugin.handle, plugin.url_for(settings), ListItem('Click here to configure'), True)

        endOfDirectory(plugin.handle)

    except Exception as e:
        addDirectoryItem(plugin.handle, plugin.url_for(show_tools), ListItem("Tools - Please send your log file for analysis"), False)
        endOfDirectory(plugin.handle)
        utils.log("Error getting index \n{0}\n{1}".format(e, traceback.format_exc()))
        pass


@plugin.route('/serverSetup')
def serverSetup():
    vaderClass.serverSetup()

@plugin.route('/categorySetup')
def categorySetup():
    vaderClass.categorySetup()

@plugin.route('/tools')
def show_tools():
    vaderClass.show_tools()

@plugin.route('/play/movie/<category_id>/<name>')
def play_movie(category_id, name):
    streams = vaderClass.get_category_id_vod(category_id, sort=True)
    utils.log('Trying to play ' + name)

    for stream in streams:
        if stream['name'].lower() == name.lower():
            chanName = stream['name']
            stream_id = stream['stream_id']
            icon = stream['stream_icon']
            container_extension = stream['container_extension']

            chanUrl = vaderClass.build_stream_url(stream_id, extension=container_extension, base='movie')


            info = {}

            info['title'] = name

            listitem = xbmcgui.ListItem(path=chanUrl, iconImage=icon)

            listitem.setInfo("video", info)
            listitem.setPath(chanUrl)

            win = xbmcgui.Window(10000)
            win.setProperty('vader.playing', 'True')
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)
            break

    return True

@plugin.route('/play/tv/<category_id>/<name>/<season>/<episode>')
def play_tv(category_id, name, season, episode):

    streams = vaderClass.get_category_id_vod(category_id, sort=True)

    for stream in streams:
        if stream['name'].lower().replace(' ', '') == name.lower().replace(' ', ''):
            chanName = stream['name']
            stream_id = stream['stream_id']
            icon = stream['stream_icon']
            container_extension = stream['container_extension']

            chanUrl = vaderClass.build_stream_url(stream_id, extension=container_extension, base='movie')
            tv = re.findall('(.*) - S(\d{1,2}) ?E(\d{1,2}) - (.*)', name)
            if len(tv) > 0:
                utils.log('using regex')
                showName = tv[0][0].strip()
                season = str(int(tv[0][1]))
                episode = str(int(tv[0][2]))
                title = str(tv[0][3])

            else:
                utils.log('unkown info')
                return


            jsonval = xbmc.executeJSONRPC(jsonGetTVEpisodes % (title,showName ))
            jsonval = json.loads(jsonval)

            info = {}
            info['mediatype'] = 'episode'
            info['season'] = season
            info['episode'] = episode
            info['tvshowtitle'] = showName
            info['title'] = title
            info['plot'] = jsonval['result']['episodes'][0]['plot']

            listitem=xbmcgui.ListItem(path=chanUrl,iconImage=icon)

            listitem.setInfo( "video", info )
            listitem.setPath(chanUrl)


            win = xbmcgui.Window(10000)
            win.setProperty('vader.playing', 'True')
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)
            break

    return True


@plugin.route('/vod/recent/<type>')
def show_vod_recent(type):


    streams = vaderClass.get_recent_vod(type)

    for stream in streams:
        chanName = stream['name']
        stream_id = stream['stream_id']
        icon = stream['stream_icon']
        container_extension = stream['container_extension']

        chanUrl = vaderClass.build_stream_url(stream_id, extension=container_extension, base='movie')


        title = chanName

        title = str(title.encode('utf-8').decode('ascii', 'ignore'))

        plugintools.add_playable(title=title, url=chanUrl,
                                 thumbnail=icon, plot='', isPlayable=True, folder=False)



    endOfDirectory(plugin.handle)


@plugin.route('/vod/movies/<year>')
def show_movies_year(year):
    try:
        if year == 'all':
            validYears = []
            validYears = vaderClass.get_vod_years()

            for year in validYears:
                addDirectoryItem(plugin.handle, plugin.url_for(show_movies_year, year=str(year)), ListItem(
                    str(year)), True)


        else:
            streams = vaderClass.get_vod_search(year, '53')
            for stream in streams:
                name = stream['name']
                stream_id = stream['stream_id']
                icon = stream['stream_icon']
                extension = stream['container_extension']

                chanUrl = vaderClass.build_stream_url(stream_id, extension=extension, base='movie')

                title = name

                title = str(title.encode('utf-8').decode('ascii', 'ignore'))

                plugintools.add_playable(title=title, url=chanUrl,
                                         thumbnail=icon, plot='', isPlayable=True, folder=False)

        endOfDirectory(plugin.handle)

    except Exception as e:
        utils.log("Error listing streams \n{0}\n{1}".format(e, traceback.format_exc()))
        pass


@plugin.route('/vod/titlesearch/<search>/')
def show_vod_titlesearch(search):
    try:
        vod_categories = vaderClass.get_vod_categories(sort=True)
        for category in vod_categories:
            parent_id = category['parent_id']
            name = category['category_name']
            cat_id = category['category_id']
            if search in name:
                addDirectoryItem(plugin.handle, plugin.url_for(show_vod, category_id=str(cat_id)), ListItem(name),
                                 True)



        endOfDirectory(plugin.handle)

    except Exception as e:
        utils.log("Error listing streams \n{0}\n{1}".format(e, traceback.format_exc()))
        pass


@plugin.route('/web_vod/parsed_shows/<type>/<channel>/')
def show_parsed_vod_shows(type, channel):
    utils.log('getting shows for ' + channel)
    data = vaderClass.getWebVodShowNames(type, channel)
    for show in data:
        addDirectoryItem(plugin.handle, plugin.url_for(show_parsed_vod_episodes, type=type, channel=channel, show=show), ListItem(
            show), True)


    endOfDirectory(plugin.handle)

@plugin.route('/playExternalLink/<link>')
def playExternalLink(link):

    try:
        link = urllib.unquote_plus(link)
        link = link.replace('https://www.youtube.com/embed/', 'http://youtube.com/watch?v=')
        utils.log(link)


        stream_url = urlresolver.resolve(link)

        if stream_url:
            utils.log('found stream url : ' + stream_url)
            xbmc.Player().play(item=stream_url, listitem=xbmcgui.ListItem(path=stream_url))
        else:
            utils.log('stream not found')

    except Exception as e:
        utils.log("Error listing streams \n{0}\n{1}".format(e, traceback.format_exc()))
        pass


    return True



@plugin.route('/web_vod/parsed_episodes/list_links_for_source/<type>/<channel>/<show>/<episode>/<source>/')
def show_links_for_vod_source(type, channel, show, episode, source):
    data = vaderClass.getParsedData(type)
    episode_links = data[channel][show][episode][source]
    for link in episode_links:
        netloc = urlparse.urlparse(link)[1]
        addDirectoryItem(plugin.handle, plugin.url_for(playExternalLink, link=urllib.quote_plus(link)), ListItem(
            'source: '+netloc), False)

    endOfDirectory(plugin.handle)


@plugin.route('/web_vod/parsed_episodes/<type>/<channel>/<show>/<episode>/')
def show_parsed_vod_episode_links(type, channel, show, episode):
    try:
        links = []
        episode_links = vaderClass.getWebVodMediaLinks(type, channel, show, episode)



        for item in episode_links:
            media_list = item['media_url']

            source_url = item['source_url']
            source_name = item['source_name']
            numLinks = len(media_list)
            itemNum = 1
            for media_url in media_list:
                appendString = str(itemNum) + '/' + str(numLinks)
                netloc = urlparse.urlparse(media_url)[1]

                if 'tvlogy.to' not in netloc:

                    addDirectoryItem(plugin.handle, plugin.url_for(playExternalLink, link=urllib.quote_plus(media_url)), ListItem(
                        source_name + ' : ' + netloc + ' : ' + appendString), True)

                itemNum = itemNum + 1

    except Exception as e:
        utils.log("Error listing streams \n{0}\n{1}".format(e, traceback.format_exc()))
        pass

    endOfDirectory(plugin.handle)


@plugin.route('/web_vod/parsed_episodes/<type>/<channel>/<show>/')
def show_parsed_vod_episodes(type, channel, show):
    try:
        data = vaderClass.getWebVodEpisodes(type, channel, show)

        for episode in data:
            addDirectoryItem(plugin.handle, plugin.url_for(show_parsed_vod_episode_links, type=type, channel=channel, show=show, episode=episode), ListItem(
                episode), True)

    except Exception as e:
        utils.log("Error listing streams \n{0}\n{1}".format(e, traceback.format_exc()))
        pass

    endOfDirectory(plugin.handle)


@plugin.route('/web_vod/parsed_chans/<type>/')
def show_parsed_vod_chans(type):

    try:
        data = vaderClass.getWebVodChanNames(type)
        for channel in data:
            addDirectoryItem(plugin.handle, plugin.url_for(show_parsed_vod_shows, type=type, channel=channel), ListItem(
                channel), True)

    except Exception as e:
        utils.log("Error listing streams \n{0}\n{1}".format(e, traceback.format_exc()))
        pass

    endOfDirectory(plugin.handle)


@plugin.route('/web_vod/')
def show_web_vod_menu():

    try:
        addDirectoryItem(plugin.handle, plugin.url_for(show_parsed_vod_chans, type='PakistanParsedData2'), ListItem(
            'Pakistan TV Shows'), True)

        addDirectoryItem(plugin.handle, plugin.url_for(show_parsed_vod_chans, type='IndianParsedData'), ListItem(
            'Indian TV Shows'), True)



    except Exception as e:
        utils.log("Error listing streams \n{0}\n{1}".format(e, traceback.format_exc()))
        pass


    endOfDirectory(plugin.handle)



@plugin.route('/vod/category/<category_id>/')
def show_vod(category_id):
    try:

        if category_id == 'all':
            categories = vaderClass.get_vod_categories()
            for category in categories:
                parent_id = str(category['parent_id'])
                name = str(category['category_name'])
                cat_id = category['category_id']
                if parent_id == '0':

                        addDirectoryItem(plugin.handle, plugin.url_for(show_vod, category_id=str(cat_id)), ListItem(name), True)

            addDirectoryItem(plugin.handle, plugin.url_for(show_movies_year, year='all'), ListItem(
                'Movies - By Year'), True)

            addDirectoryItem(plugin.handle, plugin.url_for(show_vod_recent, type='movies'), ListItem(
                'Recently Added - Movies'), True)
            addDirectoryItem(plugin.handle, plugin.url_for(show_vod_recent, type='tvshows'), ListItem(
                'Recently Added - TV Shows'), True)

            addDirectoryItem(plugin.handle, plugin.url_for(show_web_vod_menu), ListItem(
                'Web Based VOD ~Beta~'), True)


            addDirectoryItem(plugin.handle, plugin.url_for(show_vod_recent, type='tvshows'), ListItem(
                'Note: Surround Sound is included as the 2nd Audio Track, You can change Kodi default settings to auto select the best audio track instead of first'), True)

        else:
                vod_categories = vaderClass.get_vod_categories(sort=True)
                uniqueShows = []

                for category in vod_categories:
                    parent_id = category['parent_id']
                    name = category['category_name']
                    cat_id = category['category_id']

                    if parent_id == category_id:
                        if parent_id == '55':
                            showName = re.split('S\d+', name)[0].strip()
                            if showName not in uniqueShows:
                                uniqueShows.append(showName)
                                search = showName + ' S'
                                addDirectoryItem(plugin.handle, plugin.url_for(show_vod_titlesearch, search=search),
                                                 ListItem(showName),
                                                 True)
                        else:

                            addDirectoryItem(plugin.handle, plugin.url_for(show_vod, category_id=str(cat_id)), ListItem(name),
                                         True)


                streams = vaderClass.get_category_id_vod(category_id, sort=True)
                for stream in streams:
                    chanName = stream['name']
                    stream_id = stream['stream_id']
                    icon = stream['stream_icon']
                    extension = stream['container_extension']

                    chanUrl = vaderClass.build_stream_url(stream_id, extension=extension, base='movie')


                    title = chanName

                    title = str(title.encode('utf-8').decode('ascii', 'ignore'))
                    if icon == None:
                        icon = ''

                    plugintools.add_playable(title=title, url=chanUrl,
                                             thumbnail=icon, plot='', isPlayable=True, folder=False)



        endOfDirectory(plugin.handle)

    except Exception as e:
        utils.log("Error listing streams \n{0}\n{1}".format(e, traceback.format_exc()))
        pass



@plugin.route('/catchup/mc')
def show_catchup_mc():
    mcArchiveEvents = requests.get('http://vaders.tv/getMatchCenterArchive').json()

    backwardTime = datetime.utcnow() - timedelta(days=int(vaderClass.catchup_length))
    backwardTimeTs = calendar.timegm(backwardTime.timetuple())
    backwardTimeTs = int(backwardTimeTs)
    timeNow = time.time()
    timeNow = int(timeNow)
    for epgitem in mcArchiveEvents:
        title = epgitem['title']
        stream_id = epgitem['stream_id']
        startTime = int(epgitem['startTime'])
        playTime = epgitem['playTime']

        stopTime = int(epgitem['stopTime'])
        duration = int((stopTime - startTime)/60) + 5

        if (startTime > backwardTimeTs and startTime < timeNow):
            displayTime = datetime.fromtimestamp(int(startTime)).strftime('%d.%m - %H:%M')
            utc = pytz.utc
            # playTime = datetime.fromtimestamp(int(startTime), tz=utc).strftime('%Y-%m-%d:%H-%M')
            finalTitle = displayTime + " - " + title
            addDirectoryItem(plugin.handle, plugin.url_for(play_archive_adjusted, stream_id, playTime, title, str(duration)),
                             ListItem(finalTitle), False)

    endOfDirectory(plugin.handle)



@plugin.route('/catchup/category/<category_id>')
def show_catchup_tv_cat(category_id):

    try:

        if category_id == 'all':
            categories = vaderClass.get_categories()
            for category in categories:
                for cat_id in category:
                    if int(cat_id) not in vaderClass.filter_category_list_id:

                        addDirectoryItem(plugin.handle, plugin.url_for(show_catchup_tv_cat, category_id=str(cat_id)), ListItem(category[cat_id]), True)

        else:
            try:
                streams = vaderClass.get_category_id_live(category_id)
                for streamObj in streams:
                    chanName = streamObj['name']
                    stream_id = streamObj['stream_id']
                    icon = streamObj['stream_icon']
                    tv_archive = streamObj['tv_archive']

                    category_id = int(streamObj['category_id'])
                    if category_id not in vaderClass.filter_category_list_id and tv_archive == 1:
                        title = chanName

                        title = str(title.encode('utf-8').decode('ascii', 'ignore'))
                        addDirectoryItem(plugin.handle, plugin.url_for(show_catchup_listing, stream_id),
                                         ListItem(title), True)

            except Exception as e:
                plugintools.log("Error listing streams \n{0}\n{1}".format(e,traceback.format_exc()))
                pass

        endOfDirectory(plugin.handle)

    except Exception as e:
        utils.log("Error listing streams \n{0}\n{1}".format(e, traceback.format_exc()))
        pass

@plugin.route('/livetv/category/<category_id>')
def show_livetv_cat(category_id):

    try:

        if category_id == 'all':
            categories = vaderClass.get_categories()
            for category in categories:
                for cat_id in category:
                    if int(cat_id) not in vaderClass.filter_category_list_id:

                        addDirectoryItem(plugin.handle, plugin.url_for(show_livetv_cat, category_id=str(cat_id)), ListItem(category[cat_id]), True)
            endOfDirectory(plugin.handle)
        else:
            try:
                streams = vaderClass.get_category_id_live(category_id)
                for streamObj in streams:
                    chanName = streamObj['name'].replace('SA:','')
                    stream = streamObj['stream_id']
                    icon = unidecode(streamObj['stream_icon'])
                    chanUrl =  vaderClass.build_stream_url(stream)

                    if vaderClass.get_epg_chan(chanName):
                        title = '[COLOR blue]' +  unidecode(chanName) + '[/COLOR] - ' + '[I][COLOR cyan]' + unidecode(vaderClass.get_epg_chan(chanName)) +'[/COLOR][/I]'
                    else:
                        title = chanName

                    title = str(title.encode('utf-8').decode('ascii', 'ignore'))
                    utils.log(title)

                    plugintools.add_playable(title=title, url=chanUrl,
                                             thumbnail=icon, plot='',  isPlayable=True, folder=False)

                endOfDirectory(plugin.handle)
            except Exception as e:
                utils.log("Error listing streams \n{0}\n{1}".format(e,traceback.format_exc()))
                pass

    except Exception as e:
        utils.log("Error listing streams \n{0}\n{1}".format(e, traceback.format_exc()))
        pass


@plugin.route('/livetv/all/')
def show_livetv_all():
    streams = vaderClass.get_all_streams()
    for streamObj in streams:
        chanName = streamObj['name']
        stream = streamObj['stream_id']
        icon = streamObj['stream_icon']
        category_id = streamObj['category_id']
        chanUrl = vaderClass.build_stream_url(stream)
        if category_id not in vaderClass.filter_category_list_id:
            if vaderClass.get_epg_chan(chanName):
                title = '[COLOR blue]' +  chanName + '[/COLOR] - ' + '[I][COLOR cyan]' + vaderClass.get_epg_chan(chanName) +'[/COLOR][/I]'
            else:
                title = chanName

            title = str(title.encode('utf-8').decode('ascii', 'ignore'))
            plugintools.add_playable(title=title, url=chanUrl,
                                     thumbnail=icon, plot='', isPlayable=True, folder=False)

    endOfDirectory(plugin.handle)



@plugin.route('/play/<stream_id>')
def play_live(stream_id):
    info = {}
    chanUrl = vaderClass.build_stream_url(stream_id)
    listitem = xbmcgui.ListItem(path=chanUrl)
    listitem.setInfo("video", info)
    listitem.setPath(chanUrl)
    win = xbmcgui.Window(10000)
    win.setProperty('vader.playing', 'True')
    xbmc.Player().play(item=chanUrl, listitem=listitem)


@plugin.route('/play_archive/<stream_id>/<playTime>/<title>/<duration>')
def play_archive(stream_id, playTime, title, duration):
    duration = str(int(duration) + 5)
    try:
        timestamp = int(time.mktime(datetime.strptime(playTime, "%Y-%m-%d:%H-%M").timetuple()))
    except TypeError:
        timestamp = int((time.mktime(time.strptime(playTime, "%Y-%m-%d:%H-%M"))))

    #serverTzString = vaderClass.user_info['server_timezone']
    serverTzString = 'Africa/Bangui'
    tzObj = pytz.timezone(serverTzString)
    newPlayTime = datetime.fromtimestamp(int(timestamp), tz=tzObj).strftime('%Y-%m-%d:%H-%M')
    play_archive_adjusted(stream_id, newPlayTime, title, duration)

@plugin.route('/play_archive_adjusted/<stream_id>/<playTime>/<title>/<duration>')
def play_archive_adjusted(stream_id, playTime, title, duration):
    url = vaderClass.get_playlink_archive(stream_id, playTime, duration=duration)
    info = {}

    info['title'] = title
    listitem = xbmcgui.ListItem(path=url)
    listitem.setInfo("video", info)
    listitem.setPath(url)
    win = xbmcgui.Window(10000)
    win.setProperty('vader.playing', 'True')
    utils.log(url)

    xbmc.Player().play(item=url, listitem=listitem)


@plugin.route('/catchup_search/<stream_id>/<search>')
def catchup_search(stream_id, search):

    try:
        jsondata = vaderClass.get_epg_for_stream(stream_id)['epg_listings']

        backwardTime = datetime.utcnow() - timedelta(days=int(vaderClass.catchup_length))

        backwardTimeTs = calendar.timegm(backwardTime.timetuple())
        backwardTimeTs = int(backwardTimeTs)
        timeNow = time.time()
        timeNow = int(timeNow)
        showNames = []


        for epgitem in jsondata:
            title = epgitem['title']

            title = base64.b64decode(title)
            startTime = int(epgitem['start_timestamp'])
            stopTime = int(epgitem['stop_timestamp'])
            duration = int((stopTime - startTime) / 60) + 5
            if (startTime > backwardTimeTs and startTime < timeNow):

                if search in title:
                    displayTime = datetime.fromtimestamp(int(startTime)).strftime('%d.%m - %H:%M')
                    utc = pytz.utc
                    playTime = datetime.fromtimestamp(int(startTime), tz=utc).strftime('%Y-%m-%d:%H-%M')
                    finalTitle = displayTime + " - " + title

                    addDirectoryItem(plugin.handle,
                                     plugin.url_for(play_archive_adjusted, stream_id, playTime, title, str(duration)),
                                     ListItem(finalTitle), False)



    except Exception as e:
        utils.log("Error listing streams \n{0}\n{1}".format(e, traceback.format_exc()))
        pass

    endOfDirectory(plugin.handle)



@plugin.route('/catchup_listing/<stream_id>')
def show_catchup_listing(stream_id):

    jsondata = vaderClass.get_epg_for_stream(stream_id)['epg_listings']
    backwardTime = datetime.utcnow() - timedelta(days=int(vaderClass.catchup_length))
    backwardTimeTs      = calendar.timegm(backwardTime.timetuple())
    backwardTimeTs = int(backwardTimeTs)
    timeNow = time.time()
    timeNow     = int(timeNow)
    showNames = []

    for epgitem in jsondata:
        title = epgitem ['title']
        title = base64.b64decode(title).replace('/','-')
        startTime = int(epgitem['start_timestamp'])
        stopTime = int(epgitem['stop_timestamp'])
        duration = int((stopTime-startTime)/60) + 5

        if(startTime > backwardTimeTs and startTime < timeNow):
            if vaderClass.group_by_name == True:
                if title not in showNames:
                    showNames.append(title)
                    displayTime = datetime.fromtimestamp(int(startTime)).strftime('%d.%m - %H:%M')
                    utc = pytz.utc
                    if '[New!]' in title:
                        finalTitle = displayTime + " - " + title
                    else:
                        finalTitle = title
                    addDirectoryItem(plugin.handle,
                                     plugin.url_for(catchup_search, stream_id, title),
                                     ListItem(finalTitle), True)
            else:

                displayTime = datetime.fromtimestamp(int(startTime)).strftime('%d.%m - %H:%M')
                utc = pytz.utc
                playTime = datetime.fromtimestamp(int(startTime), tz=utc).strftime('%Y-%m-%d:%H-%M')
                finalTitle = displayTime + " - "    +       title
                addDirectoryItem(plugin.handle, plugin.url_for(play_archive_adjusted, stream_id, playTime, title, str(duration)), ListItem(finalTitle), False)


    endOfDirectory(plugin.handle)


@plugin.route('/catchup/<type>')
def show_catchup_menu(type):

    if type == 'all':
        addDirectoryItem(plugin.handle, plugin.url_for(show_catchup_menu, 'tv'), ListItem(vaderClass.TVCatchupName), True)
        addDirectoryItem(plugin.handle, plugin.url_for(show_catchup_menu, 'mc'), ListItem(vaderClass.MCCatchupName), True)

    if type == 'tv':
        show_catchup_tv_cat('all')

    if type == 'mc':
        show_catchup_mc()

    endOfDirectory(plugin.handle)


@plugin.route('/mc/')
def show_mc():
    closedTime = plugintools.get_setting('mcClosedTime')
    if closedTime == None or closedTime == '':
        plugintools.set_setting('mcClosedTime', '0')
    closedTime = int((plugintools.get_setting('mcClosedTime')))
    timeDiff = time.time() - closedTime
    mc_quittimer = plugintools.get_setting('mc_quittimer')
    if time.time() - closedTime > int(mc_quittimer):
        endOfDirectory(plugin.handle)
        vaderClass.startMCC()
    else:

        endOfDirectory(plugin.handle)
        xbmc.executebuiltin('Action(Back)')




@plugin.route('/accountInfo')
def accountInfo():
    username = plugintools.get_setting('username')
    password = plugintools.get_setting('password')
    apiEndpoint = 'vaders.tv'
    url = 'http://{apiEndpoint}/player_api.php?username={username}&password={password}'.format(username=username, password=password, apiEndpoint=apiEndpoint)
    data = requests.get(url, timeout=300).json()

    exp_date = str(data["user_info"]['exp_date'])
    if exp_date:
        exp_date_str =  datetime.fromtimestamp(int(exp_date)).strftime('%d-%m-%Y')
    else:
        exp_date_str = "Never"

    trial_str = str(data["user_info"]["is_trial"])
    if trial_str != True:
        trial_str = "No"
    else:
        trial_str = "Yes"

    status = str(data["user_info"]["status"])
    max_connections = str(data["user_info"]["max_connections"])
    active_cons = str(data["user_info"]["active_cons"])
    username = str(data["user_info"]["username"])

    addDirectoryItem(plugin.handle, plugin.url_for(accountInfo), ListItem("[COLOR blue] User: [/COLOR]" + username), False)
    addDirectoryItem(plugin.handle, plugin.url_for(accountInfo), ListItem("[COLOR blue] Status: [/COLOR]" + status), False)
    addDirectoryItem(plugin.handle, plugin.url_for(accountInfo), ListItem("[COLOR blue] Expires: [/COLOR]" + exp_date_str), False)
    addDirectoryItem(plugin.handle, plugin.url_for(accountInfo), ListItem("[COLOR blue] Trial Account: [/COLOR]" + trial_str), False)
    addDirectoryItem(plugin.handle, plugin.url_for(accountInfo), ListItem("[COLOR blue] Max Connections: [/COLOR]" + max_connections), False)
    addDirectoryItem(plugin.handle, plugin.url_for(accountInfo), ListItem("[COLOR blue] Active Connections: [/COLOR]" + active_cons), False)


    endOfDirectory(plugin.handle)


@plugin.route('/vaderguide')
def vaderguide():
    enable_pvr = plugintools.get_setting('enable_pvr')
    # if enable_pvr:
    #     xbmc.executebuiltin("XBMC.ActivateWindow(tvguide)")
    # else:
    xbmc.executebuiltin('XBMC.RunAddon(script.tvguide.Vader)')


    endOfDirectory(plugin.handle)

@plugin.route('/tvguide')
def tvguide():
    enable_pvr = plugintools.get_setting('enable_pvr')
    # if enable_pvr:
    xbmc.executebuiltin("XBMC.ActivateWindow(tvguide)")
    # else:
    # xbmc.executebuiltin('XBMC.RunAddon(script.tvguide.Vader)')


    endOfDirectory(plugin.handle)


@plugin.route('/settings')
def settings():
    plugintools.open_settings_dialog()

if __name__ == '__main__':

    try:
        __addon__ = xbmcaddon.Addon()
        ADDONDATA = xbmc.translatePath(__addon__.getAddonInfo('profile'))
        start = datetime.now()
        vaderClass = vader.vader()
        plugin.run()
        utils.log('Vader function ran in {0}ms'.format(str(datetime.now() - start)))
        del vaderClass
        del plugin
        del __addon__
        del ADDONDATA
    except Exception as e:
        utils.log('something horrible happened')
        utils.log("Error getting index \n{0}\n{1}".format(e, traceback.format_exc()))

    #
    #     lockFile = os.path.join(ADDONDATA, 'file.lock')
    #
    #     if not os.path.exists(lockFile):
    #         with open(lockFile, 'w') as lockFileFd:
    #             start = datetime.now()
    #             vaderClass = vader.vader()
    #             plugin.run()
    #             utils.log('Vader function ran in {0}ms'.format(str(datetime.now() - start)))
    #             del vaderClass
    #             del plugin
    #         os.remove(lockFile)
    # except Exception as e:
    #     utils.log('something horrible happened')
    #     utils.log("Error getting index \n{0}\n{1}".format(e, traceback.format_exc()))
