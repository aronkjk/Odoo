# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
from datetime import datetime, timedelta
import random
import math
import json

class region_space(models.Model):
    _name = 'proves.region_space'
    name = fields.Char(required=True)
    image = fields.Binary()

    @api.depends('image')
    def _get_images(self):
        for i in self:
            image = i.image
            data = tools.image_get_resized_images(image)
            i.image_small = data["image_small"]

class player(models.Model):
    _name = 'proves.player'
    name = fields.Char(required=True)
    image = fields.Binary()
    image_small = fields.Binary(string='Image', compute='_get_images', store=True)

    prestige = fields.Selection([('0', 'Very Low'), ('1', 'Low'), ('2', 'Normal Low'),
                            ('3', 'Normal'), ('4', 'Normal High'), ('5', 'High'),
                            ('6', 'Very High')], computed='_set_prestige')

    worlds_owner = fields.One2many('proves.world', 'owner')
    worlds_owners = fields.One2many(related='worlds_owner')

    belongs_aliance = fields.Many2one('proves.aliance')

    events = fields.Many2many('proves.event')

    @api.multi
    def _create_player(self):
        prestige ='1'

    @api.depends()
    def _set_prestige(self):
        for i in self:
            i.prestige='1'

    @api.depends('image')
    def _get_images(self):
        for i in self:
           image = i.image
           data = tools.image_get_resized_images(image)
           i.image_small = data["image_small"]

    @api.multi
    def create_new_world(self):
        names = ["Zagu", "Bonki", "Britya", "Rambiksh", "Dushakh", "Gurbag", "Caltxa", "Shibelna",
                 "Saide", "Lakshi", "Ayoth", "Gharn", "Krishuru", "Throg", "Dushuum",
                 "Krishgal", "Galda", "Kuquilu", "Kitara", "Margora", "Visenuky", "Prasha", "Ardeva",
                 "Gulgexo", "Golugrog", "Grith", "Zaisty", "Beera", "Adimha", "Krutundu"]

        for p in self:
            w_image = self.env.ref('proves.world'+str(random.randint(1,7)))
            bkg_image = self.env.ref('proves.background_kanban_planet')

            w = self.env['proves.world'].create({
                'name': 'Default Planet'+str(random.randint(1,600)),
                'image': w_image.image,
                'template': False,
                'lvl': 1,
                'owner': p.id,
                'image_background': bkg_image,
                })
            ps = self.env['power_station.structure'].create({
                'name': 'Default Power Station'+str(random.randint(1,600)),
                'completed': False,
                'perc_complete': 0,
                'lvl': 1,
                'built_in': w.id,
                'kanban_state':'start',
            })
            n = self.env['nursery.structure'].create({
                'name': 'Default Nursery'+str(random.randint(1,600)),
                'completed': False,
                'perc_complete': 0,
                'lvl': 1,
                'built_in': w.id,
            })

            for i in range(random.randint(1,7)):
                a = self.env['proves.citizen'].create({
                    'name': str(random.choice(names)),
                    'inteligence': str(random.randint(1, 7)),
                    'force': str(random.randint(1, 7)),
                    'ability': str(random.randint(1, 7)),
                    'inhabiting': w.id,
                })


class aliance(models.Model):
    _name = 'proves.aliance'
    name = fields.Char(required=True)
    participants =  fields.One2many('proves.player', 'belongs_aliance')

    image = fields.Binary()
    image_small = fields.Binary(string='Image', compute='_get_images', store=True)

    @api.depends('image')
    def _get_images(self):
        for i in self:
           image = i.image
           data = tools.image_get_resized_images(image)
           i.image_small = data["image_small"]


