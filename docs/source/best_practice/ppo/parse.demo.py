from enum import Enum, unique
from pprint import pprint

from argsloader.units import cdict, enum, cvalue, yesno, number, onoff, positive, interval, optional


@unique
class PolicyType(Enum):
    PPO = 1


@unique
class ActionSpaceType(Enum):
    DISCRETE = 1
    CONTINUOUS = 2
    HYBRID = 3


@unique
class GradClipType(Enum):
    NONE = 1
    CLIP_MOMENTUM = 2
    CLIP_VALUE = 3
    CLIP_NORM = 4
    CLIP_MOMENTUM_NORM = 5


config_loader = cdict(dict(
    # (str) RL policy register name (refer to function "POLICY_REGISTRY").
    type=cvalue('ppo', enum(PolicyType)),
    # (bool) Whether to use cuda for network.
    cuda=cvalue(False, yesno() | onoff()),
    # (bool) Whether the RL algorithm is on-policy or off-policy. (Note: in practice PPO can be off-policy used)
    on_policy=cvalue(True, yesno()),
    # (bool) Whether to use priority(priority sample, IS weight, update priority)
    priority=cvalue(False, yesno()),
    # (bool) Whether to use Importance Sampling Weight to correct biased update due to priority.
    # If True, priority must be True.
    priority_IS_weight=cvalue(False, yesno()),
    # (bool) Whether to recompurete advantages in each iteration of on-policy PPO
    recompute_adv=cvalue(True, yesno()),
    # (str) Which kind of action space used in PPOPolicy, ['discrete', 'continuous', 'hybrid']
    action_space=cvalue('discrete', enum(ActionSpaceType)),
    # (bool) Whether to use nstep return to calculate value target, otherwise, use return = adv + value
    nstep_return=cvalue(False, yesno()),
    # (bool) Whether to enable multi-agent training, i.e.: MAPPO
    multi_agent=cvalue(False, yesno()),
    # (bool) Whether to need policy data in process transition
    transition_with_policy_data=cvalue(True, yesno()),
    learn=dict(
        # (bool) Whether to use multi gpu
        multi_gpu=cvalue(False, yesno()),
        epoch_per_collect=cvalue(10, number() >> positive.int()),
        batch_size=cvalue(64, number() >> positive.int()),
        learning_rate=cvalue(3e-4, number()),
        # ==============================================================
        # The following configs is algorithm-specific
        # ==============================================================
        # (float) The loss weight of value network, policy network weight is set to 1
        value_weight=cvalue(0.5, number()),
        # (float) The loss weight of entropy regularization, policy network weight is set to 1
        entropy_weight=cvalue(0.0, number()),
        # (float) PPO clip ratio, defaults to 0.2
        clip_ratio=cvalue(0.2, number() >> interval.LR(0, 1)),
        # (bool) Whether to use advantage norm in a whole training batch
        adv_norm=cvalue(True, yesno()),
        value_norm=cvalue(True, yesno()),
        ppo_param_init=cvalue(True, yesno()),
        grad_clip_type=cvalue('clip_norm', optional(enum(GradClipType))),
        grad_clip_value=cvalue(0.5, number()),
        ignore_done=cvalue(False, yesno()),
    ),
    collect=dict(
        # (int) Only one of [n_sample, n_episode] shoule be set
        n_sample=cvalue(64, number() >> positive.int()),
        # (int) Cut trajectories into pieces with length "unroll_len".
        unroll_len=cvalue(1, number() >> positive.int()),
        # ==============================================================
        # The following configs is algorithm-specific
        # ==============================================================
        # (float) Reward's future discount factor, aka. gamma.
        discount_factor=cvalue(0.99, number() >> interval.LR(0, 1)),
        # (float) GAE lambda factor for the balance of bias and variance(1-step td and mc)
        gae_lambda=cvalue(0.95, number() >> interval.LR(0, 1)),
    ),
    eval=dict(),
))

if __name__ == '__main__':
    pprint(config_loader.call({
        'learn': {
            'grad_clip_type': 'clip_value',
        },
        'collect': {
            'n_sample': 320,
            'unroll_len': 1,
            'discount_factor': 0.95,
        },
        'cuda': 'on',
    }), indent=4)
