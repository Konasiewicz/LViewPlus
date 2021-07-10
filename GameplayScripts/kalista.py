from winstealer import *
from commons.utils import *
from commons.skills import *
from commons.items import *
from commons.targeting import *
from evade import checkEvade
import json, time, math

winstealer_script_info = {
    "script": "dxzin Kalista",
    "author": "bckd00r",
    "description": "dxzin Kalista",
    "target_champ": "kalista",
}

combo_key = 57
laneclear_key = 47


use_q_in_combo = True
use_w_in_combo = True
use_e_in_combo = True
use_r_in_combo = True


lane_clear_with_e = False


toggled = False

draw_q_range = False
draw_w_range = False
draw_e_range = False
draw_r_range = False

draw_e_dmg = False

q = {"Range": 1150}
w = {"Range": 1400}
e = {"Range": 1100}
r = {"Range": 1200}

spell_priority = {"Q": 0, "W": 0, "E": 0, "R": 0}


def winstealer_load_cfg(cfg):
    global use_q_in_combo, use_w_in_combo, use_e_in_combo, use_r_in_combo
    global draw_w_range, draw_e_range, draw_r_range
    global spell_priority, combo_key, laneclear_key
    global lane_clear_with_e
    global draw_e_dmg
    combo_key = cfg.get_int("combo_key", 57)
    harass_key = cfg.get_int("harass_key", 45)
    laneclear_key = cfg.get_int("laneclear_key", 47)
    killsteal_key = cfg.get_int("killsteal_key", 46)

    use_q_in_combo = cfg.get_bool("use_q_in_combo", True)
    use_w_in_combo = cfg.get_bool("use_w_in_combo", True)
    use_e_in_combo = cfg.get_bool("use_e_in_combo", True)
    use_r_in_combo = cfg.get_bool("use_r_in_combo", True)

    draw_w_range = cfg.get_bool("draw_w_range", False)
    draw_e_range = cfg.get_bool("draw_e_range", False)
    draw_e_dmg = cfg.get_bool("draw_e_dmg", False)
    draw_r_range = cfg.get_bool("draw_r_range", False)

    lane_clear_with_e = cfg.get_bool("lane_clear_with_e", False)
    lane_clear_with_w = cfg.get_bool("lane_clear_with_w", False)

    spell_priority = json.loads(
        cfg.get_str("spell_priority", json.dumps(spell_priority))
    )


def winstealer_save_cfg(cfg):
    global use_q_in_combo, use_w_in_combo, use_e_in_combo, use_r_in_combo
    global draw_w_range, draw_e_range, draw_r_range
    global spell_priority, combo_key, laneclear_key
    global lane_clear_with_e
    global draw_e_dmg
    cfg.set_int("combo_key", combo_key)
    cfg.set_int("laneclear_key", laneclear_key)

    cfg.set_bool("use_q_in_combo", use_q_in_combo)
    cfg.set_bool("use_w_in_combo", use_w_in_combo)
    cfg.set_bool("use_e_in_combo", use_e_in_combo)
    cfg.set_bool("use_r_in_combo", use_r_in_combo)

    cfg.set_bool("draw_q_range", draw_q_range)
    cfg.set_bool("draw_w_range", draw_w_range)
    cfg.set_bool("draw_e_range", draw_e_range)
    cfg.set_bool("draw_e_dmg", draw_e_dmg)
    cfg.set_bool("draw_r_range", draw_r_range)

    cfg.set_bool("lane_clear_with_e", lane_clear_with_e)


