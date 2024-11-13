from service.sync_hybris_diff_to_revamp_svc import SyncHybrisDiffToRevampService

if __name__ == '__main__':
    sync_hybris_diff_to_revamp_svc = SyncHybrisDiffToRevampService("E:/tmp/hktv-hybris")
    output_json = sync_hybris_diff_to_revamp_svc.get_release_change_summary("origin/release/20241104_0545")
    print(output_json)
