from pprint import pprint

from argsloader.units import cdict, cvalue, number, yesno, non_negative, regexp, positive

config_loader = cdict(dict(
    train_iterations=cvalue(int(1e9), number() >> positive.int()),
    dataloader=dict(num_workers=cvalue(0, number() >> non_negative.int()), ),
    log_policy=cvalue(True, yesno()),
    # --- Hooks ---
    hook=dict(
        load_ckpt_before_run=cvalue('', regexp('^$|.*\.pth\.tar$').match.check),
        log_show_after_iter=cvalue(100, number() >> positive.int()),
        save_ckpt_after_iter=cvalue(10000, number() >> positive.int()),
        save_ckpt_after_run=cvalue(True, yesno()),
    ),
))

if __name__ == '__main__':
    pprint(config_loader.call({
        'train_iterations': int(1e10),
        'dataloader': {
            'num_workers': 1,
        },
        'hook': {
            'load_ckpt_before_run': './expert/ckpt/ckpt_best.pth.tar',
            'log_show_after_iter': 1000,
        },
    }), indent=4)