def winstealer_draw_settings(game, ui):
    global use_q_in_combo, use_w_in_combo, use_e_in_combo, use_r_in_combo
    global draw_q_range, draw_w_range, draw_e_range, draw_r_range
    global spell_priority, combo_key, laneclear_key
    global lane_clear_with_e
    global draw_e_dmg
    ui.begin("dxzin Kalista")
    combo_key = ui.keyselect("Combo key", combo_key)
    laneclear_key = ui.keyselect("Laneclear key", laneclear_key)

    if ui.treenode("Setting [Q]"):
        use_q_in_combo = ui.checkbox("Use Q in Combo", use_q_in_combo)
        draw_w_range = ui.checkbox("Draw Q Range", draw_q_range)
        ui.treepop()

    if ui.treenode("Setting [W]"):
        use_w_in_combo = ui.checkbox("Use W in Combo", use_w_in_combo)
        draw_w_range = ui.checkbox("Draw W Range", draw_w_range)
        ui.treepop()

    if ui.treenode("Setting [E]"):
        use_e_in_combo = ui.checkbox("Use E in Combo", use_e_in_combo)
        draw_e_range = ui.checkbox("Draw E Range", draw_e_range)
        draw_e_dmg = ui.checkbox("Draw When is Killeable By E DMG", draw_e_dmg)
        ui.treepop()

    if ui.treenode("Setting [R]"):
        use_r_in_combo = ui.checkbox("Use R in Combo", use_r_in_combo)
        draw_r_range = ui.checkbox("Draw R Range", draw_r_range)
        ui.treepop()

    if ui.treenode("Laneclear"):
        lane_clear_with_e = ui.checkbox("Laneclear with E", lane_clear_with_e)
        ui.treepop()
    ui.end()


# (0.15 * (game.player.bonus_atk + game.player.base_atk)

qBaseDamage = [20.0, 85.0, 150.0, 215.0, 280.0]


def QDamage(game, target):
    global qBaseDamage
    resistance_melee = target.armour
    penetration_melee_percent = 0.0  # TODO
    penetration_melee_flat = 0.0  # TODO
    penetration_melee_lethality = 0.0  # TODO

    resistance_magic = target.magic_resist
    penetration_magic_percent = 0.0  # TODO
    penetration_magic_flat = 0.0  # TODO
    penetration_magic_lethality = 0.0  # TODO

    # Lethality calculation
    # penetration_flat += penetration_lethality * (0.6 + 0.4 * source.lvl / 18.0)
    damage_mul_melee = 0.0
    damage_mul_magic = 0.0

    if resistance_melee >= 0.0:
        damage_mul_melee = 100.0 / (100.0 + resistance_melee)
    else:
        damage_mul_melee = 2.0 - 100.0 / (100.0 - resistance_melee)

    if resistance_magic >= 0.0:
        damage_mul_magic = 100.0 / (100.0 + resistance_magic)
    else:
        damage_mul_magic = 2.0 - 100.0 / (100.0 - resistance_magic)

    damage_melee = 0
    damage_magic = 0
    total_atk = game.player.base_atk + game.player.bonus_atk

    damage_melee = qBaseDamage[game.player.Q.level - 1] + (total_atk * 1)

    return (damage_melee * damage_mul_melee) + (damage_magic * damage_mul_magic)


eBaseDamage = [20.0, 30.0, 40.0, 50.0, 60.0]
eStackDamage = [10.0, 16.0, 22.0, 28.0, 34.0]
eStackPercent = [0.2, 0.2375, 0.275, 0.3125, 0.35]


def EDamage(game, target):
    global eBaseDamage

    # Calculate resistance
    resistance_melee = target.armour
    penetration_melee_percent = 0.0  # TODO
    penetration_melee_flat = 0.0  # TODO
    penetration_melee_lethality = 0.0  # TODO

    resistance_magic = target.magic_resist
    penetration_magic_percent = 0.0  # TODO
    penetration_magic_flat = 0.0  # TODO
    penetration_magic_lethality = 0.0  # TODO

    # Lethality calculation
    # penetration_flat += penetration_lethality * (0.6 + 0.4 * source.lvl / 18.0)
    damage_mul_melee = 0.0
    damage_mul_magic = 0.0

    if resistance_melee >= 0.0:
        damage_mul_melee = 100.0 / (100.0 + resistance_melee)
    else:
        damage_mul_melee = 2.0 - 100.0 / (100.0 - resistance_melee)

    if resistance_magic >= 0.0:
        damage_mul_magic = 100.0 / (100.0 + resistance_magic)
    else:
        damage_mul_magic = 2.0 - 100.0 / (100.0 - resistance_magic)

    ecount = 0
    if getBuff(target, "kalistaexpungemarker"):
        ecount = getBuff(target, "kalistaexpungemarker").countAlt - 1
    else:
        count = -1

    damage_melee = 0
    damage_magic = 0
    if ecount >= 0:
        total_atk = game.player.base_atk + game.player.bonus_atk
        damage_melee = eBaseDamage[game.player.E.level - 1] + (total_atk * 0.6)
        damage_melee += (
            eStackDamage[game.player.E.level - 1]
            + ((total_atk) * eStackPercent[game.player.E.level - 1])
        ) * ecount
    return (damage_melee * damage_mul_melee) + (damage_magic * damage_mul_magic)


