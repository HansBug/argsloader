from enum import Enum, unique
from pprint import pprint

from argsloader.units import cdict, cvalue, number, enum, yesno, onoff, positive, interval, is_type


@unique
class PolicyType(Enum):
    RAINBOW = 1


@unique
class EpsilonGreedyDecayType(Enum):
    EXP = 1
    LINEAR = 2


@unique
class ReplayBufferType(Enum):
    NAIVE_REPLAY_BUFFER_DICT = 1
    ADVANCED_REPLAY_BUFFER_DICT = 2


config_loader = cdict(
    dict(
        # (str) RL policy register name (refer to function "POLICY_REGISTRY").
        type=cvalue('rainbow', enum(PolicyType)),
        # (bool) Whether to use cuda for network.
        cuda=cvalue(False, yesno() | onoff()),
        # (bool) Whether the RL algorithm is on-policy or off-policy.
        on_policy=cvalue(False, yesno()),
        # (bool) Whether use priority(priority sample, IS weight, update priority)
        priority=cvalue(True, yesno()),
        # (bool) Whether use Importance Sampling Weight to correct biased update. If True, priority must be True.
        priority_IS_weight=cvalue(False, yesno()),
        # (int) Number of training samples(randomly collected) in replay buffer when training starts.
        # random_collect_size=2000,
        model=dict(
            # (float) Value of the smallest atom in the support set.
            # Default to -10.0.
            v_min=cvalue(-10, number() >> is_type(int)),
            # (float) Value of the smallest atom in the support set.
            # Default to 10.0.
            v_max=cvalue(10, number() >> is_type(int)),
            # (int) Number of atoms in the support set of the
            # value distribution. Default to 51.
            n_atom=cvalue(51, number() >> positive.int()),
        ),
        # (float) Reward's future discount factor, aka. gamma.
        discount_factor=cvalue(0.99, number() >> interval.LR(0, 1)),
        # (int) N-step reward for target q_value estimation
        nstep=cvalue(3, number() >> positive.int()),
        learn=dict(
            # (bool) Whether to use multi gpu
            multi_gpu=cvalue(False, yesno()),
            # How many updates(iterations) to train after collector's one collection.
            # Bigger "update_per_collect" means bigger off-policy.
            # collect data -> update policy-> collect data -> ...
            update_per_collect=cvalue(1, number() >> positive.int()),
            batch_size=cvalue(32, number() >> positive.int()),
            learning_rate=cvalue(0.001, number() >> interval.l(0)),
            # ==============================================================
            # The following configs are algorithm-specific
            # ==============================================================
            # (int) Frequence of target network update.
            target_update_freq=cvalue(100, number() >> positive.int()),
            # (bool) Whether ignore done(usually for max step termination env)
            ignore_done=cvalue(False, yesno()),
        ),
        # collect_mode config
        collect=dict(
            # (int) Only one of [n_sample, n_episode] shoule be set
            # n_sample=cvalue(32, number() >> positive.int()),
            # (int) Cut trajectories into pieces with length "unroll_len".
            unroll_len=cvalue(1, number() >> positive.int())),
        eval=dict(),
        # other config
        other=dict(
            # Epsilon greedy with decay.
            eps=dict(
                # (str) Decay type. Support ['exp', 'linear'].
                type=cvalue('exp', enum(EpsilonGreedyDecayType)),
                # (float) End value for epsilon decay, in [0, 1]. It's equals to `end` because rainbow uses noisy net.
                start=cvalue(0.05, number() >> interval.LR(0, 1)),
                # (float) End value for epsilon decay, in [0, 1].
                end=cvalue(0.05, number() >> interval.LR(0, 1)),
                # (int) Env steps of epsilon decay.
                decay=cvalue(100000, number() >> positive.int()),
            ),
            replay_buffer=dict(
                # (int) Max size of replay buffer.
                replay_buffer_size=cvalue(100000, number() >> positive.int()),
                # (float) Prioritization exponent.
                alpha=cvalue(0.6, number() >> interval.LR(0, 1)),
                # (float) Importance sample soft coefficient.
                # 0 means no correction, while 1 means full correction
                beta=cvalue(0.4, number() >> interval.LR(0, 1)),
                # (int) Anneal step for beta: 0 means no annealing. Defaults to 0
                anneal_step=cvalue(100000, number() >> is_type(int) >> interval.L(0)),
                cfg_type=cvalue('NaiveReplayBufferDict',
                                enum(ReplayBufferType)),
            )),
    ))

if __name__ == '__main__':
    pprint(config_loader.call({
        'other': {
            'replay_buffer': {
                'cfg_type': 'AdvancedReplayBufferDict'
            },
        },
        'cuda': 'on',
    }), indent=4)