class world(models.Model):
    _name = 'proves.world'
    name = fields.Char()
    image = fields.Binary()
    image_small = fields.Binary(string='Image', compute='_get_images', store=True)
    image_background = fields.Binary()
    lvl = fields.Integer()
    template = fields.Boolean()
    space_pos = fields.Integer(compute='_get_pos')

    attacker = fields.One2many('proves.battle', 'attack')
    defender = fields.One2many('proves.battle', 'defend')

    player_attacker = fields.One2many('proves.battle', 'attacker')
    player_defender = fields.One2many('proves.battle', 'defender')

    tiles = fields.Integer(default=30)
    free_tiles = fields.Integer(compute='_free_tiles')
    structures = fields.Integer(compute='_get_structures')

    num_nur = fields.Integer(compute='_get_structures')
    births_xm = fields.Integer(compute='_get_structures')
    population = fields.Integer(compute='_get_structures')
    max_population = fields.Integer(compute='_get_structures')
    perc_population = fields.Integer(compute='_get_structures')

    num_ps = fields.Integer(compute='_get_structures')
    energy_xm = fields.Integer(compute='_get_structures')
    total_energy = fields.Integer(compute='_get_structures')
    max_energy = fields.Integer(compute='_get_structures')
    perc_energy = fields.Integer(compute='_get_structures')

    num_at = fields.Integer(compute='_get_structures')
    power_attack_xm = fields.Integer(compute='_get_structures')
    power_attack = fields.Integer(compute='_get_structures')
    max_power_attack = fields.Integer(compute='_get_structures')
    perc_power_attack = fields.Integer(compute='_get_structures')

    num_dd = fields.Integer(compute='_get_structures')
    power_defense_xm = fields.Integer(compute='_get_structures')
    power_defense = fields.Integer(compute='_get_structures')
    max_power_defense = fields.Integer(compute='_get_structures')
    perc_power_defense = fields.Integer(compute='_get_structures')

    owner = fields.Many2one('proves.player', ondelete='cascade')

    power_stations = fields.One2many('power_station.structure', 'built_in')
    nursery = fields.One2many('nursery.structure', 'built_in')
    attack_towers = fields.One2many('attack_tower.structure', 'built_in')
    defense_dome = fields.One2many('defense_dome.structure', 'built_in')
    residents = fields.One2many('proves.citizen', 'inhabiting')

    @api.depends()
    def _free_tiles(self):
        for w in self:
            w.free_tiles = w.tiles - w.structures

    @api.depends()
    def _get_structures(self):
        for w in self:

            for r in w.residents:
                w.population += 1

            for ps in w.power_stations:
                w.num_ps += 1
                w.structures += 1
                w.energy_xm += ps.energy_xm
                w.max_energy += ps.max_energy
                w.total_energy += ps.energy

            for n in w.nursery:
                w.num_nur += 1
                w.structures += 1
                w.births_xm += n.births_xm
                w.max_population += n.capacity

            for at in w.attack_towers:
                w.num_at += 1
                w.structures += 1
                w.power_attack_xm += at.damage_xm
                w.power_attack += at.damage
                w.max_power_attack += at.max_damage

            for dd in w.defense_dome:
                w.num_dd += 1
                w.structures += 1
                w.power_defense_xm += dd.buckler_xm
                w.max_power_defense += dd.max_buckler
                w.power_defense += dd.buckler

            if w.max_population > 0:
                w.perc_population = w.population * 100 / w.max_population
                if w.population > 0: w.perc_population -= 1
            if w.max_energy > 0:
                w.perc_energy = w.total_energy * 100 / w.max_energy
                if w.total_energy > 0: w.perc_energy -= 1
            if w.max_power_attack > 0:
                w.perc_power_attack = w.power_attack * 100 / w.max_power_attack
                if w.power_attack > 0: w.perc_power_attack -= 1
            if w.max_power_defense > 0:
                w.perc_power_defense = w.power_defense * 100 / w.max_power_defense
                if w.power_defense > 0: w.perc_power_defense -= 1

    @api.multi
    def create_resources(self):

        names = ["Zagu", "Bonki", "Britya", "Rambiksh", "Dushakh", "Gurbag", "Caltxa", "Shibelna",
                 "Saide", "Lakshi", "Ayoth", "Gharn", "Krishuru", "Throg", "Dushuum",
                 "Krishgal", "Galda", "Kuquilu", "Kitara", "Margora", "Visenuky", "Prasha", "Ardeva",
                 "Gulgexo", "Golugrog", "Grith", "Zaisty", "Beera", "Adimha", "Krutundu"]

        for w in self:

            #Battales
            for b in w.defender:
                if b.finished == False:
                    b.compute_battle()

            #Evaluar nivels i fer produccio
            for ps in w.power_stations:
                if ps.completed:
                    if ps.lvl == 2:
                        ps.energy_xm = 7
                        ps.max_energy = 175
                    if ps.lvl == 3:
                        ps.energy_xm = 10
                        ps.max_energy = 300
                    if ps.lvl == 4:
                        ps.energy_xm = 15
                        ps.max_energy = 600

                    total_wk = 0
                    for wk in ps.workers:
                        total_wk += 1

                        ps.energy_xm = ps.energy + wk.inteligence / 2
                        ps.energy_xm = ps.energy + wk.force / 3
                        ps.energy_xm = ps.energy + wk.hability / 6

                    if total_wk == 0:
                        ps.kanban_state = 'blocked'
                    else:
                        ps.kanban_state = 'producing'

                    if ps.energy < ps.max_energy:
                        ps.energy += ps.energy_xm
                else:
                    ps.perc_complete += 3.5
                    if ps.perc_complete >= 100:
                        ps.completed = True
                        ps.kanban_state = 'blocked'

            for n in w.nursery:
                if n.completed:
                    if n.lvl == 2:
                        n.births_xm = 8
                        n.capacity = 80
                    if n.lvl == 3:
                        n.births_xm = 16
                        n.capacity = 160
                    if n.lvl == 4:
                        n.births_xm = 32
                        n.capacity = 320

                    total_wk = 0
                    for wk in n.workers:
                        total_wk = sum(wk)

                        n.births_xm = n.births_xm + wk.inteligence / 6
                        n.births_xm = n.births_xm + wk.force / 3
                        n.births_xm = n.births_xm + wk.hability / 2

                    if total_wk == 0:
                        n.kanban_state = 'blocked'
                    else:
                        n.kanban_state = 'producing'

                    if w.population < w.max_population:
                        for b in range(n.births_xm):
                            a = self.env['proves.citizen'].create({
                                'name' :  str(random.choice(names)),
                                'inteligence' : str(random.randint(1,7)),
                                'force' : str(random.randint(1,7)),
                                'ability' : str(random.randint(1,7)),
                                'inhabiting' : w.id,
                            })
                else:
                    n.perc_complete += 3.5
                    if n.perc_complete >= 100:
                        n.completed = True
                        n.kanban_state = 'blocked'

            for at in w.attack_towers:
                if at.completed:
                    if at.lvl == 2:
                        at.damage_xm = 8
                        at.max_damage = 600
                    if at.lvl == 3:
                        at.births_xm = 16
                        at.max_damage = 800
                    if at.lvl == 4:
                        at.births_xm = 50
                        at.max_damage = 1500

                    total_wk = 0
                    for wk in at.workers:
                        total_wk = sum(wk)

                        at.damage_xm = at.damage_xm + wk.inteligence / 2
                        at.damage_xm = at.damage_xm + wk.force / 3
                        at.damage_xm = at.damage_xm + wk.hability / 3

                    if total_wk == 0:
                        at.kanban_state = 'blocked'
                    else:
                        at.kanban_state = 'producing'

                    if at.damage < at.max_damage:
                        at.damage += at.damage_xm
                else:
                    at.perc_complete += 3.5
                    if at.perc_complete >= 100:
                        at.completed = True
                        at.kanban_state = 'blocked'

            for dd in w.defense_dome:
                if dd.completed:
                    if dd.lvl == 2:
                        dd.buckler_xm = 8
                        dd.max_buckler = 600
                    if dd.lvl == 3:
                        dd.buckler_xm = 16
                        dd.max_buckler = 800
                    if dd.lvl == 4:
                        dd.buckler_xm = 50
                        dd.max_buckler = 1500

                    total_wk = 0
                    for wk in dd.workers:
                        total_wk = sum(wk)

                        dd.buckler_xm = dd.buckler_xm + wk.inteligence / 6
                        dd.buckler_xm = dd.buckler_xm + wk.force / 2
                        dd.buckler_xm = dd.buckler_xm + wk.hability / 2

                    if total_wk == 0:
                        dd.kanban_state = 'blocked'
                    else:
                        dd.kanban_state = 'producing'

                    if dd.buckler < dd.max_buckler:
                        dd.buckler += dd.buckler_xm
                else:
                    dd.perc_complete += 3.5
                    if dd.perc_complete >= 100:
                        dd.completed = True
                        dd.kanban_state = 'blocked'

            for r in w.residents:
                if r.life_expectacy > 0:
                    r.life_expectacy -= random.randint(1,6)
                else:
                    w.population -= 1
                    r.unlink()

    @api.depends('image')
    def _get_images(self):
        for i in self:
           image = i.image
           data = tools.image_get_resized_images(image)
           i.image_small = data["image_small"]

    @api.depends()
    def _get_pos(self):
        for i in self:
            i.space_pos = i.id * 10 + random.randint(1,9)

    @api.multi
    def create_new_power_station(self):
        for w in self:
            if w.structures < w.tiles and w.total_energy >= 70:

                cost_x_ps = 70 / w.num_ps
                for ps in w.power_stations:
                    ps.energy = ps.energy - cost_x_ps

                ps = self.env['power_station.structure'].create({
                    'name': 'Default Power Station'+str(random.randint(1,600)),
                    'completed': False,
                    'perc_complete': 0,
                    'lvl': 1,
                    'built_in': w.id,
                    'kanban_state':'start',
                })

    @api.multi
    def create_new_nursery(self):
        for w in self:
            if w.structures < w.tiles and w.total_energy >= 90:

                cost_x_ps = 90 / w.num_ps
                for ps in w.power_stations:
                    ps.energy = ps.energy - cost_x_ps

                n = self.env['nursery.structure'].create({
                    'name': 'Deffault Nursery'+str(random.randint(1,600)),
                    'completed': False,
                    'perc_complete': 0,
                    'lvl': 1,
                    'built_in': w.id,
                    'kanban_state': 'start',
                })

    @api.multi
    def create_new_defense_dome(self):
        for w in self:
            if w.structures < w.tiles and w.total_energy >= 300:

                cost_x_ps = 300 / w.num_ps
                for ps in w.power_stations:
                    ps.energy = ps.energy - cost_x_ps

                dd = self.env['defense_dome.structure'].create({
                    'name': 'Deffault Defense Dome'+str(random.randint(1,600)),
                    'completed': False,
                    'perc_complete': 0,
                    'lvl': 1,
                    'built_in': w.id,
                    'kanban_state':'start',
                })

    @api.multi
    def create_new_attack_tower(self):
        for w in self:
            if w.structures < w.tiles and w.total_energy >= 350:

                cost_x_ps = 350 / w.num_ps
                for ps in w.power_stations:
                    ps.energy = ps.energy - cost_x_ps

                ta = self.env['attack_tower.structure'].create({
                    'name': 'Deffault Attack Tower'+str(random.randint(1,600)),
                    'completed': False,
                    'perc_complete': 0,
                    'lvl': 1,
                    'built_in': w.id,
                    'kanban_state':'start',
                })

