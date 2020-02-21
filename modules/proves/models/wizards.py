from odoo import models, fields, api, tools
from datetime import datetime, timedelta
from openerp.exceptions import ValidationError


class create_battle(models.TransientModel):
    _name = 'proves.create_battle'

    name = fields.Char(default='Battle')

    attacker = fields.Many2one('res.partner', readonly=True)
    defender = fields.Many2one('res.partner', readonly=True)

    attack = fields.Many2one('proves.world')
    defend = fields.Many2one('proves.world', domain="[('template', '=', False),('owner','!=','attacker')]")

    att_pos = fields.Integer(compute='_compute_details', readonly=True)
    def_pos = fields.Integer(compute='_compute_details', readonly=True)
    distance = fields.Integer(compute='_compute_details', readonly=True)
    damage = fields.Integer()
    max_power_attack = fields.Integer(compute='_compute_details')

    state = fields.Selection([
        ('start', 'Select Objective'),
        ('damage', 'Select the damage structure to attack'),
        ('finish', 'Info of the attack')],
        'state', default='start')

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

    start_date = fields.Datetime(default=_get_start_date, readonly=True)
    end_date = fields.Datetime(compute='_get_end_date', readonly=True)

    @api.multi
    def _compute_details(self):
        self.max_power_attack = self.attack.power_attack
        self.defender = self.defend.owner
        self.att_pos = self.attack.space_pos
        self.def_pos = self.defend.space_pos
        if self.att_pos <= self.def_pos:
            self.distance = self.def_pos - self.att_pos
        if self.att_pos > self.def_pos:
            self.distance = self.att_pos - self.def_pos

    @api.onchange('damage')
    def onchange_damage(self):
        if self.damage > self.max_power_attack:
            self.damage =self.max_power_attack
        if self.damage < 0:
            self.damage = 0

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

    @api.multi
    def next(self):
        if self.state == 'start':
            self.state = 'damage'
        elif self.state == 'damage':
            self.state = 'finish'
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Battle',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    @api.multi
    def back(self):
        if self.state == 'finish':
            self.state = 'damage'
        elif self.state == 'damage':
            self.state = 'start'

        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Battle',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    @api.multi
    def create_battle(self):
        b = self.env['proves.battle'].create({
            'attacker':self.attacker.id,
            'attack':self.attack.id,
            'defend':self.defend.id,
            'defender': self.defender.id,
            'finished':False,
            'distance':self.distance,
            'damage':self.damage,
            'start_date':self.start_date,
            'end_date':self.end_date
        })
        return {
            'name': 'Battle',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'proves.battle',
            'res_id': b.id,
            'context': self._context,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }