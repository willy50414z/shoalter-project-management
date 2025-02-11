from datetime import datetime, timezone
import time

import datetime
from zoneinfo import ZoneInfo

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

    def set_index(self, index: str):
        self.search_payload_dict["params"]["index"] = index

    def set_filter(self, keyword_and: List[str] = [], keyword_or: List[str] = [], kubernetes_pod_names: List[str] = []):
        keyword_filter = []
        k8s_namespace_filter = []
        keyword_filter.extend(self.gen_and_keyword_obj(keyword_and))
        keyword_filter.append(self.gen_or_keyword_obj(keyword_or))
        k8s_namespace_filter.append(self.gen_k8s_pod_name_filter(kubernetes_pod_names))
        self.search_payload_dict["params"]["body"]["query"]["bool"]["filter"].extend(keyword_filter)
        self.search_payload_dict["params"]["body"]["query"]["bool"]["filter"] += k8s_namespace_filter

    def set_data_size(self, data_size: int):
        self.search_payload_dict["params"]["body"]["size"] = data_size

    def set_range_time(self, timestamp_gte: str, timestamp_lte: str):
        range_time_payload = {
            "range": {
                "@timestamp": {"gte": timestamp_gte, "lte": timestamp_lte, "format": "strict_date_optional_time"}}}
        self.search_payload_dict["params"]["body"]["query"]["bool"]["filter"].append(range_time_payload)

    def to_json(self):
        return json.dumps(self.search_payload_dict)

    def gen_and_keyword_obj(self, keywords):
        multi_match_list = []
        for k in keywords:
            multi_match_list.append({"multi_match": {"type": "phrase", "query": k, "lenient": True}})
        return multi_match_list

    def gen_or_keyword_obj(self, keywords):
        should_list = []
        for k in keywords:
            should_list.append({"multi_match": {"type": "phrase", "query": k, "lenient": True}})
        return {"bool": {"should": should_list, "minimum_should_match": 1}}

    def gen_k8s_pod_name_filter(self, pod_name):
        match_phrase_list = []
        for n in pod_name:
            match_phrase_list.append({"match_phrase": {"kubernetes.pod_name": n}})
        return {"bool": {"should": match_phrase_list, "minimum_should_match": 1}}


