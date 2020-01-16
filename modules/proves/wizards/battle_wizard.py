# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools

class battle_wizard(models.Transient):
    _name = 'create.appointment'

    battle_id = fields.Many2one('proves.battle', string = "Battle")

