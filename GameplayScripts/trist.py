from winstealer import *
from commons.utils import *
from commons.skills import *
from commons.items import *
from commons.targeting import *
from evade import checkEvade
import json, time, math

winstealer_script_info = {
    "script": "WS+ tristana",
    "author": "bckd00r",
    "description": "WS+ tristana",
    "target_champ": "tristana",
}
combo_key = 57
lasthit_key = 45


laneclear_key = 47

## Combo
use_q_in_combo = True
use_w_in_combo = True
use_e_in_combo = True
use_r_in_combo = True

# Evade

use_e_on_evade = True


# Laneclear
lane_clear_with_q = True

# Drawings
draw_q_range = True
draw_w_range = True
draw_e_range = True
draw_r_range = False

q = {"Range": 1000}
w = {"Range": 1000}
e = {"Range": 750}
r = {"Range": 10000}


def winstealer_load_cfg(cfg):
    global key_orbwalk, lasthit_key, harass_key, laneclear_key
    global use_q_in_combo, use_w_in_combo, use_e_in_combo, use_r_in_combo
    global use_e_on_evade
    global lane_clear_with_q
    global draw_q_range, draw_w_range, draw_e_range, draw_r_range

    lasthit_key = cfg.get_int("lasthit_key", 46)
    combo_key = cfg.get_int("combo_key", 57)
    laneclear_key = cfg.get_int("laneclear_key", 47)

    use_q_in_combo = cfg.get_bool("use_q_in_combo", True)
    use_w_in_combo = cfg.get_bool("use_w_in_combo", True)

    use_r_in_combo = cfg.get_bool("use_r_in_combo", True)

    ## Evade

    use_e_on_evade = cfg.get_bool("use_e_on_evade", True)

    ## Laneclear
    lane_clear_with_q = cfg.get_bool("lane_clear_with_q", True)

    ## Drawings
    draw_q_range = cfg.get_bool("draw_q_range", False)
    draw_w_range = cfg.get_bool("draw_w_range", False)
    draw_e_range = cfg.get_bool("draw_e_range", False)
    draw_r_range = cfg.get_bool("draw_r_range", False)


def winstealer_save_cfg(cfg):
    global key_orbwalk, lasthit_key, harass_key, laneclear_key
    global use_q_in_combo, use_w_in_combo, use_r_in_combo
    global use_e_on_evade

    global lane_clear_with_q

    ## Keys
    cfg.set_int("lasthit_key", lasthit_key)
    cfg.set_int("combo_key", combo_key)
    cfg.set_int("laneclear_key", laneclear_key)

    ## Combo
    cfg.set_bool("use_q_in_combo", use_q_in_combo)
    cfg.set_bool("use_w_in_combo", use_w_in_combo)

    cfg.set_bool("use_r_in_combo", use_r_in_combo)

    ## Evade

    cfg.set_bool("use_e_on_evade", use_e_on_evade)

    ## KS

    ## Laneclear
    cfg.set_bool("lane_clear_with_q", lane_clear_with_q)

    ## Drawings
    cfg.set_bool("draw_q_range", draw_q_range)
    cfg.set_bool("draw_w_range", draw_e_range)
    cfg.set_bool("draw_e_range", draw_w_range)
    cfg.set_bool("draw_r_range", draw_r_range)


def winstealer_draw_settings(game, ui):
    global use_q_in_combo, use_w_in_combo, use_e_in_combo, use_r_in_combo
    global draw_q_range, draw_w_range, draw_e_range, draw_r_range
    global combo_key, lasthit_key, laneclear_key
    global steal_kill_with_q, steal_kill_with_w, steal_kill_with_e, steal_kill_with_r
    global lane_clear_with_q

    ui.begin("WS+ tristana")
    combo_key = ui.keyselect("Combo key", combo_key)

    laneclear_key = ui.keyselect("Laneclear key", laneclear_key)
    lasthit_key = ui.keyselect("Lasthit key", lasthit_key)
    if ui.treenode("Setting [Q]"):
        use_q_in_combo = ui.checkbox("Use Q in Combo", use_q_in_combo)

        draw_q_range = ui.checkbox("Draw Q Range", draw_q_range)
        ui.treepop()

    if ui.treenode("Setting [W]"):
        use_w_in_combo = ui.checkbox("Use W in Combo", use_w_in_combo)
        draw_w_range = ui.checkbox("Draw W Range", draw_w_range)
        ui.treepop()

    if ui.treenode("Setting [E]"):
        use_e_in_combo = ui.checkbox("Use E in Combo", use_e_in_combo)

        draw_e_range = ui.checkbox("Draw E Range", draw_e_range)
        ui.treepop()

    if ui.treenode("Setting [R]"):
        use_r_in_combo = ui.checkbox("Use R in Combo", use_r_in_combo)
        ui.treepop()

    if ui.treenode("Laneclear"):
        lane_clear_with_q = ui.checkbox("Laneclear with Q", lane_clear_with_q)
        ui.treepop()
    ui.end()


