import sys

from winstealer import *
from commons.utils import *
from commons.skills import *
from commons.items import *
from commons.targeting import *
from evade import checkEvade
import json, time, math

winstealer_script_info = {
    "script": "REKO:CASSIO",
    "author": "SUMOREKO",
    "description": "REKO Cassio",
    "target_champ": "cassiopeia",
}

combo_key = 57
harass_key = 45
laneclear_key = 47
killsteal_key = 46

use_q_in_combo = True
use_w_in_combo = True
use_e_in_combo = True
use_r_in_combo = True

lane_clear_with_q = False
lane_clear_with_e = False
lasthit_with_q = False

steal_kill_with_e = False

toggled = False

draw_q_range = False
draw_w_range = False
draw_e_range = False
draw_r_range = False

draw_e_dmg = False

q = {"Range": 850}
w = {"Range": 850}
e = {"Range": 750}
r = {"Range": 825}

spell_priority = {"Q": 0, "W": 0, "E": 0, "R": 0}


def winstealer_load_cfg(cfg):
    global use_q_in_combo, use_w_in_combo, use_e_in_combo, use_r_in_combo
    global draw_w_range, draw_e_range, draw_r_range
    global spell_priority, combo_key, harass_key, laneclear_key, killsteal_key
    global steal_kill_with_e
    global lane_clear_with_e
    combo_key = cfg.get_int("combo_key", 57)
    harass_key = cfg.get_int("harass_key", 45)
    laneclear_key = cfg.get_int("laneclear_key", 47)
    killsteal_key = cfg.get_int("killsteal_key", 46)

    use_q_in_combo = cfg.get_bool("use_q_in_combo", True)
    use_w_in_combo = cfg.get_bool("use_w_in_combo", True)
    use_e_in_combo = cfg.get_bool("use_e_in_combo", True)
    use_r_in_combo = cfg.get_bool("use_r_in_combo", True)

    draw_q_range = cfg.get_bool("draw_q_range", False)
    draw_w_range = cfg.get_bool("draw_w_range", False)
    draw_e_range = cfg.get_bool("draw_e_range", False)
    draw_r_range = cfg.get_bool("draw_r_range", False)

    lane_clear_with_e = cfg.get_bool("lane_clear_with_e", False)
    lane_clear_with_w = cfg.get_bool("lane_clear_with_w", False)

    spell_priority = json.loads(
        cfg.get_str("spell_priority", json.dumps(spell_priority))
    )


def winstealer_save_cfg(cfg):
    global use_q_in_combo, use_w_in_combo, use_e_in_combo, use_r_in_combo
    global draw_w_range, draw_e_range, draw_r_range
    global spell_priority, combo_key, harass_key, laneclear_key, killsteal_key
    global steal_kill_with_e
    global lane_clear_with_e
    cfg.set_int("combo_key", combo_key)
    cfg.set_int("harass_key", harass_key)
    cfg.set_int("laneclear_key", laneclear_key)

    cfg.set_bool("use_q_in_combo", use_q_in_combo)
    cfg.set_bool("use_w_in_combo", use_w_in_combo)
    cfg.set_bool("use_e_in_combo", use_e_in_combo)
    cfg.set_bool("use_r_in_combo", use_r_in_combo)

    cfg.set_bool("draw_w_range", draw_w_range)
    cfg.set_bool("draw_e_range", draw_e_range)
    cfg.set_bool("draw_r_range", draw_r_range)

    cfg.set_bool("lane_clear_with_e", lane_clear_with_e)


