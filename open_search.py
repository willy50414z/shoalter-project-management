import datetime

from dateutil.relativedelta import relativedelta

from service.open_search_svc import OpenSearchService

if __name__ == '__main__':
    env = "Dev"  # Dev / Staging / Prod
    output_file = ""  # "E:/aa.txt" 空值就是直接印在console
    # start_iso_datetime = "2025-02-12T18:30:00.148Z" #start datetime
    # end_iso_datetime = "2025-02-15T16:45:06.148Z" #end datetime

    start_iso_datetime = (datetime.datetime.now() - relativedelta(**{"minutes": 40})).isoformat()
    start_iso_datetime = start_iso_datetime[0:len(start_iso_datetime)-3] + "Z"
    end_iso_datetime = datetime.datetime.now().isoformat()
    end_iso_datetime = end_iso_datetime[0:len(end_iso_datetime) - 3] + "Z"

    kubernetes_pod_name = [] # pod_names
    keyword_and = ["646229c3745eefbb"] # criteria
    keyword_or = [] # criteria

    interval_unit = "months"  # years,months,days,hours,minutes
    interval_value = 1

    os_svc = OpenSearchService(env, output_file=output_file)
    os_svc.split_search_by_period(kubernetes_pod_name, keyword_and, keyword_or,
                                  start_iso_datetime, end_iso_datetime,
                                  interval_unit, interval_value)
    print(f"total output count: [{len(os_svc.exist_log_id)}]")
    print(f"query fail periods: [{os_svc.search_fail_periods}]")