def Combo(game):
    global q, w, e, r
    q_spell = getSkill(game, "Q")
    w_spell = getSkill(game, "W")
    e_spell = getSkill(game, "E")
    r_spell = getSkill(game, "R")

    if use_q_in_combo and IsReady(game, q_spell) and q_spell.name == "tristana":
        target = GetBestTargetsInRange(game, 1000)
        if target and ValidTarget(target):
            q_spell.move_and_trigger(
                game.world_to_screen(
                    castpoint_for_collision(game, q_spell, game.player, target)
                )
            )
    if use_q_in_combo and IsReady(game, q_spell):
        target = GetBestTargetsInRange(game, q["Range"])
        if target and ValidTarget(target):
            q_spell.move_and_trigger(game.world_to_screen(target.pos))
    if use_w_in_combo and IsReady(game, w_spell):
        target = GetBestTargetsInRange(game, w["Range"])
        if target and ValidTarget(target):
            w_spell.move_and_trigger(game.world_to_screen(target.pos))
    if (
        use_e_in_combo
        and e_spell
        and IsReady(game, e_spell)
        and q_spell
        and IsReady(game, q_spell)
        and q_spell.name == "tristana"
    ):
        target = GetBestTargetsInRange(game, e["Range"])
        if target and ValidTarget(target):
            e_spell.move_and_trigger(game.world_to_screen(target.pos))
            q_spell.move_and_trigger(game.world_to_screen(target.pos))
    if use_r_in_combo and IsReady(game, r_spell):
        target = GetBestTargetsInRange(game, r["Range"])
        if target:
            if RDamage(game, target) > target.health:
                if target.isMoving:
                    r_spell.move_and_trigger(
                        game.world_to_screen(
                            castpoint_for_collision(game, r_spell, game.player, target)
                        )
                    )
                else:
                    r_spell.move_and_trigger(game.world_to_screen(target.pos))


def Laneclear(game):
    q_spell = getSkill(game, "Q")
    if lane_clear_with_q and IsReady(game, q_spell):
        minion = GetBestMinionsInRange(game, q["Range"])
        if minion and is_last_hitable(game, game.player, minion):
            q_spell.move_and_trigger(game.world_to_screen(minion.pos))
    if lane_clear_with_q and IsReady(game, q_spell):
        minion = GetBestMinionsInRange(game, q["Range"]) or GetBestJungleInRange(
            game, q["Range"]
        )
        if ValidTarget(minion) and minion:
            q_spell.move_and_trigger(game.world_to_screen(minion.pos))


def winstealer_update(game, ui):
    global use_q_in_combo, use_w_in_combo, use_e_in_combo, use_r_in_combo
    global draw_q_range, draw_w_range, draw_e_range, draw_r_range
    global combo_key, harass_key, killsteal_key, laneclear_key
    global steal_kill_with_q, steal_kill_with_w, steal_kill_with_e, steal_kill_with_r

    self = game.player

    if draw_q_range:
        game.draw_circle_world(game.player.pos, q["Range"], 100, 1, Color.WHITE)
    if draw_w_range:
        game.draw_circle_world(game.player.pos, w["Range"], 100, 1, Color.WHITE)
    # if draw_e_range:
    #     game.draw_circle_world(game.player.pos, e["Range"], 100, 2, Color.WHITE)
    if draw_r_range:
        game.draw_circle_world(game.player.pos, r["Range"], 100, 1, Color.WHITE)

    if self.is_alive and not checkEvade() and not game.isChatOpen and self.isTargetable:
        if game.is_key_down(combo_key):
            Combo(game)
        if game.is_key_down(laneclear_key):
            Laneclear(game)
