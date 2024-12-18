import pyperclip

from service.sync_hybris_diff_to_revamp_svc import SyncHybrisDiffToRevampService

if __name__ == '__main__':
    sync_hybris_diff_to_revamp_svc = SyncHybrisDiffToRevampService("E:/tmp/hktv-hybris")
    output_json = sync_hybris_diff_to_revamp_svc.get_release_change_summary("origin/release/20241216_0545")
    pyperclip.copy(output_json)
    print(output_json)
