# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
from datetime import datetime, timedelta
from openerp.exceptions import ValidationError
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
    _name = 'res.partner'
    _inherit = 'res.partner'
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
        for p in self:
            w_image = self.env.ref('proves.world'+str(random.randint(1,7)))
            ps_image = self.env.ref('proves.power_station_lvl1')
            n_image = self.env.ref('proves.nursery_lvl1')

            w = self.env['proves.world'].create({
                'name': 'Default Planet'+str(random.randint(1,600)),
                'image': w_image.image,
                'template': False,
                'lvl': 1,
                'owner': p.id,
                })
            ps = self.env['power_station.structure'].create({
                'name': 'Default Power Station'+str(random.randint(1,600)),
                'template': False,
                'completed': False,
                'perc_complete': 0,
                'lvl': 1,
                'built_in': w.id,
                'kanban_state':'start',
                'image':ps_image.image,
                'image_lvl': ps_image.image_lvl,
                'inc_int': 5,
                'inc_frc': 6,
                'inc_abt': 9,
            })
            n = self.env['nursery.structure'].create({
                'name': 'Default Nursery'+str(random.randint(1,600)),
                'template': False,
                'completed': False,
                'perc_complete': 0,
                'lvl': 1,
                'built_in': w.id,
                'image': n_image.image,
                'image_lvl': n_image.image_lvl,
                'inc_int': 9,
                'inc_frc': 6,
                'inc_abt': 5,
                'production_xm': 3,
            })

