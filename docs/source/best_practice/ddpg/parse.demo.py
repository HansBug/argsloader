from enum import Enum, unique
from pprint import pprint

from argsloader.units import cdict, cvalue, number, enum, yesno, onoff, positive, interval


@unique
class PolicyType(Enum):
    DDPG = 1

@unique
class ActionSpaceType(Enum):
    CONTINUOUS = 1
    HYBRID = 2

config_loader = cdict(dict(
    # (str) RL policy register name (refer to function "POLICY_REGISTRY").
    type=cvalue('ddpg', enum(PolicyType)),
    # (bool) Whether to use cuda for network.
    cuda=cvalue(False, yesno() | onoff()),
    # (bool type) on_policy: Determine whether on-policy or off-policy.
    # on-policy setting influences the behaviour of buffer.
    # Default False in DDPG.
    on_policy=cvalue(False, yesno()),
    # (bool) Whether use priority(priority sample, IS weight, update priority)
    # Default False in DDPG.
    priority=cvalue(False, yesno()),
    # (bool) Whether use Importance Sampling Weight to correct biased update. If True, priority must be True.
    priority_IS_weight=cvalue(False, yesno()),
    # (int) Number of training samples(randomly collected) in replay buffer when training starts.
    # Default 25000 in DDPG/TD3.
    random_collect_size=cvalue(25000, number() >> positive.int()),
    # (str) Action space type
    action_space=cvalue('continuous', enum(ActionSpaceType)),  # ['continuous', 'hybrid']
    # (bool) Whether use batch normalization for reward
    reward_batch_norm=cvalue(False, yesno()),
    model=dict(
        # (bool) Whether to use two critic networks or only one.
        # Clipped Double Q-Learning for Actor-Critic in original TD3 paper(https://arxiv.org/pdf/1802.09477.pdf).
        # Default True for TD3, False for DDPG.
        twin_critic=cvalue(False, yesno()),
    ),
    learn=dict(
        # (bool) Whether to use multi gpu
        multi_gpu=cvalue(False, yesno()),
        # How many updates(iterations) to train after collector's one collection.
        # Bigger "update_per_collect" means bigger off-policy.
        # collect data -> update policy-> collect data -> ...
        update_per_collect=cvalue(1, number() >> positive.int()),
        # (int) Minibatch size for gradient descent.
        batch_size=cvalue(256, number() >> positive.int()),
        # (float) Learning rates for actor network(aka. policy).
        learning_rate_actor=cvalue(1e-3, number()),
        # (float) Learning rates for critic network(aka. Q-network).
        learning_rate_critic=cvalue(1e-3, number()),
        # (bool) Whether ignore done(usually for max step termination env. e.g. pendulum)
        # Note: Gym wraps the MuJoCo envs by default with TimeLimit environment wrappers.
        # These limit HalfCheetah, and several other MuJoCo envs, to max length of 1000.
        # However, interaction with HalfCheetah always gets done with False,
        # Since we inplace done==True with done==False to keep
        # TD-error accurate computation(``gamma * (1 - done) * next_v + reward``),
        # when the episode step is greater than max episode step.
        ignore_done=cvalue(False, yesno()),
        # (float type) target_theta: Used for soft update of the target network,
        # aka. Interpolation factor in polyak averaging for target networks.
        # Default to 0.005.
        target_theta=cvalue(0.005, number()),
        # (float) discount factor for the discounted sum of rewards, aka. gamma.
        discount_factor=cvalue(0.99, number() >> interval.LR(0, 1)),
        # (int) When critic network updates once, how many times will actor network update.
        # Delayed Policy Updates in original TD3 paper(https://arxiv.org/pdf/1802.09477.pdf).
        # Default 1 for DDPG, 2 for TD3.
        actor_update_freq=cvalue(1, number() >> positive.int()),
        # (bool) Whether to add noise on target network's action.
        # Target Policy Smoothing Regularization in original TD3 paper(https://arxiv.org/pdf/1802.09477.pdf).
        # Default True for TD3, False for DDPG.
        noise=cvalue(False, yesno()),
    ),
    collect=dict(
        # (int) Only one of [n_sample, n_episode] shoule be set
        # n_sample=1,
        # (int) Cut trajectories into pieces with length "unroll_len".
        unroll_len=cvalue(1, number() >> positive.int()),
        # (float) It is a must to add noise during collection. So here omits "noise" and only set "noise_sigma".
        noise_sigma=cvalue(0.1, number()),
    ),
    eval=dict(
        evaluator=dict(
            # (int) Evaluate every "eval_freq" training iterations.
            eval_freq=cvalue(5000, number() >> positive.int()),
        ),
    ),
    other=dict(
        replay_buffer=dict(
            # (int) Maximum size of replay buffer.
            replay_buffer_size=cvalue(100000, number() >> positive.int()),
        ),
    ),
))

if __name__ == '__main__':
    pprint(config_loader.call({
        'learn': {
            'actor_update_freq': 2,
            'discount_factor': 0.95,
        },
        'collect': {
            'unroll_len': 2,
        },
        'cuda': 'on',
    }), indent=4)