class battle(models.Model):
    _name = 'proves.battle'
    name = fields.Char()
    finished = fields.Boolean(default='False')

    attacker = fields.Many2one('proves.player', compute='_read_only')
    defender = fields.Many2one('proves.player', compute='_read_only')

    attack = fields.Many2one('proves.world')
    show_attack = fields.Many2one('proves.world', compute='_read_only')
    defend = fields.Many2one('proves.world')

    att_pos = fields.Integer(compute='_read_only')
    def_pos = fields.Integer(compute='_read_only')
    distance = fields.Integer(compute='_read_only')
    damage = fields.Integer()


    def _get_start_date(self):
        date = datetime.now()
        return fields.Datetime.to_string(date)

    start_date = fields.Datetime(default=_get_start_date)
    end_date = fields.Datetime(compute='_get_end_date')

    def _get_end_date(self):
        for w in self:
            pos_att = w.attack.space_pos
            pos_def = w.defend.space_pos

            space_diff = 0
            if pos_att > pos_def:
                space_diff = pos_att - pos_def
            if pos_att < pos_def:
                space_diff = pos_def - pos_att

            date = w.start_date + timedelta(minutes=space_diff)

            w.end_date = fields.Datetime.to_string(date)

    @api.multi
    def _read_only(self):
        for w in self:
            w.show_attack = w.attack
            w.attacker = w.attack.owner
            w.defender = w.defend.owner
            w.att_pos = w.attack.space_pos
            w.def_pos = w.defend.space_pos
            if w.att_pos < w.def_pos:
                w.distance = w.def_pos - w.att_pos
            if w.att_pos > w.def_pos:
                w.distance = w.att_pos - w.def_pos

    @api.onchange('defend')
    def onchange_attack(self):
        self.defender = self.defend.owner

        self.att_pos = self.attack.space_pos
        self.def_pos = self.defend.space_pos

        pos_att = self.attack.space_pos
        pos_def = self.defend.space_pos

        space_diff = 0
        if pos_att > pos_def:
            space_diff = pos_att - pos_def
        if pos_att < pos_def:
                space_diff = pos_def - pos_att

        date = datetime.now() + timedelta(minutes=space_diff)
        self.end_date = fields.Datetime.to_string(date)
        self.distance = space_diff

    def compute_battle(self):
        date_now = datetime.now()
        for b in self:
            if b.end_date <= date_now:
                dm_for_dd = b.damage / b.defend.num_dd
                for dd in b.defend.defense_dome:
                    dd.buckler = dd.buckler-dm_for_dd
                b.finished = True


