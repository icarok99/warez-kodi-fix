# -*- coding: utf-8 -*-

WEBSITE = 'CDN'

import re
import os
import sys
# try:
#     from resources.lib.autotranslate import AutoTranslate
#     portuguese = AutoTranslate.language('Portuguese')
#     english = AutoTranslate.language('English')
#     select_option_name = AutoTranslate.language('select_option')
# except ImportError:
#     portuguese = 'DUBLADO'
#     english = 'LEGENDADO'
#     select_option_name = 'SELECIONE UMA OPÇÃO ABAIXO:'
# try:
#     from resources.lib import resolveurl
#     from resources.lib.unblock import unblock as requests
# except ImportError:
#     local_path = os.path.dirname(os.path.realpath(__file__))
#     lib_path = local_path.replace('scrapers', '')
#     sys.path.append(lib_path)
#     from resolvers import resolveurl
#     from unblock import unblock as requests
import requests
from urllib.parse import urljoin as resolveurl
portuguese = 'DUBLADO'
english = 'LEGENDADO'
select_option_name = 'SELECIONE UMA OPÇÃO ABAIXO:'

class source:
    __headers__ = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0', 'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3'}

    @classmethod
    def warezcdn_servers(cls,imdb,season=False,episode=False):
        links = []
        referer = 'https://embed.warezcdn.com/'
        headers = cls.__headers__
        headers.update({'Referer': referer})        
        if season and episode:
            url = 'https://embed.warezcdn.com/serie/%s/%s/%s'%(str(imdb),str(season),str(episode))
            data = requests.get(url,headers=headers).text
            audio_id = re.compile('<div class="item" data-load-episode-content="(.*?)">.+?<img class="img" src="(.*?)" loading="lazy">.+?<div class="name">(.*?)</div>', re.MULTILINE|re.DOTALL|re.IGNORECASE).findall(data)
            if audio_id:
                audio = ''
                for id, img, name in audio_id:
                    if str(episode) in name:
                        audio += str(id)
                        break
                if audio:
                    data2 = requests.post('https://embed.warezcdn.net/serieAjax.php', headers=headers, data={'getAudios': audio}).json()
                    lang = []
                    languages = data2.get('list', '')
                    if languages:
                        for key in languages:
                            d = languages[key]
                            _id = d['id']
                            audio = d['audio']
                            mixdrop = d.get('mixdropStatus', '')
                            fembed = d.get('fembedStatus', '')
                            streamtape = d.get('streamtapeStatus', '')
                            warezcdn = d.get('warezcdnStatus', '')
                            lang.append((_id,audio,mixdrop,fembed,streamtape,warezcdn))
                    if lang:
                        lang2 = []
                        for _id,audio,mixdrop,fembed,streamtape,warezcdn in lang:
                            if str(audio) == '1' or str(audio) == 'Original':
                                audio = english
                            elif str(audio) == '2' or str(audio) == 'Dublado':
                                audio  = portuguese
                            else:
                                audio = 'UNKNOW'
                            if mixdrop == '3':                        
                                url = 'https://embed.warezcdn.net/getPlay.php?id=%s&sv=mixdrop'%str(_id)
                                lang2.append(('MIXDROP', audio, url))
                            if fembed == '3':
                                url = 'https://embed.warezcdn.net/getPlay.php?id=%s&sv=fembed'%str(_id)
                                lang2.append(('FEMBED', audio, url))                            
                            if streamtape == '3':
                                url = 'https://embed.warezcdn.net/getPlay.php?id=%s&sv=streamtape'%str(_id)
                                lang2.append(('STREAMTAPE',audio,url))
                            if warezcdn == '3':
                                url = 'https://warezcdn.com/player/player.php?id=%s'%str(_id)
                                lang2.append(('CDN', audio, url))
                        if lang2:
                            for name, audio, url in lang2:
                                if name in ['MIXDROP', 'STREAMTAPE']:
                                    name = name + ' - ' + audio
                                    links.append((name,url))

                                #     try:
                                #         r = requests.get(url,headers=headers)
                                #         src = r.text
                                #         try:
                                #             src = re.compile('window.location.href="(.*?)"').findall(src)[0]
                                #         except:
                                #             src = ''
                                #         if src:
                                #             try:
                                #                 sub = src.split('http')[2]
                                #                 sub = 'http%s'%sub
                                #                 try:
                                #                     sub = sub.split('&')[0]
                                #                 except:
                                #                     pass
                                #                 if not '.srt' in sub:
                                #                     sub = ''                                            
                                #             except:
                                #                 sub = ''
                                #             try:
                                #                 src = src.split('?')[0]
                                #             except:
                                #                 pass
                                #             try:
                                #                 src = src.split('#')[0]
                                #             except:
                                #                 pass                                                 
                                #             name = name + ' - ' + audio
                                #             servers.append((name,src,sub))
                                #     except:
                                #         pass
                                # elif name == 'CDN':
                                #     name = 'ALTERNATIVO' + ' - ' + audio
                                #     servers.append((name,url,''))

        else:
            url = 'https://embed.warezcdn.com/filme/%s'%str(imdb)
            data = requests.get(url,headers=headers).text
            audio_id = re.compile('<div class="selectAudioButton.+?" data-load-hosts="(.*?)">(.*?)</div>', re.MULTILINE|re.DOTALL|re.IGNORECASE).findall(data)
            if not audio_id:
                audio_id = []
                idioma = re.compile('<div class="selectAudio">(.*?)</div>', re.MULTILINE|re.DOTALL|re.IGNORECASE).findall(data)
                if idioma:
                    text = idioma[0].lower()
                    if 'dublado' in text:
                        lg = 'DUBLADO'
                    elif 'legendado' in text:
                        lg = 'LEGENDADO'
                    else:
                        lg = ''
                    if lg:
                        id_audio = re.compile('<div class="hostList active" data-audio-id="(.*?)">', re.MULTILINE|re.DOTALL|re.IGNORECASE).findall(data)
                        if id_audio:
                            audio_id.append((id_audio[0],lg))
            if audio_id:
                lang = {}
                for id, lg in audio_id:
                    if 'LEGENDADO' in lg:
                        lang[id]=english
                    elif 'DUBLADO' in lg:
                        lang[id]=portuguese
                hosts = re.compile('<div class="buttonLoadHost.+?" data-load-embed="(.*?)" data-load-embed-host="(.*?)">', re.MULTILINE|re.DOTALL|re.IGNORECASE).findall(data)
                if hosts:
                    for id, name in hosts:
                        lg=lang[id]
                        if name in ['mixdrop', 'streamtape']:
                            url = 'https://embed.warezcdn.net/getPlay.php?id=%s&sv=%s'%(str(id),name)
                            if name == 'streamtape':
                                name = 'STREAMTAPE' + ' - ' + lg
                            else:
                                name = 'MIXDROP' + ' - ' + lg
                            links.append((name,url))                           

                        #     try:
                        #         r = requests.get(url,headers=headers)
                        #         src = r.text
                        #         try:
                        #             src = re.compile('window.location.href="(.*?)"').findall(src)[0]
                        #         except:
                        #             src = ''
                        #         if src:
                        #             try:
                        #                 sub = src.split('http')[2]
                        #                 sub = 'http%s'%sub
                        #                 try:
                        #                     sub = sub.split('&')[0]
                        #                 except:
                        #                     pass
                        #                 if not '.srt' in sub:
                        #                     sub = ''                                            
                        #             except:
                        #                 sub = ''
                        #             try:
                        #                 src = src.split('?')[0]
                        #             except:
                        #                 pass
                        #             try:
                        #                 src = src.split('#')[0]
                        #             except:
                        #                 pass
                        #             if name == 'streamtape':
                        #                 name = 'STREAMTAPE' + ' - ' + lg
                        #             else:
                        #                 name = 'MIXDROP' + ' - ' + lg
                        #             servers.append((name,src,sub))
                        #     except:
                        #         pass
                        # elif name == 'warezcdn':
                        #     src = 'https://warezcdn.com/player/player.php?id=%s'%str(id)
                        #     name = 'ALTERNATIVO' + ' - ' + lg
                        #     servers.append((name,src,''))


        return links
    
    @classmethod
    def search_movies(cls,imdb,year):
        try:
            return cls.warezcdn_servers(imdb,False,False)
        except:
            return []      
    
    @classmethod
    def resolve_movies(cls,url):
        #referer_player = 'https://warezcdn.com/'
        referer_player = ''
        streams = []
        if 'embed.warezcdn' in url:
            referer = 'https://embed.warezcdn.com/'
            headers = cls.__headers__
            headers.update({'Referer': referer})            
            try:
                r = requests.get(url,headers=headers)
                src = r.text
                try:
                    src = re.compile('window.location.href="(.*?)"').findall(src)[0]
                except:
                    src = ''
                if src:
                    try:
                        sub = src.split('http')[2]
                        sub = 'http%s'%sub
                        try:
                            sub = sub.split('&')[0]
                        except:
                            pass
                        if not '.srt' in sub:
                            sub = ''                                            
                    except:
                        sub = ''
                    try:
                        src = src.split('?')[0]
                    except:
                        pass
                    try:
                        src = src.split('#')[0]
                    except:
                        pass
                    stream, sub2 = resolveurl(src,referer_player)
                    if sub:
                        subfinal = sub
                    else:
                        subfinal = sub2
                    streams.append((stream,subfinal))
            except:
                pass          
        return streams
    
    @classmethod
    def search_tvshows(cls,imdb,year,season,episode):
        try:
            return cls.warezcdn_servers(imdb,season,episode)
        except:
            return []    

    @classmethod
    def resolve_tvshows(cls,url):
        #referer_player = 'https://warezcdn.com/'
        referer_player = ''
        streams = []
        if 'embed.warezcdn' in url:
            referer = 'https://embed.warezcdn.com/'
            headers = cls.__headers__
            headers.update({'Referer': referer})            
            try:
                r = requests.get(url,headers=headers)
                src = r.text
                try:
                    src = re.compile('window.location.href="(.*?)"').findall(src)[0]
                except:
                    src = ''
                if src:
                    try:
                        sub = src.split('http')[2]
                        sub = 'http%s'%sub
                        try:
                            sub = sub.split('&')[0]
                        except:
                            pass
                        if not '.srt' in sub:
                            sub = ''                                            
                    except:
                        sub = ''
                    try:
                        src = src.split('?')[0]
                    except:
                        pass
                    try:
                        src = src.split('#')[0]
                    except:
                        pass
                    stream, sub2 = resolveurl(src,referer_player)
                    if sub:
                        subfinal = sub
                    else:
                        subfinal = sub2
                    streams.append((stream,subfinal))
            except:
                pass          
        return streams                    