def winstealer_draw_settings(game, ui):
    global use_q_in_combo, use_w_in_combo, use_e_in_combo, use_r_in_combo
    global draw_w_range, draw_e_range, draw_r_range
    global spell_priority, combo_key, harass_key, laneclear_key, killsteal_key
    global steal_kill_with_e
    global lane_clear_with_e
    global draw_e_dmg
    ui.begin("REKO:CASSIO")
    combo_key = ui.keyselect("Combo key", combo_key)
    harass_key = ui.keyselect("Harass key", harass_key)
    laneclear_key = ui.keyselect("Laneclear key", laneclear_key)
    killsteal_key = ui.keyselect("Killsteal key", killsteal_key)

    if ui.treenode("Setting [Q]"):
        use_q_in_combo = ui.checkbox("Use Q in Combo", use_q_in_combo)
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
        draw_r_range = ui.checkbox("Draw R Range", draw_r_range)
        ui.treepop()

    if ui.treenode("Laneclear"):
        lane_clear_with_e = ui.checkbox("Laneclear with E", lane_clear_with_e)
        ui.treepop()
    ui.end()


lastQ = 0

mana_q = [50,60,70,80,90]
mana_w = [70,80,90,100,110]
mana_e = [50,48,46,44,42]
mana_r = 100

def GetLowestHPTarget(game, range):
    lowest_target = None
    lowest_hp = 9999

    player = game.player

    for champ in game.champs:
        if (
            champ.is_alive
            and champ.is_visible
            and champ.is_enemy_to(player)
            and game.is_point_on_screen(champ.pos)
            and champ.pos.distance(player.pos) <= range
        ):
            if(champ.health < lowest_hp):
                lowest_hp = champ.health
                lowest_target = champ

    return lowest_target

def GetLowestHPandPoisonTarget(game, range):
    lowest_target = None
    lowest_hp = 9999

    player = game.player

    for champ in game.champs:
        if (
            champ.is_alive
            and champ.is_visible
            and champ.is_enemy_to(player)
            and game.is_point_on_screen(champ.pos)
            and champ.pos.distance(player.pos) <= range
            and champ.buffs
        ):

            qpoison = getBuff(champ, "cassiopeiaqdebuff")
            wpoison = getBuff(champ, "cassiopeiawpoison")

            if(champ.health < lowest_hp) and (qpoison or wpoison):
                lowest_hp = champ.health
                lowest_target = champ

    return lowest_target

def Combo(game):
    global use_q_in_combo, use_w_in_combo, use_e_in_combo, use_r_in_combo
    global draw_e_range, draw_w_range, draw_r_range
    global combo_key, harass_key, laneclear_key
    global lane_clear_with_e
    global q, w, e, r
    global lastQ
    q_spell = getSkill(game, "Q")
    w_spell = getSkill(game, "W")
    e_spell = getSkill(game, "E")
    r_spell = getSkill(game, "R")
    if (
        use_q_in_combo
        and game.player.mana > mana_q[game.player.Q.level-1]
    ):
        target = GetLowestHPTarget(game, q["Range"])
        if target and IsReady(game, q_spell):
            q_spell.move_and_trigger(
                game.world_to_screen(
                    castpoint_for_collision(game, q_spell, game.player, target)
                )
            )

    if (
        use_w_in_combo
        and game.player.mana > mana_w[game.player.W.level-1]
    ):
        target = GetLowestHPTarget(game, w["Range"]-100)
        if target and IsReady(game, w_spell):
            w_spell.move_and_trigger(game.world_to_screen(target.pos))

    if (
        use_e_in_combo
        and game.player.mana > mana_e[game.player.E.level-1]
    ):
        target = GetLowestHPandPoisonTarget(game, e["Range"])
        if target and IsReady(game, e_spell):
            e_spell.move_and_trigger(game.world_to_screen(target.pos))

    if (
        use_r_in_combo
        and game.player.mana > mana_r
    ):
        target = GetLowestHPTarget(game, 600)
        if target and IsReady(game, r_spell):
            r_spell.move_and_trigger(
                game.world_to_screen(
                    castpoint_for_collision(game, r_spell, game.player, target)
                )
            )


def Laneclear(game):
    e_spell = getSkill(game, "E")

def winstealer_update(game, ui):
    global use_q_in_combo, use_w_in_combo, use_w_in_combo, use_r_in_combo
    global draw_q_range, draw_w_range, draw_e_range, draw_r_range
    global q, w, e, r
    global combo_key, laneclear_key, harass_key
    global draw_e_dmg
    self = game.player

    player = game.player

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
