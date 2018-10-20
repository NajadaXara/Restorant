# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import logging

from odoo import api, fields, models, exceptions
from datetime import datetime
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource

class Menu(models.Model):
    _name = "restorant.menu"
    _description = "Menu"

    name = fields.Char(string="Emri")
    perberes = fields.Char(string="Perberesi")
    informacion = fields.Char(string="Info")
    cmimi = fields.Float(string="Cmimi")
    menu_dite = fields.Boolean(string="Menu Ditore")

class Kamarier(models.Model):
    _name = "restorant.kamarier"
    _description = "Kamarier"

    name = fields.Char(string="Kamarier_Id")
    emri = fields.Char(string="Emri")
    mbiemri = fields.Char(string="Mbiemri")
    informacion = fields.Text(string="Info")

class Tavolina(models.Model):
    _name = "restorant.tavolina"
    _description = "Tavolina"

    name = fields.Char(string="Numri Tavolines")
    id_kamarier = fields.Many2one('restorant.kamarier', string="Kamarier_Id")

    state = fields.Selection([
        ('perfunduar', 'Bosh'),
        ('krijuar', 'E Rezervuar'),
        ('pritje', 'E Zene'),
        ('servirur', 'Servirur')], string='Statusi', default="perfunduar")

    @api.multi
    def liro(self):
        self.state = 'perfunduar'
        for tavolina in self:
            if tavolina.state:
                ids = self.env['restorant.porosi'].search([('tavolina_id', '=', tavolina.id)])
                if ids:
                    ids.write({'status': tavolina.state})

    # @api.multi
    # def cancel(self):
    #     for tavolina in self:
    #             if tavolina.state:
    #                 self.env['restorant.porosi'].search([('tavolina_id', '=', tavolina.name)]).unlink()
    #     self.state = 'liruar'

class Porosi(models.Model):
    _name = "restorant.porosi"
    _description = "Porosi"

    name = fields.Char(string="Emri Porosise")
    tavolina_id = fields.Many2one('restorant.tavolina', string="Tavolina_Id")
    menu_ids = fields.Many2many('restorant.menu', string='Menus')
    cmimi_total = fields.Float(compute="_get_total_price", string="Cmimi")
    status = fields.Selection([
        ('bosh', 'Ne Krijim'),
        ('krijuar', 'Krijuar'),
        ('pritje', 'Pritje'),
        ('servirur', 'Servirur'),
        ('perfunduar', 'Perfunduar')], string='Statusi', default="bosh")
    data = fields.Datetime(string="Data", default=datetime.today())

    @api.multi
    def merr(self):
        self.status = 'pritje'
        for porosi in self:
            if porosi.tavolina_id:
                for tavolina in porosi.tavolina_id:
                    tavolina.write({'state': self.status})

    @api.multi
    def servir(self):
        self.status = 'servirur'
        for porosi in self:
            if porosi.tavolina_id:
                for tavolina in porosi.tavolina_id:
                    tavolina.write({'state': self.status})

    @api.onchange('status')
    @api.multi
    def _change_status(self):
        for porosi in self:
            if porosi.tavolina_id:
                for tavolina in porosi.tavolina_id:
                    tavolina.write({'state': self.status})

    @api.multi
    def _get_total_price(self):
        for porosi in self:
            cmimi = 0.0
            if porosi.menu_ids:
                for menu in porosi.menu_ids:
                    cmimi += menu.cmimi
            porosi.cmimi_total = cmimi

# class SasiPorosi(models.Model):
#     _name = "restorant.sasiporosi"
#     _description = "Sasia e Porosise"
#
#     menu = fields.Many2many('restorant.menu', string="Menus")
#     sasia = fields.Integer(string="Sasia")
#     porosia = fields.Many2one('restorant.porosi', string="Porosia")
