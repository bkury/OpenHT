# -*- coding: utf-8 -*-

#################################################################################################

import logging

#################################################################################################

LOG = logging.getLogger('Emby.'+__name__)

#################################################################################################

def emby_url(client, handler):
    return  "%s/emby/%s" % (client['config/auth.server'], handler)

def basic_info():
    return  "Etag,PresentationUniqueKey"

def info():
    return  (
                "Path,Genres,SortName,Studios,Writer,Taglines,LocalTrailerCount,Video3DFormat,"
                "OfficialRating,CumulativeRunTimeTicks,ItemCounts,PremiereDate,ProductionYear,"
                "Metascore,AirTime,DateCreated,People,Overview,CommunityRating,StartDate,"
                "CriticRating,CriticRatingSummary,Etag,ShortOverview,ProductionLocations,"
                "Tags,ProviderIds,ParentId,RemoteTrailers,SpecialEpisodeNumbers,Status,EndDate,"
                "MediaSources,VoteCount,RecursiveItemCount,PrimaryImageAspectRatio,DisplayOrder,"
                "PresentationUniqueKey,OriginalTitle"
            )

def music_info():
    return  (
                "Etag,Genres,SortName,Studios,Writer,PremiereDate,ProductionYear,"
                "OfficialRating,CumulativeRunTimeTicks,Metascore,CommunityRating,"
                "AirTime,DateCreated,MediaStreams,People,ProviderIds,Overview,ItemCounts,"
                "PresentationUniqueKey"
            )

#################################################################################################

