import datetime
import time

import requests
import json
from typing import List
from dateutil.relativedelta import relativedelta

auth_cookie = None
header = None
index = None
miss_date = list()

class SearchPayload:
    search_payload = '{"params":{"index":"[applications]_app-cos*",' \
                     '"body":{"version":true,"size":500,"sort":[{"@timestamp":{"order":"asc","unmapped_type":"boolean"}}],"aggs":{"2":{"date_histogram":{"field":"@timestamp","fixed_interval":"10m","time_zone":"Asia/Taipei","min_doc_count":1}}},"stored_fields":["*"],"script_fields":{},"_source":{"excludes":[]},' \
                     '"query":{"bool":{"must":[],' \
                     '"filter":[],"should":[],"must_not":[]}}},"preference":1718243777255}}'
    def __init__(self):
        self.search_payload_dict = json.loads(self.search_payload)

    def set_index(self,index:str):
        self.search_payload_dict["params"]["index"] = index

    def set_filter(self, keyword_and:List[str]=[], keyword_or:List[str]=[], kubernetes_pod_names:List[str]=[]):
        keyword_filter = []
        k8s_namespace_filter = []
        keyword_filter.extend(self.gen_and_keyword_obj(keyword_and))
        keyword_filter.append(self.gen_or_keyword_obj(keyword_or))
        k8s_namespace_filter.append(self.gen_k8s_pod_name_filter(kubernetes_pod_names))
        self.search_payload_dict["params"]["body"]["query"]["bool"]["filter"].extend(keyword_filter)
        self.search_payload_dict["params"]["body"]["query"]["bool"]["filter"] += k8s_namespace_filter

    def set_data_size(self,data_size:int):
        self.search_payload_dict["params"]["body"]["size"] = data_size

    def set_range_time(self,timestamp_gte:str,timestamp_lte:str):
        range_time_payload = {
            "range": {
                "@timestamp": {"gte": timestamp_gte, "lte": timestamp_lte, "format": "strict_date_optional_time"}}}
        self.search_payload_dict["params"]["body"]["query"]["bool"]["filter"].append(range_time_payload)

    def to_json(self):
        return json.dumps(self.search_payload_dict)

    def gen_and_keyword_obj(self,keywords):
        multi_match_list = []
        for k in keywords:
            multi_match_list.append({"multi_match": {"type": "phrase", "query": k, "lenient": True}})
        return multi_match_list

    def gen_or_keyword_obj(self,keywords):
        should_list = []
        for k in keywords:
            should_list.append({"multi_match": {"type": "phrase", "query": k, "lenient": True}})
        return {"bool": {"should": should_list, "minimum_should_match": 1}}

    def gen_k8s_pod_name_filter(self,pod_name):
        match_phrase_list = []
        for n in pod_name:
            match_phrase_list.append({"match_phrase": { "kubernetes.pod_name": n }})
        return {"bool": {"should": match_phrase_list, "minimum_should_match": 1}}



def convert_timestamp(input_date_start, input_date_end, input_time_start, input_time_end):
    start_datetime = input_date_start + " " + input_time_start
    start_datetime = datetime.datetime.strptime(start_datetime, "%Y-%m-%d %H:%M:%S.%f")
    start_datetime_utc = start_datetime - datetime.timedelta(hours=8)

    end_date_time = input_date_end + " " + input_time_end
    end_date_time = datetime.datetime.strptime(end_date_time, "%Y-%m-%d %H:%M:%S.%f")
    end_date_time_utc = end_date_time - datetime.timedelta(hours=8)

    return start_datetime_utc.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z", end_date_time_utc.strftime(
        "%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

def authenticate(env,headers, uname, pwd):
    url = "https://backbone-efk.hktv.com.hk/auth/login"
    headers["referer"] = "https://backbone-efk.hktv.com.hk/app/login?"

    if (env == 'Dev' or env == 'Staging'):
        url = "https://devstg-efk.hkmpcl.com.hk//auth/login"
        headers["referer"] = "https://devstg-efk.hkmpcl.com.hk//app/login?"

    payload = {"username": uname, "password": pwd}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        print("Response cookie security_authentication:", response.cookies)
        return response.cookies.get("security_authentication")
    else:
        print(response)
        return

