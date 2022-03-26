from enum import Enum, unique
from pprint import pprint

from argsloader.units import cdict, enum, cvalue, yesno, number, is_type, cfree, getitem_, onoff, nature, \
    positive


@unique
class PolicyType(Enum):
    C51 = 1


@unique
class DecayType(Enum):
    EXP = 1
    LINEAR = 2


@unique
class CollectElementType(Enum):
    STEP = 1
    SAMPLE = 2
    EPISODE = 3


config_loader = cdict(dict(
    # (str) RL policy register name (refer to function "POLICY_REGISTRY").
    type=cvalue('c51', enum(PolicyType)),
    # (bool) Whether to use cuda for network.
    cuda=cvalue(False, yesno() | onoff()),
    # (bool) Whether the RL algorithm is on-policy or off-policy.
    on_policy=cvalue(False, yesno()),
    # (bool) Whether use priority(priority sample, IS weight, update priority)
    priority=cvalue(False, yesno()),
    # (float) Reward's future discount factor, aka. gamma.
    discount_factor=cvalue(0.97, number()),
    # (int) N-step reward for target q_value estimation
    nstep=cvalue(1, number() >> nature()),
    model=dict(
        v_min=cvalue(-10, number()),
        v_max=cvalue(10, number()),
        n_atom=cvalue(51, number()),
    ),
    learn=dict(
        # (bool) Whether to use multi gpu
        multi_gpu=cvalue(False, yesno()),
        # How many updates(iterations) to train after collector's one collection.
        # Bigger "update_per_collect" means bigger off-policy.
        # collect data -> update policy-> collect data -> ...
        update_per_collect=cvalue(3, number() >> positive.int()),
        batch_size=cvalue(64, number() >> positive.int()),
        learning_rate=cvalue(0.001, number()),
        # ==============================================================
        # The following configs are algorithm-specific
        # ==============================================================
        # (int) Frequency of target network update.
        target_update_freq=cvalue(100, number() >> is_type(int)),
        # (bool) Whether ignore done(usually for max step termination env)
        ignore_done=cvalue(False, yesno()),
    ),
    # collect_mode config
    collect=dict(
        # (int) Only one of [n_sample, n_step, n_episode] should be set
        # n_sample=8,
        collect_element_type=cfree(
            (
                    (getitem_('n_sample') & 'sample') |
                    (getitem_('n_step') & 'step') |
                    (getitem_('n_episode') & 'episode') |
                    'sample'
            ) >> enum(CollectElementType),
        ),
        collect_number=cfree(
            (
                    getitem_('n_sample') | getitem_('n_step') |
                    getitem_('n_episode') | 8
            ) >> number() >> positive.int()
        ),
        # (int) Cut trajectories into pieces with length "unroll_len".
        unroll_len=cvalue(1, number() >> positive.int()),
    ),
    eval=dict(),
    # other config
    other=dict(
        # Epsilon greedy with decay.
        eps=dict(
            # (str) Decay type. Support ['exp', 'linear'].
            type=cvalue('exp', enum(DecayType)),
            start=cvalue(0.95, number()),
            end=cvalue(0.1, number()),
            # (int) Decay length(env step)
            decay=cvalue(10000, number() >> positive.int()),
        ),
        replay_buffer=dict(
            replay_buffer_size=cvalue(10000, number() >> positive.int()),
        )
    ),
))

if __name__ == '__main__':
    pprint(config_loader.call({
        'collect': {
            'n_episode': 13,
        },
        'cuda': 'on',
    }), indent=4)