class aliance(models.Model):
    _name = 'proves.aliance'
    name = fields.Char(required=True)
    participants =  fields.One2many('res.partner', 'belongs_aliance')

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
    num_structures = fields.Integer(compute='_get_structures')
    structures = fields.One2many('proves.structure', 'built_in')

    num_nur = fields.Integer(compute='_get_structures')
    production_xm = fields.Integer(compute='_get_structures')
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

    owner = fields.Many2one('res.partner', ondelete='cascade')

    power_stations = fields.One2many('power_station.structure', 'built_in')
    nursery = fields.One2many('nursery.structure', 'built_in')
    attack_towers = fields.One2many('attack_tower.structure', 'built_in')
    defense_dome = fields.One2many('defense_dome.structure', 'built_in')
    residents = fields.One2many('proves.citizen', 'inhabiting')

    @api.depends()
    def _free_tiles(self):
        for w in self:
            w.free_tiles = w.tiles - w.num_structures

    @api.depends()
    def _get_structures(self):
        for w in self:
            w.num_structures = len(w.structures)
            for r in w.residents:
                w.population += 1

            #por tipo de estrucura
            for ps in w.power_stations:
                w.num_ps += 1
                #w.num_structures += 1
                w.energy_xm += ps.production_xm
                w.max_energy += ps.max_energy
                w.total_energy += ps.energy

            for n in w.nursery:
                w.num_nur += 1
                #w.num_structures += 1
                w.production_xm += n.production_xm
                w.max_population += n.capacity

            for at in w.attack_towers:
                w.num_at += 1
                #w.num_structures += 1
                w.power_attack_xm += at.production_xm
                w.power_attack += at.damage
                w.max_power_attack += at.max_damage

            for dd in w.defense_dome:
                w.num_dd += 1
                #w.num_structures += 1
                w.power_defense_xm += dd.production_xm
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

        for w in self.search([]):

            #Batallas
            for b in w.defender:
                if b.finished == False:
                    b.compute_battle()

            #Ciudadanos
            for r in w.residents:
                r.life_expectacy -= random.randint(1, 6)
                if r.life_expectacy <= 0:
                    w.population -= 1
                    #r.unlink()

            #Produccion
            for ps in w.power_stations:
                if ps.completed:
                    total_wk = len(ps.workers)

                    if total_wk == 0:
                        ps.kanban_state = 'blocked'
                    else:
                        ps.kanban_state = 'producing'
                        ps.production_xm = 20
                        for wk in ps.workers:
                            ps.production_xm += (wk.inteligence / ps.inc_int) + (wk.force / ps.inc_frc) + (wk.ability / ps.inc_abt)

                        if ps.energy < ps.max_energy:
                            limit = ps.max_energy - ps.energy
                            if ps.production_xm <= limit:
                                ps.energy += ps.production_xm
                            else:
                                ps.energy += ps.production_xm - limit
                else:
                    ps.perc_complete += 25
                    if ps.perc_complete >= 100:
                        ps.completed = True
                        ps.kanban_state = 'blocked'

            for n in w.nursery:
                if n.completed:
                    total_wk = len(n.workers)

                    if total_wk == 0:
                        n.kanban_state = 'blocked'
                    else:
                        n.kanban_state = 'producing'
                        n.production_xm = 3
                        for wk in n.workers:
                            n.production_xm += (wk.inteligence / n.inc_int) + (wk.force / n.inc_frc) + (wk.ability / n.inc_abt)

                        if w.population < w.max_population:
                            limit =  n.capacity - total_wk
                            cnt = 0
                            for b in range(0,int(round(n.production_xm))):
                                cnt += 1
                                if cnt <= limit:
                                    a = self.env['proves.citizen'].create({
                                        'name' :  str(random.choice(names)),
                                        'inteligence' : str(random.randint(1,7)),
                                        'force' : str(random.randint(1,7)),
                                        'ability' : str(random.randint(1,7)),
                                        'inhabiting' : w.id,
                                        'working': n.structure_id.id,
                                    })
                else:
                    n.perc_complete += 25
                    if n.perc_complete >= 100:
                        n.completed = True
                        for b in range(int(round(n.production_xm))):
                            a = self.env['proves.citizen'].create({
                                'name' :  str(random.choice(names)),
                                'inteligence' : str(random.randint(1,7)),
                                'force' : str(random.randint(1,7)),
                                'ability' : str(random.randint(1,7)),
                                'inhabiting' : w.id,
                                'working': n.structure_id.id,
                            })

            for at in w.attack_towers:
                if at.completed:
                    total_wk = len(at.workers)

                    if total_wk == 0:
                        at.kanban_state = 'blocked'
                    else:
                        at.kanban_state = 'producing'
                        at.production_xm = 20

                        for wk in at.workers:
                            at.production_xm += (wk.inteligence / at.inc_int) + (wk.force / at.inc_frc) + (wk.ability / at.inc_abt)

                        if at.damage < at.max_damage:
                            limit = at.max_damage - at.damage
                            if at.production_xm <= limit:
                                at.damage += at.production_xm
                            else:
                                at.damage += at.production_xm - limit
                else:
                    at.perc_complete += 25
                    if at.perc_complete >= 100:
                        at.completed = True
                        at.kanban_state = 'blocked'

            for dd in w.defense_dome:
                if dd.completed:
                    total_wk = len(dd.workers)

                    if total_wk == 0:
                        dd.kanban_state = 'blocked'
                    else:
                        dd.kanban_state = 'producing'
                        dd.production_xm = 20

                        for wk in dd.workers:
                            dd.production_xm += (wk.inteligence / dd.inc_int) + (wk.force / dd.inc_frc) + (wk.ability / dd.inc_abt)

                        if dd.buckler < dd.max_buckler:
                            limit = dd.max_buckler - dd.buckler
                            if dd.production_xm <= limit:
                                dd.buckler += dd.production_xm
                            else:
                                dd.buckler += dd.production_xm - limit
                else:
                    dd.perc_complete += 25
                    if dd.perc_complete >= 100:
                        dd.completed = True
                        dd.kanban_state = 'blocked'

            #Costes energeticos
            for s in w.structures:
                w.total_energy -= s.energy_tax


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
            if w.num_structures < w.tiles and w.total_energy >= 40:
                cost_x_ps = 40 / w.num_ps
                for ps in w.power_stations:
                    ps.energy -= cost_x_ps

                ps_image = self.env.ref('proves.power_station_lvl1')

                ps = self.env['power_station.structure'].create({
                    'name': 'Default Power Station'+str(random.randint(1,600)),
                    'completed': False,
                    'perc_complete': 0,
                    'lvl': 1,
                    'built_in': w.id,
                    'energy_tax': 1,
                    'kanban_state':'start',
                    'image': ps_image.image,
                    'image_lvl': ps_image.image_lvl,
                    'inc_int': 5,
                    'inc_frc': 6,
                    'inc_abt': 9,
                })

    @api.multi
    def create_new_nursery(self):
        names = ["Zagu", "Bonki", "Britya", "Rambiksh", "Dushakh", "Gurbag", "Caltxa", "Shibelna",
                 "Saide", "Lakshi", "Ayoth", "Gharn", "Krishuru", "Throg", "Dushuum",
                 "Krishgal", "Galda", "Kuquilu", "Kitara", "Margora", "Visenuky", "Prasha", "Ardeva",
                 "Gulgexo", "Golugrog", "Grith", "Zaisty", "Beera", "Adimha", "Krutundu"]

        for w in self:
            if w.num_structures < w.tiles and w.total_energy >= 90:
                cost_x_ps = 90 / w.num_ps
                for ps in w.power_stations:
                    ps.energy = ps.energy - cost_x_ps

                n_image = self.env.ref('proves.nursery_lvl1')

                n = self.env['nursery.structure'].create({
                    'name': 'Deffault Nursery'+str(random.randint(1,600)),
                    'completed': False,
                    'perc_complete': 0,
                    'lvl': 1,
                    'built_in': w.id,
                    'energy_tax': 4,
                    'kanban_state': 'start',
                    'image': n_image.image,
                    'image_lvl': n_image.image_lvl,
                    'inc_int': 9,
                    'inc_frc': 6,
                    'inc_abt': 5,
                    'production_xm': 3,
                })

    @api.multi
    def create_new_defense_dome(self):
        for w in self:
            if w.num_structures < w.tiles and w.total_energy >= 300:

                cost_x_ps = 300 / w.num_ps
                for ps in w.power_stations:
                    ps.energy = ps.energy - cost_x_ps

                dd_image = self.env.ref('proves.defense_dome_lvl1')

                dd = self.env['defense_dome.structure'].create({
                    'name': 'Deffault Defense Dome'+str(random.randint(1,600)),
                    'completed': False,
                    'perc_complete': 0,
                    'lvl': 1,
                    'built_in': w.id,
                    'energy_tax': 6,
                    'kanban_state':'start',
                    'image': dd_image.image,
                    'image_lvl': dd_image.image_lvl,
                    'inc_int': 9,
                    'inc_frc': 5,
                    'inc_abt': 5,
                })

    @api.multi
    def create_new_attack_tower(self):
        for w in self:
            if w.num_structures < w.tiles and w.total_energy >= 350:
                cost_x_ps = 350 / w.num_ps
                for ps in w.power_stations:
                    ps.energy -= cost_x_ps

                ta_image = self.env.ref('proves.attack_tower_lvl1')

                ta = self.env['attack_tower.structure'].create({
                    'name': 'Deffault Attack Tower'+str(random.randint(1,600)),
                    'completed': False,
                    'perc_complete': 0,
                    'lvl': 1,
                    'built_in': w.id,
                    'energy_tax': 6,
                    'kanban_state':'start',
                    'image': ta_image.image,
                    'image_lvl': ta_image.image_lvl,
                    'inc_int': 5,
                    'inc_frc': 6,
                    'inc_abt': 6,
                })