def DrawEDMG(game, player):
    color = Color.GREEN
    player = game.player
    for champ in game.champs:
        if (
            champ.is_alive
            and champ.is_visible
            and champ.is_enemy_to(player)
            and game.is_point_on_screen(champ.pos)
        ):
            if EDamage(game, champ) >= champ.health:
                p = game.hp_bar_pos(champ)
                color.a = 5.0
                game.draw_rect(
                    Vec4(p.x - 47, p.y - 27, p.x + 61, p.y - 12), color, 0, 2
                )


lastQ = 0


def Combo(game):
    global use_q_in_combo, use_w_in_combo, use_e_in_combo, use_r_in_combo
    global draw_q_range, draw_e_range, draw_w_range, draw_r_range
    global combo_key, laneclear_key
    global lane_clear_with_e
    global q, w, e, r
    global lastQ
    q_spell = getSkill(game, "Q")
    w_spell = getSkill(game, "W")
    e_spell = getSkill(game, "E")
    r_spell = getSkill(game, "R")
    if (
        use_q_in_combo
        and game.player.mana > 120 + 40 + 40
        and IsReady(game, q_spell)
        and lastQ + 2 < game.time
    ):
        target = GetBestTargetsInRange(game, q["Range"])
        if target and not IsCollisioned(game, target):
            lastQ = game.time
            if target.isMoving:
                q_spell.move_and_trigger(
                    game.world_to_screen(
                        castpoint_for_collision(game, q_spell, game.player, target)
                    )
                )
            else:
                q_spell.move_and_trigger(
                    game.world_to_screen(
                        castpoint_for_collision(game, q_spell, game.player, target)
                    )
                )

    if use_e_in_combo and IsReady(game, e_spell) and game.player.mana > 30:
        target = GetBestTargetsInRange(game, 1100)
        if target and getBuff(target, "kalistaexpungemarker"):
            if EDamage(game, target) >= target.health:
                e_spell.trigger(False)


def Laneclear(game):
    e_spell = getSkill(game, "E")
    if lane_clear_with_e and IsReady(
        game, e_spell
    ):  # and getBuff(game.player, "TwitchDeadlyVenom")
        target = GetBestJungleInRange(game) or GetBestMinionsInRange(game)
        if target and getBuff(target, "kalistaexpungemarker"):
            if EDamage(game, target) >= target.health:
                e_spell.trigger(False)


def winstealer_update(game, ui):
    global use_q_in_combo, use_w_in_combo, use_w_in_combo, use_r_in_combo
    global draw_q_range, draw_w_range, draw_e_range, draw_r_range
    global q, w, e, r
    global combo_key, laneclear_key, harass_key
    global draw_e_dmg
    self = game.player

    player = game.player

    if draw_e_dmg:
        DrawEDMG(game, player)

    if draw_q_range:
        game.draw_circle_world(game.player.pos, q["Range"], 100, 1, Color.WHITE)
    if draw_w_range:
        game.draw_circle_world(game.player.pos, w["Range"], 100, 1, Color.WHITE)
    if draw_e_range:
        game.draw_circle_world(game.player.pos, e["Range"], 100, 1, Color.WHITE)
    if draw_r_range:
        game.draw_circle_world(game.player.pos, r["Range"], 100, 1, Color.WHITE)

    if self.is_alive and not game.isChatOpen and not checkEvade():
        if game.was_key_pressed(combo_key):
            Combo(game)
        if game.was_key_pressed(laneclear_key):
            Laneclear(game)