class structure(models.Model):
    _name = 'proves.structure'
    name = fields.Char()

    cost = fields.Integer(default=20)
    completed = fields.Boolean(default=False)
    perc_complete = fields.Float('% Complete', (3, 2))
    lvl = fields.Integer()

    built_in = fields.Many2one('proves.world', ondelete='cascade')
    workers = fields.One2many('proves.citizen', 'working')

    #EstadoCo
    kanban_state = fields.Selection([
        ('start', 'Construction in progress'),
        ('blocked', 'Blocked'),
        ('producing', 'In production')],
        'Kanban State', default='start')


class power_station(models.Model):
    _name = 'power_station.structure'
    _inherit = 'proves.structure'

    energy = fields.Integer(default=20)
    max_energy = fields.Integer(default=100)
    energy_xm = fields.Integer(default=20)

class attack_tower(models.Model):
    _name = 'attack_tower.structure'
    _inherit = 'proves.structure'

    damage = fields.Integer(default=40)
    max_damage = fields.Integer(default=400)
    damage_xm = fields.Integer(default=20)

class defense_dome(models.Model):
    _name = 'defense_dome.structure'
    _inherit = 'proves.structure'

    buckler = fields.Integer(default=50)
    max_buckler = fields.Integer(default=200)
    buckler_xm = fields.Integer(default=20)

class nursery(models.Model):
    _name = 'nursery.structure'
    _inherit = 'proves.structure'

    residents = fields.Integer(default=3)
    capacity = fields.Integer(default=40)
    births_xm = fields.Integer(default=20)

class citizen(models.Model):
    _name = 'proves.citizen'
    name = fields.Char()
    life_expectacy = fields.Integer(default=90)
    inteligence = fields.Integer()
    force = fields.Integer()
    ability = fields.Integer()

    inhabiting = fields.Many2one('proves.world', ondelete='cascade')
    working = fields.Many2one('proves.structure')

class event(models.Model):
    _name = 'proves.event'
    name = fields.Char()
    player_inc = fields.Many2many('proves.player')

    date = fields.Datetime()
    end_date = fields.Datetime()

    tipe_event = fields.Selection([
        ('attack', 'Battle'),
        ('exchange', 'Treatment'),
        ('union_petition', 'Request')])