class battle(models.Model):
    _name = 'proves.battle'
    name = fields.Char(default='Battle')
    finished = fields.Boolean(default='False')

    attacker = fields.Many2one('res.partner', compute='_read_only')
    defender = fields.Many2one('res.partner', compute='_read_only')

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

class citizen(models.Model):
    _name = 'proves.citizen'
    name = fields.Char()
    dead = fields.Boolean(default=False)
    life_expectacy = fields.Integer(default=90)
    inteligence = fields.Integer()
    force = fields.Integer()
    ability = fields.Integer()

    inhabiting = fields.Many2one('proves.world')
    working = fields.Many2one('proves.structure', ondelete='cascade', domain="[('built_in', '=', inhabiting)]")

class structure(models.Model):
    _name = 'proves.structure'
    name = fields.Char()
    template = fields.Boolean()

    cost = fields.Integer(default=20)
    completed = fields.Boolean(default=False)
    perc_complete = fields.Float('% Complete', (3, 2))
    lvl = fields.Integer()
    resource = fields.Integer()

    built_in = fields.Many2one('proves.world', ondelete='cascade')
    workers = fields.One2many('proves.citizen', 'working')
    production_xm = fields.Float()
    energy_tax = fields.Integer()

    image = fields.Binary()
    image_lvl = fields.Binary()
    image_small = fields.Binary(string='Image', compute='_get_images', store=True)
    image_lvl_small = fields.Binary(string='Image', compute='_get_lvl_images', store=True)

    inc_int = fields.Integer()
    inc_frc = fields.Integer()
    inc_abt = fields.Integer()

    #EstadoCo
    kanban_state = fields.Selection([
        ('start', 'Construction in progress'),
        ('blocked', 'Blocked'),
        ('producing', 'In production')],
        'Kanban State', default='start')

    @api.depends('image')
    def _get_images(self):
        for i in self:
            image = i.image
            data = tools.image_get_resized_images(image)
            i.image_small = data["image_small"]


    @api.depends('image_lvl')
    def _get_lvl_images(self):
        for i in self:
            image = i.image_lvl
            data = tools.image_get_resized_images(image)
            i.image_lvl_small = data["image_small"]