class OpenSearchService:

    def __init__(self, env, output_file=None, data_size=10000):
        self.auth_cookie = None
        self.header = None
        self.env = env
        self.data_size = data_size
        self.set_env()
        self.output_file = output_file
        self.search_result = []
        self.exist_log_id = []
        self.search_fail_periods = []
        if self.env == 'Dev':
            self.index = "[applications]_app-cos*"
        elif self.env == "Staging":
            self.index = "[applications]_cos-v2-staging_*"
        elif self.env == "Prod":
            self.index = "[applications]_app-cos*"

    def iso_to_datetime(self, iso_datetime):
        return datetime.datetime.strptime(iso_datetime, "%Y-%m-%dT%H:%M:%S.%fZ")

    def convert_timestamp(self, input_date_start, input_date_end, input_time_start, input_time_end):
        start_datetime = input_date_start + " " + input_time_start
        start_datetime = datetime.datetime.strptime(start_datetime, "%Y-%m-%d %H:%M:%S.%f")
        start_datetime_utc = start_datetime - datetime.timedelta(hours=8)

        end_date_time = input_date_end + " " + input_time_end
        end_date_time = datetime.datetime.strptime(end_date_time, "%Y-%m-%d %H:%M:%S.%f")
        end_date_time_utc = end_date_time - datetime.timedelta(hours=8)

        return start_datetime_utc.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z", end_date_time_utc.strftime(
            "%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    def authenticate(self, env, headers, uname, pwd):
        url = "https://backbone-efk.hktv.com.hk/auth/login"
        headers["referer"] = "https://backbone-efk.hktv.com.hk/app/login?"

        if self.env == 'Dev' or self.env == 'Staging':
            url = "https://devstg-efk.hkmpcl.com.hk/auth/login"
            headers["referer"] = "https://devstg-efk.hkmpcl.com.hk/app/login?"

        payload = {"username": uname, "password": pwd}
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            print("Response cookie security_authentication:", response.cookies)
            return response.cookies.get("security_authentication")
        else:
            print(response)
            return

    def get_auth_cookie_and_headers_prod(self, env):
        # Dev/Staging
        # username = "admin"
        # password = "developer"

        # Prod
        username = "TW-IT"
        password = "vBT78n2.Q<{)"

        base_headers = {
            'accept': '*/*',
            'accept-language': 'zh-TW,zh;q=0.9',
            'content-type': 'application/json',
            # Dev/Staging
            # 'origin': 'https://devstg-efk.hkmpcl.com.hk',
            # Prod
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
        return self.authenticate(env, base_headers, username, password), base_headers

    def get_auth_cookie_and_headers_dev(self, env):
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
        return self.authenticate(env, base_headers, username, password), base_headers

    def search(self, headers, payload):
        url = "https://backbone-efk.hktv.com.hk/internal/search/opensearch"
        if self.env == 'Dev' or self.env == 'Staging':
            url = "https://devstg-efk.hkmpcl.com.hk/internal/search/opensearch"

        headers["cookie"] = f"security_authentication={self.auth_cookie}"
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.text
        elif response.status_code == 401:
            self.set_env()
            return self.search(headers, payload)
        else:
            return response.status_code

    # def print_result(self, hits):
    #     for hit in hits:
    #         print(hit['_source']['kubernetes']['namespace_name'] + ' : ' + hit['_source']['log'])

    def datetime_to_opensearch_time(self, datetime):
        iso_format = datetime.astimezone(ZoneInfo("UTC")).isoformat()
        million_second = iso_format[iso_format.rfind(".") + 1:iso_format.rfind("+")]
        return iso_format[:iso_format.rfind(".")] + "." + million_second[0:3] + "Z"

    def build_payload(self, start_datetime, end_datetime, kubernetes_pod_names, keyword_and, keyword_or):
        search_payload_obj = SearchPayload()
        search_payload_obj.set_index(self.index)
        search_payload_obj.set_data_size(self.data_size)
        # timestamp_gte, timestamp_lte = convert_timestamp(date_start, date_end, time_start, time_end)
        search_payload_obj.set_range_time(self.datetime_to_opensearch_time(start_datetime),
                                          self.datetime_to_opensearch_time(end_datetime))
        search_payload_obj.set_filter(keyword_and=keyword_and, keyword_or=keyword_or,
                                      kubernetes_pod_names=kubernetes_pod_names)
        return search_payload_obj

    def handle_query_result(self, hits):
        output_file_content = ""
        for hit in hits:
            if hit["_id"] not in self.exist_log_id:
                self.exist_log_id.append(hit["_id"])
                if self.output_file:
                    output_file_content = f"{output_file_content}{hit['_source']['kubernetes']['namespace_name'] + '\t' + hit['_source']['log']}"
                else:
                    print(hit['_source']['kubernetes']['namespace_name'] + '\t' + hit['_source']['log'][
                                                                                  :len(hit['_source']['log']) - 2])
        if len(output_file_content)>0:
            with open(self.output_file, "a", encoding="utf-8") as file:
                file.write(output_file_content)
            print(f"{len(hits)} hits has outputs to {self.output_file}")

    def add_to_fail_search_periods(self, start_datetime, end_datetime, e):
        self.search_fail_periods.append({"start_datetime": self.datetime_to_opensearch_time(start_datetime),
                                         "end_datetime": self.datetime_to_opensearch_time(end_datetime),
                                         "exception": e})

    def search_opensearch(self, start_datetime, end_datetime, kubernetes_pod_names=[], keyword_and=[],
                          keyword_or=[]):
        search_payload_obj = self.build_payload(start_datetime, end_datetime, kubernetes_pod_names, keyword_and,
                                                keyword_or)

        search_result = self.search(self.header, search_payload_obj.to_json())
        try:
            result_json = json.loads(search_result)
            if "hits" in result_json["rawResponse"] and "hits" in result_json["rawResponse"]["hits"] and \
                    result_json['rawResponse']['_shards']['failed'] == 0:
                hits = result_json["rawResponse"]["hits"]["hits"]
                self.handle_query_result(hits)
            else:
                self.add_to_fail_search_periods(start_datetime, end_datetime, search_result)
                return

            if len(hits) == self.data_size:
                last_log_time_utc = datetime.datetime.strptime(hits[len(hits) - 1]["_source"]["time"][:26],
                                                               "%Y-%m-%dT%H:%M:%S.%f")
                last_log_time_hk = last_log_time_utc + relativedelta(**{"hours": 8})
                last_log_time_hk = last_log_time_hk.astimezone(ZoneInfo("Asia/Hong_Kong"))
                self.search_opensearch(last_log_time_hk, end_datetime, kubernetes_pod_names, keyword_and, keyword_or)
        except Exception as e:
            self.add_to_fail_search_periods(start_datetime, end_datetime, e)

    def split_search_by_period(self, kubernetes_pod_names, keyword_and, keyword_or,
                               start_iso_datetime, end_iso_datetime, interval_unit, interval_value):
        start_datetime = self.iso_to_datetime(start_iso_datetime)
        end_datetime = self.iso_to_datetime(end_iso_datetime)
        while start_datetime <= end_datetime:
            next_datetime = start_datetime + relativedelta(**{interval_unit: interval_value})
            self.search_opensearch(kubernetes_pod_names=kubernetes_pod_names,
                                   keyword_and=keyword_and,
                                   keyword_or=keyword_or,
                                   start_datetime=start_datetime,
                                   end_datetime=end_datetime)

            start_datetime = next_datetime
            if start_datetime >= end_datetime:
                break

    def set_env(self):
        if self.env == 'Dev':
            self.auth_cookie, self.header = self.get_auth_cookie_and_headers_dev(self.env)
        elif self.env == "Staging":
            self.auth_cookie, self.header = self.get_auth_cookie_and_headers_dev(self.env)
        elif self.env == "Prod":
            self.auth_cookie, self.header = self.get_auth_cookie_and_headers_prod(self.env)
