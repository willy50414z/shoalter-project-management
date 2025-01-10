import requests
import re
import json
from datetime import datetime, timedelta
import pytz


# convert datetime UTC+8 to UTC
def convert_timestamp2(input_date_start, input_date_end, input_time_start, input_time_end):
    start_datetime = input_date_start + " " + input_time_start
    start_datetime = datetime.strptime(start_datetime, "%Y-%m-%d %H:%M:%S.%f")
    start_datetime_utc = start_datetime - timedelta(hours=8)

    end_date_time = input_date_end + " " + input_time_end
    end_date_time = datetime.strptime(end_date_time, "%Y-%m-%d %H:%M:%S.%f")
    end_date_time_utc = end_date_time - timedelta(hours=8)

    return start_datetime_utc.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z", end_date_time_utc.strftime(
        "%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def convert_timestamp(input_date):
    # Parse input timestamp in UTC+8 timezone
    input_time = datetime.strptime(input_date, "%Y-%m-%d")
    input_time = pytz.timezone('Asia/Shanghai').localize(input_time)

    # Convert the timestamp to UTC
    input_time_utc = input_time.astimezone(pytz.utc)

    # Format the UTC timestamp as "yyyy-mm-ddThh:mm:ss.000Z"
    formatted_utc_time = input_time_utc.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    # Get the next day in UTC
    next_day_utc = (input_time_utc + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    return formatted_utc_time, next_day_utc


def authenticate(headers, uname, pwd):
    url = "https://backbone-efk.hktv.com.hk/auth/login"
    headers["referer"] = "https://backbone-efk.hktv.com.hk/app/login?"
    payload = {"username": uname, "password": pwd}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        print("Response cookie security_authentication:", response.cookies)
        return response.cookies.get("security_authentication")
    else:
        print(response)
        return


def search(headers, payload, auth):
    url = "https://backbone-efk.hktv.com.hk/internal/search/opensearch"
    headers["cookie"] = f"security_authentication={auth}"
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.text
    else:
        print(response)


def gen_and_keyword_obj(keywords):
    multi_match_list = []
    for k in keywords:
        multi_match_list.append({"multi_match": {"type": "phrase", "query": k, "lenient": True}})
    return multi_match_list


def gen_or_keyword_obj(keywords):
    should_list = []
    for k in keywords:
        should_list.append({"multi_match": {"type": "phrase", "query": k, "lenient": True}})
    return {"bool": {"should": should_list, "minimum_should_match": 1}}


def gen_or_namespace_obj(namespaces):
    return


# src: response["hits"]["hits"]["_source"]
def retrieve_kubernetes_info(src):
    k = src["kubernetes"]
    print(f"container_name: {k['container_name']}, pod_name: {k['pod_name']}")
    return


# src: response["hits"]["hits"]["_source"]
def fetch_log(src):
    # pattern = r'.*\"cisPaymentInfoFirst6InCart\": \"null\".*'
    pattern = r'.*\[T-([0-9a-f]{16}),S-.*'
    pattern2 = r'.*_HikariPool.*'
    r = re.findall(pattern, src["log"])
    # u = re.findall(user_pk_pattern, src["log"])
    if len(r) > 0:

        print(r[0])
        # print(f"{r[0]}\t{u[0]}\t{src['@timestamp']}")
        return 1
        # retrieve_kubernetes_info(src)
    return 0


if __name__ == "__main__":
    username = "TW-IT"
    password = "vBT78n2.Q<{)"

    keyword_and = ["this is NOT parallel run flow"]
    keyword_or = []
    date_start = "2024-08-08"
    date_end = "2024-08-08"
    time_start = "00:00:00.000"
    time_end = "12:00:00.000"
    data_size = 8000
    index_pattern = "[applications]_app-cos*"
    base_headers = {
        'accept': '*/*',
        'accept-language': 'zh-TW,zh;q=0.9',
        'content-type': 'application/json',
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
    search_payload = '{"params":{"index":"[applications]_app-cos*",' \
                     '"body":{"version":true,"size":500,"sort":[{"@timestamp":{"order":"asc","unmapped_type":"boolean"}}],"aggs":{"2":{"date_histogram":{"field":"@timestamp","fixed_interval":"10m","time_zone":"Asia/Taipei","min_doc_count":1}}},"stored_fields":["*"],"script_fields":{},"_source":{"excludes":[]},' \
                     '"query":{"bool":{"must":[],' \
                     '"filter":[{"bool":{"minimum_should_match":1,"should":[{"match_phrase":{"kubernetes.namespace_name":"shoalter-ecommerce-engine"}}]}}],"should":[],"must_not":[]}}},"preference":1718243777255}}'
    # login to get auth cookie
    auth_cookie = authenticate(base_headers, username, password)
    # search pattern
    search_payload_json = json.loads(search_payload)
    # setup index pattern
    search_payload_json["params"]["index"] = index_pattern
    # opensearch dashboards ui only 500 a time
    search_payload_json["params"]["body"]["size"] = data_size
    # prepare field filter payload like namespace_name, container_name, etc
    # field_filter = [{"bool":{"should":[{"match_phrase":{"kubernetes.container_name":"cart"}}],"minimum_should_match":1}}]
    field_filter = []
    # prepare keyword filter payload
    keyword_filter = []
    # add AND keywords
    keyword_filter.extend(gen_and_keyword_obj(keyword_and))
    # add OR keywords, more than 25 will die, more than 22 will show no result
    keyword_filter.append(gen_or_keyword_obj(keyword_or))
    search_payload_json["params"]["body"]["query"]["bool"]["filter"].extend(keyword_filter)
    # search time range in UTC
    # timestamp_gte, timestamp_lte = convert_timestamp(data_date)  # UTC
    timestamp_gte, timestamp_lte = convert_timestamp2(date_start, date_end, time_start, time_end)  # UTC+8 to UTC
    range_time_payload = {
        "range": {"@timestamp": {"gte": timestamp_gte, "lte": timestamp_lte, "format": "strict_date_optional_time"}}}
    search_payload_json["params"]["body"]["query"]["bool"]["filter"].append(range_time_payload)
    search_payload_json["params"]["body"]["query"]["bool"]["filter"] += field_filter
    search_payload = json.dumps(search_payload_json)

    result = search(base_headers, search_payload, auth_cookie)  # raw text
    result_json = json.loads(result)  # parse json
    hits = result_json["rawResponse"]["hits"]["hits"]  # get hits
    print(len(hits))
    trace_ids = []
    c = 0
    for hit in hits:
        # retrieve_kubernetes_info(hit["_source"])
        c += fetch_log(hit["_source"])
    # logs = [hit["_source"]["log"] for hit in hits]  # get filtered log
    # print(len(logs))
    print(c)