def get_auth_cookie_and_headers_prod(env):
    #Dev/Staging
    #username = "admin"
    #password = "developer"

    #Prod
    username = "TW-IT"
    password = "vBT78n2.Q<{)"

    base_headers = {
        'accept': '*/*',
        'accept-language': 'zh-TW,zh;q=0.9',
        'content-type': 'application/json',
        #Dev/Staging
        # 'origin': 'https://devstg-efk.hkmpcl.com.hk',
        #Prod
        'origin': 'https://backbone-efk.hktv.com.hk',
        'osd-version': '2.3.0',
        'priority': 'u=1, i',
        'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    }
    return authenticate(env,base_headers,username,password),base_headers

def get_auth_cookie_and_headers_dev(env):
    username = "admin"
    password = "developer"

    base_headers = {
        'accept': '*/*',
        'accept-language': 'zh-TW,zh;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://devstg-efk.hkmpcl.com.hk',
        'osd-version': '2.3.0',
        'priority': 'u=1, i',
        'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    }
    return authenticate(env,base_headers,username,password),base_headers

def search(env,headers, payload, auth):
    url = "https://backbone-efk.hktv.com.hk/internal/search/opensearch"
    if env == 'Dev' or env == 'Staging':
        url = "https://devstg-efk.hkmpcl.com.hk//internal/search/opensearch"

    headers["cookie"] = f"security_authentication={auth}"
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.text
    elif response.status_code == 401:
        set_env(env)
        return search(env,headers, payload, auth)
    else:
        return response.status_code

def print_result(hits):
    for hit in hits:
        print(hit['_source']['kubernetes']['namespace_name']+' : '+hit['_source']['log'])

def binary_search_time_by_inorder_traversal(env, kubernetes_pod_names: List[str]=[], keyword_and:List[str]=[], keyword_or:List[str]=[], date_start = datetime.date.today().strftime("%Y-%m-%d"), date_end = datetime.date.today().strftime("%Y-%m-%d"), time_start ="00:00:00.000", time_end ="23:59:59.999", data_size=10000):
    print(f'{date_start}:{time_start} - {date_end}:{time_end}')
    search_payload_obj = SearchPayload()
    search_payload_obj.set_index(index)
    search_payload_obj.set_data_size(data_size)
    timestamp_gte, timestamp_lte = convert_timestamp(date_start, date_end, time_start, time_end)
    search_payload_obj.set_range_time(timestamp_gte,timestamp_lte)
    search_payload_obj.set_filter(keyword_and=keyword_and,keyword_or=keyword_or, kubernetes_pod_names=kubernetes_pod_names)

    result = search(env,header,search_payload_obj.to_json(),auth_cookie)
    try:
        result_json = json.loads(result)
        if result_json['rawResponse']['_shards']['failed'] > 0:
            raise RuntimeError()
        hits = result_json["rawResponse"]["hits"]["hits"]

        if len(hits) == data_size:
            print(f'hits = {len(hits)}')
            start_time = datetime.datetime.strptime(date_start + " " + time_start, "%Y-%m-%d %H:%M:%S.%f")
            end_time = datetime.datetime.strptime(date_end + " " + time_end, "%Y-%m-%d %H:%M:%S.%f")
            middle_time = start_time + (end_time - start_time) / 2
            time.sleep(5)
            set_env(env)
            binary_search_time_by_inorder_traversal(env, keyword_and, keyword_or,
                                                    kubernetes_pod_names, date_start, middle_time.strftime("%Y-%m-%d"),
                                                    time_start, middle_time.strftime("%H:%M:%S.%f")[0:12], data_size)
            time.sleep(5)
            set_env(env)
            binary_search_time_by_inorder_traversal(env, keyword_and, keyword_or,
                                                    kubernetes_pod_names, middle_time.strftime("%Y-%m-%d"), date_end,
                                                    middle_time.strftime("%H:%M:%S.%f")[0:12], time_end, data_size)
        else:
            for hit in hits:
                print(hit['_source']['log'])
    except Exception as e :
        print(e)
        miss_date.append(f'start:[{date_start} {time_start}] - end:[{date_end} {time_end}], ')


def loop_find(env, kubernetes_pod_names, keyword_and, keyword_or,
              start_date, end_date, time_start, time_end, interval_unit, interval_value, data_size):
    current_datetime = datetime.datetime.combine(start_date,
                                                 datetime.datetime.strptime(time_start, "%H:%M:%S.%f").time())
    end_datetime = datetime.datetime.combine(end_date, datetime.datetime.strptime(time_end, "%H:%M:%S.%f").time())

    while current_datetime <= end_datetime:
        date_start = current_datetime.strftime('%Y-%m-%d')
        time_start_str = current_datetime.strftime('%H:%M:%S.%f')[:-3]

        next_datetime = current_datetime + relativedelta(**{interval_unit: interval_value})

        if next_datetime > end_datetime:
            next_datetime = end_datetime

        date_end = next_datetime.strftime('%Y-%m-%d')
        time_end_str = next_datetime.strftime('%H:%M:%S.%f')[:-3]

        binary_search_time_by_inorder_traversal(env=env,
                                                kubernetes_pod_names=kubernetes_pod_names,
                                                keyword_and=keyword_and,
                                                keyword_or=keyword_or,
                                                date_start=date_start,
                                                date_end=date_end,
                                                time_start=time_start_str,
                                                time_end=time_end_str,
                                                data_size=data_size)

        current_datetime = next_datetime
        print("-------------")
        if current_datetime >= end_datetime:
            break
    if miss_date:
        print('miss_date:')
        print(miss_date)


def set_env(env):
    global auth_cookie,header,index
    if env == 'Dev':
        auth_cookie, header = get_auth_cookie_and_headers_dev(env)
        index = "[applications]_app-cos*"
    elif env == "Staging":
        auth_cookie, header = get_auth_cookie_and_headers_dev(env)
        index = "[applications]_cos-v2-staging_*"
    elif env == "Prod":
        auth_cookie, header = get_auth_cookie_and_headers_prod(env)
        index = "[applications]_app-cos*"

if __name__ == '__main__':
    kubernetes_pod_name = ["iims","iids"]
    # Dev / Staging / Prod
    env = "Prod"
    set_env(env)

    keyword_and = []
    keyword_or = []
    start_date = datetime.datetime(2025, 2, 1)
    end_date = datetime.datetime(2025, 2, 8)
    current_date = start_date
    time_start = "00:00:00.000"
    time_end = "11:00:00.000"
    data_size = 10000

    interval_unit = "months"  #years,months,days,hours,minutes
    interval_value = 1
    loop_find(env, kubernetes_pod_name, keyword_and, keyword_or,
              start_date, end_date, time_start, time_end,
              interval_unit, interval_value, data_size)