class API(object):

    ''' All the api calls to the server.
    '''
    def __init__(self, client, *args, **kwargs):
        self.client = client

    def _http(self, action, url, request={}):
        request.update({'type': action, 'handler': url})

        return  self.client.request(request)

    def _get(self, handler, params=None):
        return  self._http("GET", handler, {'params': params})

    def _post(self, handler, json=None, params=None):
        return  self._http("POST", handler, {'params': params, 'json': json})

    def _delete(self, handler, params=None):
        return  self._http("DELETE", handler, {'params': params})

    #################################################################################################

    # Bigger section of the Emby api

    #################################################################################################

    def try_server(self):
        return  self._get("System/Info/Public")

    def sessions(self, handler="", action="GET", params=None, json=None):

        if action == "POST":
            return  self._post("Sessions%s" % handler, json, params)
        elif action == "DELETE":
            return  self._delete("Sessions%s" % handler, params)
        else:
            return  self._get("Sessions%s" % handler, params)

    def users(self, handler="", action="GET", params=None, json=None):

        if action == "POST":
            return  self._post("Users/{UserId}%s" % handler, json, params)
        elif action == "DELETE":
            return  self._delete("Users/{UserId}%s" % handler, params)
        else:
            return  self._get("Users/{UserId}%s" % handler, params)

    def items(self, handler="", action="GET", params=None, json=None):
        
        if action == "POST":
            return  self._post("Items%s" % handler, json, params)
        elif action == "DELETE":
            return  self._delete("Items%s" % handler, params)
        else:
            return  self._get("Items%s" % handler, params)

    def user_items(self, handler="", params=None):
        return  self.users("/Items%s" % handler, params=params)

    def shows(self, handler, params):
        return  self._get("Shows%s" % handler, params)

    def videos(self, handler):
        return  self._get("Videos%s" % handler)

    def artwork(self, item_id, art, max_width, ext="jpg", index=None):

        if index is None:
            return  emby_url(self.client, "Items/%s/Images/%s?MaxWidth=%s&format=%s" % (item_id, art, max_width, ext))

        return emby_url(self.client, "Items/%s/Images/%s/%s?MaxWidth=%s&format=%s" % (item_id, art, index, max_width, ext))

    #################################################################################################

    # More granular api

    #################################################################################################

    def get_users(self, disabled=False, hidden=None):
        return  self._get("Users", params={
                    'IsDisabled': disabled,
                    'IsHidden': hidden
                })

    def get_public_users(self):
        return  self._get("Users/Public")

    def get_user(self, user_id=None):
        return  self.users() if user_id is None else self._get("Users/%s" % user_id)

    def get_views(self):
        return  self.users("/Views")

    def get_media_folders(self):
        return  self.users("/Items")

    def get_item(self, item_id):
        return  self.users("/Items/%s" % item_id)

    def get_items(self, item_ids):
        return  self.users("/Items", params={
                    'Ids': ','.join(str(x) for x in item_ids),
                    'Fields': info()
                })

    def get_sessions(self):
        return  self.sessions(params={'ControllableByUserId': "{UserId}"})

    def get_device(self, device_id):
        return  self.sessions(params={'DeviceId': device_id})

    def post_session(self, session_id, url, params=None, data=None):
        return  self.sessions("/%s/%s" % (session_id, url), "POST", params, data)

    def get_images(self, item_id):
        return  self.items("/%s/Images" % item_id)

    def get_suggestion(self, media="Movie,Episode", limit=1):
        return  self.users("/Suggestions", {
                    'Type': media,
                    'Limit': limit
                })

    def search(self, term, media=None):
        return  self._get("Search/Hints", {
                    'UserId': "{UserId}",
                    'SearchTerm': term.encode('utf-8'),
                    'IncludeItemTypes': media
                })

    def get_recently_added(self, media=None, parent_id=None, limit=20):
        return  self.user_items("/Latest", {
                    'Limit': limit,
                    'UserId': "{UserId}",
                    'IncludeItemTypes': media,
                    'ParentId': parent_id,
                    'Fields': info()
                })

    def get_next(self, index=None, limit=1):
        return  self.shows("/NextUp", {
                    'Limit': limit,
                    'UserId': "{UserId}",
                    'StartIndex': None if index is None else int(index)
                })

    def get_adjacent_episodes(self, show_id, item_id):
        return  self.shows("/%s/Episodes" % show_id, {
                    'UserId': "{UserId}",
                    'AdjacentTo': item_id,
                    'Fields': info()
                })

    def get_genres(self, parent_id=None):
        return  self._get("Genres", {
                    'ParentId': parent_id,
                    'UserId': "{UserId}",
                    'Fields': info()
                })

    def get_recommendation(self, parent_id=None, limit=20):
        return  self._get("Movies/Recommendations", {
                    'ParentId': parent_id,
                    'UserId': "{UserId}",
                    'Fields': info(),
                    'Limit': limit
                })

    def get_items_by_letter(self, parent_id=None, media=None, letter=None):
        return  self.user_items(params={
                    'ParentId': parent_id,
                    'NameStartsWith': letter,
                    'Fields': info(),
                    'Recursive': True,
                    'IncludeItemTypes': media
                })

    def get_channels(self):
        return  self._get("LiveTv/Channels", {
                    'UserId': "{UserId}",
                    'EnableImages': True,
                    'EnableUserData': True
                })

    def get_intros(self, item_id):
        return  self.user_items("/%s/Intros" % item_id)

    def get_additional_parts(self, item_id):
        return  self.videos("/%s/AdditionalParts" % item_id)

    def delete_item(self, item_id):
        return  self.items("/%s" % item_id, "DELETE")

    def get_local_trailers(self, item_id):
        return  self.user_items("/%s/LocalTrailers" % item_id)

    def get_ancestors(self, item_id):
        return  self.items("/%s/Ancestors" % item_id, params={
                    'UserId': "{UserId}"
                })

    def get_items_theme_video(self, parent_id):
        return  self.users("/Items", params={
                    'HasThemeVideo': True,
                    'ParentId': parent_id,
                    'Recursive': True
                })

    def get_themes(self, item_id):
        return  self.items("/%s/ThemeMedia" % item_id, params={
                    'UserId': "{UserId}",
                    'InheritFromParent': True,
                    'EnableThemeSongs': True,
                    'EnableThemeVideos': True
                })

    def get_items_theme_song(self, parent_id):
        return  self.users("/Items", params={
                    'HasThemeSong': True,
                    'ParentId': parent_id,
                    'Recursive': True
                })

    def get_plugins(self):
        return  self._get("Plugins")

    def get_seasons(self, show_id):
        return  self.shows("/%s/Seasons" % show_id, params={
                    'UserId': "{UserId}",
                    'EnableImages': True,
                    'Fields': info()
                })

    def get_date_modified(self, date, parent_id, media=None):
        return  self.users("/Items", params={
                    'ParentId': parent_id,
                    'Recursive': True,
                    'IsMissing': False,
                    'IsVirtualUnaired': False,
                    'IncludeItemTypes': media or None,
                    'MinDateLastSaved': date,
                    'Fields': info()
                })

    def get_userdata_date_modified(self, date, parent_id, media=None):
        return  self.users("/Items", params={
                    'ParentId': parent_id,
                    'Recursive': True,
                    'IsMissing': False,
                    'IsVirtualUnaired': False,
                    'IncludeItemTypes': media or None,
                    'MinDateLastSavedForUser': date,
                    'Fields': info()
                })

    def refresh_item(self, item_id):
        return  self.items("/%s/Refresh" % item_id, "POST", json={
                    'Recursive': True,
                    'ImageRefreshMode': "FullRefresh",
                    'MetadataRefreshMode': "FullRefresh",
                    'ReplaceAllImages': False,
                    'ReplaceAllMetadata': True
                })

    def favorite(self, item_id, option=True):
        return  self.users("/FavoriteItems/%s" % item_id, "POST" if option else "DELETE")

    def get_system_info(self):
        return  self._get("System/Configuration")

    def post_capabilities(self, data):
        return  self.sessions("/Capabilities/Full", "POST", json=data)

    def session_add_user(self, session_id, user_id, option=True):
        return  self.sessions("/%s/Users/%s" % (session_id, user_id), "POST" if option else "DELETE")

    def session_playing(self, data):
        return  self.sessions("/Playing", "POST", json=data)

    def session_progress(self, data):
        return  self.sessions("/Playing/Progress", "POST", json=data)

    def session_stop(self, data):
        return  self.sessions("/Playing/Stopped", "POST", json=data)

    def item_played(self, item_id, watched):
        return  self.users("/PlayedItems/%s" % item_id, "POST" if watched else "DELETE")

    def get_sync_queue(self, date, filters=None):
        return  self._get("Emby.Kodi.SyncQueue/{UserId}/GetItems", params={
                    'LastUpdateDT': date,
                    'filter': filters or None
                })

    def get_server_time(self):
        return  self._get("Emby.Kodi.SyncQueue/GetServerDateTime")

    def get_play_info(self, item_id, profile, source_id=None, is_playback=False):
        return  self.items("/%s/PlaybackInfo" % item_id, "POST", json={
                    'UserId': "{UserId}",
                    'DeviceProfile': profile,
                    'AutoOpenLiveStream': is_playback,
                    'IsPlayback': is_playback,
                    'MediaSourceId': source_id
                })

    def get_live_stream(self, item_id, play_id, token, profile):
        return  self._post("LiveStreams/Open", json={
                    'UserId': "{UserId}",
                    'DeviceProfile': profile,
                    'OpenToken': token,
                    'PlaySessionId': play_id,
                    'ItemId': item_id
                })

    def close_live_stream(self, live_id):
        return  self._post("LiveStreams/Close", json={
                    'LiveStreamId': live_id
                })

    def close_transcode(self, device_id):
        return  self._delete("Videos/ActiveEncodings", params={
                    'DeviceId': device_id
                })

    def delete_item(self, item_id):
        return  self.items("/%s" % item_id, "DELETE")

    def is_valid_episode(self, parent_id, name, item_id):

        ''' Special function to detect if episodes are displayed in emby.
            Detect stacked versions, etc.
        '''
        try:
            result = self.shows("/%s/Episodes" % parent_id, {
                'UserId': "{UserId}",
                'AdjacentTo': item_id,
                'EnableImages': False,
                'EnableUserData': False,
                'EnableTotalRecordCount': False
            })
            for item in result['Items']:

                if str(item['Id']) == item_id:
                    return str(item['Id'])

            for item in result['Items']:

                if item['Name'] == name:
                    return str(item['Id'])
            else:
                raise Exception("NotFound")

        except Exception as error:
            return item_id

    def is_valid_series(self, parent_id, name, item_id):

        ''' Special function to detect if series is displayed or pooled.
            Use series name. I coudln't find another way.
            Returns main series id found.
        '''
        try:
            result = self.search(name, "Series")['SearchHints']

            if len(result) == 1:
                return str(result[0]['Id'])

            for item in result:

                if str(item['Id']) == item_id:
                    return str(item['Id'])

            parent_id = parent_id or self.get_library_by_item_id(item_id)['Id']
            for item in result:

                if item['Name'] == name:
                    try:
                        if self.get_library_by_item_id(item['Id'])['Id'] == parent_id:
                            return str(item['Id'])
                    except Exception:
                        pass
            else:
                raise Exception("NotFound")

        except Exception as error:
            return item_id

    def is_valid_movie(self, parent_id, name, item_id):

        ''' Special function to detect if movies should be displayed.
            Returns movie id found or itself.
        '''
        try:
            result = self.search(name, "Movie")['SearchHints']

            if len(result) == 1:
                return str(result[0]['Id'])

            for item in result:

                if str(item['Id']) == item_id:
                    return str(item['Id'])

            parent_id = parent_id or self.get_library_by_item_id(item_id)['Id']
            for item in result:

                if item['Name'] == name:
                    try:
                        if self.get_library_by_item_id(item['Id'])['Id'] == parent_id:
                            return str(item['Id'])
                    except Exception as error:
                        pass
            else:
                raise Exception("NotFound")

        except Exception as error:
            return item_id

    def get_library_by_item_id(self, item_id):

        ''' Only applies for video content. Music content has no ancestors.
            Return the library dictionary {'Id': string, 'Name': string}
        '''
        ancestors = self.get_ancestors(item_id)

        if not ancestors:
            raise Exception("EmptyAncestors")

        for ancestor in ancestors:
            if ancestor['Type'] == 'CollectionFolder':
                return ancestor