class power_station(models.Model):
    _name = 'power_station.structure'
    _inherits = {'proves.structure':'structure_id'}

    energy = fields.Integer(default=20)
    max_energy = fields.Integer(default=100)

    @api.multi
    def up_lvl(self):
        if self.lvl == 3:
            ps_image = self.env.ref('proves.power_station_lvl4')
            self.image_lvl = ps_image.image_lvl
            self.lvl = self.lvl + 1
            self.production_xm = 15
            self.max_energy = 600
            self.energy_tax = 4
            self.inc_int = 2
            self.inc_frc = 3
            self.inc_abt = 6
            self.completed = False
            self.perc_complete = 0
            self.kanban_state = 'start'
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        if self.lvl == 2:
            ps_image = self.env.ref('proves.power_station_lvl3')
            self.image_lvl = ps_image.image_lvl
            self.lvl = self.lvl + 1
            self.production_xm = 10
            self.max_energy = 300
            self.energy_tax = 3
            self.inc_int = 3
            self.inc_frc = 4
            self.inc_abt = 7
            self.completed = False
            self.perc_complete = 0
            self.kanban_state = 'start'
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        if self.lvl == 1:
            ps_image = self.env.ref('proves.power_station_lvl2')
            self.image_lvl = ps_image.image_lvl
            self.lvl = self.lvl + 1
            self.production_xm = 7
            self.max_energy = 175
            self.energy_tax = 2
            self.inc_int = 4
            self.inc_frc = 5
            self.inc_abt = 8
            self.completed = False
            self.perc_complete = 0
            self.kanban_state = 'start'
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }

class attack_tower(models.Model):
    _name = 'attack_tower.structure'
    _inherits = {'proves.structure':'structure_id'}

    damage = fields.Integer(default=40)
    max_damage = fields.Integer(default=400)

    @api.multi
    def up_lvl(self):
        if self.lvl == 3:
            at_image = self.env.ref('proves.attack_tower_lvl4')
            self.image_lvl = at_image.image_lvl
            self.lvl = self.lvl + 1
            self.production_xm = 50
            self.max_damage = 1500
            self.energy_tax = 10
            self.inc_int = 2
            self.inc_frc = 3
            self.inc_abt = 3
            self.completed = False
            self.perc_complete = 0
            self.kanban_state = 'start'
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        if self.lvl == 2:
            at_image = self.env.ref('proves.attack_tower_lvl3')
            self.image_lvl = at_image.image_lvl
            self.lvl = self.lvl + 1
            self.production_xm = 16
            self.max_damage = 800
            self.energy_tax = 9
            self.inc_int = 3
            self.inc_frc = 4
            self.inc_abt = 4
            self.completed = False
            self.perc_complete = 0
            self.kanban_state = 'start'
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        if self.lvl == 1:
            at_image = self.env.ref('proves.attack_tower_lvl2')
            self.image_lvl = at_image.image_lvl
            self.lvl = self.lvl + 1
            self.production_xm = 8
            self.max_damage = 600
            self.energy_tax = 8
            self.inc_int = 4
            self.inc_frc = 5
            self.inc_abt = 5
            self.completed = False
            self.perc_complete = 0
            self.kanban_state = 'start'
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }

