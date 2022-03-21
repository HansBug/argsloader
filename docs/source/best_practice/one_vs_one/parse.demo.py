from enum import unique, Enum, Flag
from pprint import pprint

from hbutils.reflection import quick_import_object

from argsloader.units import cdict, enum, cvalue, number, nature, yesno, mapping, is_type, getitem_


@unique
class LeagueType(Enum):
    ONE_VS_ONE = 1


@unique
class PlayerCategory(Flag):
    DEFAULT = 0
    ZERG = 1 << 0
    TERRAN = 1 << 1
    PROTOSS = 1 << 2


@unique
class PayoffType(Enum):
    BATTLE = 1


config_loader = cdict(dict(
    league_type=cvalue('one_vs_one', enum(LeagueType)),
    import_names=cvalue(
        ["pprint.pprint", 'json.loads', 'argsloader.units'],
        mapping(is_type(str) >> quick_import_object >> getitem_(0, offset=False)),
    ),
    # ---player----
    # "player_category" is just a name. Depends on the env.
    # For example, in StarCraft, this can be ['zerg', 'terran', 'protoss'].
    player_category=cvalue(['default'], enum(PlayerCategory)),
    # Support different types of active players for solo and battle league.
    # For solo league, supports ['solo_active_player'].
    # For battle league, supports ['battle_active_player', 'main_player', 'main_exploiter', 'league_exploiter'].
    active_players=dict(
        naive_sp_player=cvalue(1, number() >> nature()),  # {player_type: player_num}
    ),
    naive_sp_player=dict(
        # There should be keys ['one_phase_step', 'branch_probs', 'strong_win_rate'].
        # Specifically for 'main_exploiter' of StarCraft, there should be an additional key ['min_valid_win_rate'].
        one_phase_step=cvalue(10, number() >> nature()),
        branch_probs=dict(
            pfsp=cvalue(0.5, number()),
            sp=cvalue(0.5, number()),
        ),
        strong_win_rate=cvalue(0.7, number()),
    ),
    # "use_pretrain" means whether to use pretrain model to initialize active player.
    use_pretrain=cvalue(False, yesno()),
    # "use_pretrain_init_historical" means whether to use pretrain model to initialize historical player.
    # "pretrain_checkpoint_path" is the pretrain checkpoint path used in "use_pretrain" and
    # "use_pretrain_init_historical". If both are False, "pretrain_checkpoint_path" can be omitted as well.
    # Otherwise, "pretrain_checkpoint_path" should list paths of all player categories.
    use_pretrain_init_historical=cvalue(False, yesno()),
    pretrain_checkpoint_path=dict(
        default='default_cate_pretrain.pth',  # file parser is required.
    ),
    # ---payoff---
    payoff=dict(
        # Supports ['battle']
        type=cvalue('battle', enum(PayoffType)),
        decay=cvalue(0.99, number()),
        min_win_rate_games=cvalue(8, number()),
    ),
    metric=dict(
        mu=cvalue(0, number()),
        sigma=cvalue(25 / 3, number()),
        beta=cvalue(25 / 3 / 2, number()),
        tau=cvalue(0.0, number()),
        draw_probability=cvalue(0.02, number()),
    ),
))

if __name__ == '__main__':
    pprint(config_loader.call({
        'player_category': ['zerg', 'protoss'],
        'use_pretrain': 'yes',
    }), indent=4)
