from service.sync_hybris_diff_to_revamp_svc import SyncHybrisDiffToRevampService

if __name__ == '__main__':
    sync_hybris_diff_to_revamp_svc = SyncHybrisDiffToRevampService("E:/tmp/hktv-hybris")
    output_json = sync_hybris_diff_to_revamp_svc.get_branch_change_summary("POC/check_revamp_3580", "1d8fb1dd511bb122cafe96182750ce76b8a04f1a")
    print(output_json)