class defense_dome(models.Model):
    _name = 'defense_dome.structure'
    _inherits = {'proves.structure':'structure_id'}

    buckler = fields.Integer(default=50)
    max_buckler = fields.Integer(default=200)

    @api.multi
    def up_lvl(self):
        if self.lvl == 3:
            dd_image = self.env.ref('proves.defense_dome_lvl4')
            self.image_lvl = dd_image.image_lvl
            self.lvl = self.lvl + 1
            self.production_xm = 50
            self.max_buckler = 1500
            self.energy_tax = 8
            self.inc_int = 6
            self.inc_frc = 2
            self.inc_abt = 2
            self.completed = False
            self.perc_complete = 0
            self.kanban_state = 'start'
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        if self.lvl == 2:
            dd_image = self.env.ref('proves.defense_dome_lvl3')
            self.image_lvl = dd_image.image_lvl
            self.lvl = self.lvl + 1
            self.production_xm = 16
            self.max_buckler = 800
            self.energy_tax = 7
            self.inc_int = 7
            self.inc_frc = 3
            self.inc_abt = 3
            self.completed = False
            self.perc_complete = 0
            self.kanban_state = 'start'
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        if self.lvl == 1:
            dd_image = self.env.ref('proves.defense_dome_lvl2')
            self.image_lvl = dd_image.image_lvl
            self.lvl = self.lvl + 1
            self.production_xm = 8
            self.max_buckler = 600
            self.energy_tax = 6
            self.inc_int = 8
            self.inc_frc = 4
            self.inc_abt = 4
            self.completed = False
            self.perc_complete = 0
            self.kanban_state = 'start'
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }

class nursery(models.Model):
    _name = 'nursery.structure'
    _inherits = {'proves.structure':'structure_id'}
    they_inhabit = fields.Integer(compute='_count_workers')
    capacity = fields.Integer(default=40)

    @api.multi
    def _count_workers(self):
        for n in self:
            n.they_inhabit = len(n.workers)

    @api.multi
    def up_lvl(self):
        if self.lvl == 3:
            n_image = self.env.ref('proves.nursery_lvl4')
            self.image_lvl = n_image.image_lvl
            self.lvl = self.lvl + 1
            self.production_xm = 32
            self.capacity = 320
            self.energy_tax = 7
            self.inc_int = 7
            self.inc_frc = 3
            self.inc_abt = 2
            self.completed = False
            self.perc_complete = 0
            self.kanban_state = 'start'
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        if self.lvl == 2:
            n_image = self.env.ref('proves.nursery_lvl3')
            self.image_lvl = n_image.image_lvl
            self.lvl = self.lvl + 1
            self.production_xm = 16
            self.capacity = 160
            self.energy_tax = 6
            self.inc_int = 7
            self.inc_frc = 4
            self.inc_abt = 3
            self.completed = False
            self.perc_complete = 0
            self.kanban_state = 'start'
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        if self.lvl == 1:
            n_image = self.env.ref('proves.nursery_lvl2')
            self.image_lvl = n_image.image_lvl
            self.lvl = self.lvl + 1
            self.production_xm = 8
            self.capacity = 80
            self.energy_tax = 5
            self.inc_int = 8
            self.inc_frc = 5
            self.inc_abt = 4
            self.completed = False
            self.perc_complete = 0
            self.kanban_state = 'start'
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }

class event(models.Model):
    _name = 'proves.event'
    name = fields.Char()
    player_inc = fields.Many2many('res.partner')

    date = fields.Datetime()
    end_date = fields.Datetime()

    tipe_event = fields.Selection([
        ('attack', 'Battle'),
        ('exchange', 'Treatment'),
        ('union_petition', 'Request')])

