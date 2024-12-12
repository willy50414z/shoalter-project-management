from service.sync_hybris_diff_to_revamp_svc import SyncHybrisDiffToRevampService

if __name__ == '__main__':
    sync_hybris_diff_to_revamp_svc = SyncHybrisDiffToRevampService("E:/tmp/hktv-hybris")
    output_json = sync_hybris_diff_to_revamp_svc.get_branch_change_summary("feature/HYBRIS-3718", "87653fcf5c212749e4424b3e3bc915edf06502e8")
    print(output_json)
