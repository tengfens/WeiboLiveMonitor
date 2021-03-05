from endpoints import *
from urllib.request import Request, urlopen
import time
import json
import os
import time
from random import randint

MONTH_MAP = {
    "Jan": '01',
    "Feb": '02',
    "Mar": '03',
    "Apr": '04',
    "May": '05',
    "Jun": '06',
    "Jul": '07',
    "Aug": '08',
    "Sep": '09',
    "Oct": '10',
    "Nov": '11',
    "Dec": '12'
}

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'}
PROXIES = {'http':'http://child-prc.intel.com:913', 'https':'http://child-prc.intel.com:913'}

class UpdateEngine(object):
    def __init__(self, uid_list):
        self.__uid_list = uid_list
        self.__data_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
        if not os.path.exists(self.__data_folder):
            os.makedirs(self.__data_folder)

    def __update_meta_for_one_user(self, uid):
        print("[{}] @{}: updating live meta".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), uid))
        meta_json = os.path.join(self.__data_folder, uid + '.json')
        if os.path.exists(meta_json):
            live_meta = json.load(open(meta_json, 'r+'))
        else:
            live_meta = {}

        user_name = ''
        for attempt in range(3):
            try:
                user_info = CONTAINER_USER_INFO % (uid, uid)
                req = Request(user_info, headers=HEADERS)
                res_content = urlopen(req).read().decode(errors='ignore')
                res = json.loads(res_content)
            except:
                res = {}
            if 'ok' in res.keys() and res['ok'] == 1:
                user_name = res['data']['userInfo']['screen_name']
                break
        
        weibo_data = {}
        for attempt in range(3):
            try:
                user_home_page = CONTAINER_USER_PAGE % (uid, uid, uid)
                req = Request(user_home_page, headers=HEADERS)
                res_content = urlopen(req).read().decode(errors='ignore')
                res = json.loads(res_content)
            except:
                res = {}
            if 'ok' in res.keys() and res['ok'] == 1:
                weibo_data = res['data']['cards']
                print("[{}] @{}: get home page successfully".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), uid))
                break
        if not weibo_data:
            print("[{}] @{}: failed to access home page".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), uid))

        live_meta_diff = {}
        for card in weibo_data:
            if 'page_info' in card['mblog'].keys():
                if card['mblog']['page_info']['type'] == 'live':
                    live_url = card['mblog']['page_info']['page_url']
                    live_id = os.path.basename(live_url)
                    live_time = card['mblog']['created_at'].split()
                    live_time_str = live_time[5] + MONTH_MAP[live_time[1]] + live_time[2] + live_time[3].replace(':', '')
                    if live_time_str not in live_meta.keys():
                        print("[{}] @{}: adding new live {}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), uid, live_time_str))
                        live_flv_url = ''
                        live_hls_url = ''
                        live_replay_url = ''
                        live_stream_id = ''
                        live_req_url = LIVE_REQUEST_PAGE % (live_id)
                        for attempt in range(3):
                            try:
                                live_req = Request(live_req_url, headers=HEADERS)
                                live_res_content = urlopen(live_req).read().decode(errors='ignore')
                                live_res = json.loads(live_res_content)
                            except:
                                live_res = {}
                            if 'msg' in live_res.keys() and live_res['msg'] == 'success':
                                live_flv_url = live_res['data']['item']['stream_info']['pull']['live_origin_flv_url']
                                live_hls_url = live_res['data']['item']['stream_info']['pull']['live_origin_hls_url']
                                live_stream_id = os.path.basename(live_hls_url).split('.')[0]
                                live_replay_url = LIVE_REPLAY_PAGE % (live_stream_id)
                                break
                        live_meta[live_time_str] = {}
                        live_meta[live_time_str]['live_id'] = live_id
                        live_meta[live_time_str]['url'] = live_url
                        live_meta[live_time_str]['url_mobile'] = LIVE_PAGE_H5 % (live_id)
                        live_meta[live_time_str]['live_stream_id'] = live_stream_id
                        live_meta[live_time_str]['live_flv_url'] = live_flv_url
                        live_meta[live_time_str]['live_hls_url'] = live_hls_url
                        live_meta[live_time_str]['live_replay_url'] = live_replay_url

                        live_meta_diff[live_time_str] = live_meta[live_time_str]
        self.__save_json(meta_json, live_meta)
        return user_name, live_meta_diff

    def __save_json(self, meta_json, meta_data):
        data = json.dumps(meta_data, indent=4, separators=(', ', ': '), ensure_ascii=False)
        print(data)
        file = open(meta_json, 'w+')
        file.write(data)
        file.close()

    def update_meta(self):
        meta_diff = {}
        for uid in self.__uid_list:
            user, diff = self.__update_meta_for_one_user(uid)
            time.sleep(randint(1, 10))
            if diff:
                meta_diff[user] = {}
                meta_diff[user]['uid'] = uid
                meta_diff[user]['diff'] = diff
        return meta_diff
