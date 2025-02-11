from service.open_search_svc import OpenSearchService

if __name__ == '__main__':
    env = "Prod"  # Dev / Staging / Prod
    output_file = "E:/aa.txt"  # "E:/aa.txt" 空值就是直接印在console
    start_iso_datetime = "2025-02-01T00:55:00.001Z" #start datetime
    end_iso_datetime = "2025-02-01T01:00:00.001Z" #end datetime
    kubernetes_pod_name = ["iims", "iids"] # pod_names
    keyword_and = [] # criteria
    keyword_or = [] # criteria

    interval_unit = "months"  # years,months,days,hours,minutes
    interval_value = 1

    os_svc = OpenSearchService(env, output_file=output_file)
    os_svc.split_search_by_period(kubernetes_pod_name, keyword_and, keyword_or,
                                  start_iso_datetime, end_iso_datetime,
                                  interval_unit, interval_value)
    print(f"total output count: [{len(os_svc.exist_log_id)}]")
    print(f"query fail periods: [{os_svc.search_fail_periods}]")