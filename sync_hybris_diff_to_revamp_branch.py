from service.sync_hybris_diff_to_revamp_svc import SyncHybrisDiffToRevampService
import pyperclip

if __name__ == '__main__':
    sync_hybris_diff_to_revamp_svc = SyncHybrisDiffToRevampService("E:/tmp/hktv-hybris")
    output_json = sync_hybris_diff_to_revamp_svc.get_branch_change_summary("feature/HYBRIS-3714", "1d8fb1dd511bb122cafe96182750ce76b8a04f1a")
    pyperclip.copy(output_json)
    print(output_json)
