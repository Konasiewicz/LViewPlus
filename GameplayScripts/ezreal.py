from winstealer import *

import orb_walker
from commons.utils import *
from commons.skills import *
from commons.items import *
from commons.targeting import *
from evade import checkEvade
from orb_walker import *
import json, time, math

winstealer_script_info = {
    "script": "REKO:Ezreal",
    "author": "SUMOREKO",
    "description": "SUMOREKO Ezreal",
    "target_champ": "ezreal",
}

Q = {"Slot":"Q","Range":1180}
W = {"Slot":"W","Range":1180}
E = {"Slot":"E","Range":475}
R = {"Slot":"R","Range":2500}

combo_key = 57
harass_key = 45
laneclear_key = 47
ks_key = 20

Qcombo = True
QinAA = True
Qharass = True

draw_q_range = True

def GetClosestTarget(game, range):
    lowest_target = None
    lowest_dist = 9999

    player = game.player

    for champ in game.champs:
        if (
            champ.is_alive
            and champ.is_visible
            and champ.is_enemy_to(player)
            and game.is_point_on_screen(champ.pos)
            and champ.pos.distance(player.pos) <= range
            and not checkEvade()
        ):
            if(champ.health < lowest_dist):
                lowest_dist = champ.pos.distance(player.pos)
                lowest_target = champ

    return lowest_target

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
            and not checkEvade()
        ):
            if(champ.health < lowest_hp):
                lowest_hp = champ.health
                lowest_target = champ

    return lowest_target


TargetingAlgorithm = GetLowestHPTarget

def QLogic(game):

    q_spell = getSkill(game, "Q")

    for target in game.champs:
        if (
            target
            and target.is_visible
            and target.is_enemy_to(game.player)
            and target.is_alive
            and game.is_point_on_screen(target.pos)
            and not orb_walker.onAttack
        ):
            target = TargetingAlgorithm(game, q_spell.cast_range)
            if target and IsReady(game, q_spell) and not IsCollisioned(game, target):
                q_spell.move_and_trigger(
                    game.world_to_screen(
                        castpoint_for_collision(game, q_spell, game.player, target)
                    )
                )

def WLogic(game):
    w_spell = getSkill(game, "W")

    for target in game.champs:
        if (
                target
                and target.is_visible
                and target.is_enemy_to(game.player)
                and target.is_alive
                and game.is_point_on_screen(target.pos)
                and not orb_walker.onAttack
        ):
            target = TargetingAlgorithm(game, w_spell.cast_range)
            if target and IsReady(game, w_spell):
                w_spell.move_and_trigger(
                    game.world_to_screen(
                        castpoint_for_collision(game, w_spell, game.player, target)
                    )
                )

def winstealer_update(game, ui):

    q_spell = getSkill(game, "Q")
    w_spell = getSkill(game, "W")
    e_spell = getSkill(game, "E")
    r_spell = getSkill(game, "R")

    global use_q_in_combo, use_w_in_combo, use_w_in_combo, use_r_in_combo
    global draw_q_range, draw_w_range, draw_e_range, draw_r_range
    global q, w, e, r
    global combo_key, laneclear_key, harass_key
    global draw_e_dmg

    #if draw_q_range:
    game.draw_circle_world(game.player.pos, Q["Range"], 100, 1, Color.RED)

    if game.player.is_alive and not game.isChatOpen and not checkEvade():
        if game.was_key_pressed(combo_key):
            WLogic(game)
            QLogic(game)