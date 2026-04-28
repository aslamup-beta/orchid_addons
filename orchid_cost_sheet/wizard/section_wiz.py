# -*- coding: utf-8 -*-
from openerp import models, fields, api
class section_mat_add_wiz(models.TransientModel):
    _name = 'section.mat.add.wiz'
    mat_ids = fields.Many2many('od.cost.mat.main.pro.line','rel_wiz_material_section_add','wiz_id','mat_id',string='Mat Main Proposal Line')
    @api.one
    def link(self):
        context = self.env.context
        active_id = context.get('active_id')
        for line in self.mat_ids:
            line['section_id'] = active_id

class section_mat_remove_wiz(models.TransientModel):
    _name = 'section.mat.remove.wiz'
    mat_ids = fields.Many2many('od.cost.mat.main.pro.line','rel_wiz_material_remove_section','wiz_id','mat_id',string='Mat Main Proposal Line')
    @api.one
    def remove_link(self):
        context = self.env.context
        for line in self.mat_ids:
            line['section_id'] = False


class section_opt_add_wiz(models.TransientModel):
    _name = 'section.opt.add.wiz'
    mat_ids = fields.Many2many('od.cost.mat.optional.item.line','rel_wiz_material_opt_secton_add','wiz_id','mat_id',string='Mat Main Proposal Line')
    @api.one
    def link(self):
        context = self.env.context
        active_id = context.get('active_id')
        for line in self.mat_ids:
            line['opt_section_id'] = active_id

class section_opt_remove_wiz(models.TransientModel):
    _name = 'section.opt.remove.wiz'
    mat_ids = fields.Many2many('od.cost.mat.optional.item.line','rel_wiz_remove_material_opt_section','wiz_id','mat_id',string='Mat Main Proposal Line')
    @api.one
    def remove_link(self):
        context = self.env.context
        for line in self.mat_ids:
            line['opt_section_id'] = False


class section_trn_add_wiz(models.TransientModel):
    _name = 'section.trn.add.wiz'
    mat_ids = fields.Many2many('od.cost.trn.customer.training.line','rel_wiz_material_trn_secton_add','wiz_id','mat_id',string='Mat Main Proposal Line')
    @api.one
    def link(self):
        context = self.env.context
        active_id = context.get('active_id')
        for line in self.mat_ids:
            line['trn_section_id'] = active_id

class section_trn_remove_wiz(models.TransientModel):
    _name = 'section.trn.remove.wiz'
    mat_ids = fields.Many2many('od.cost.trn.customer.training.line','rel_wiz_remove_material_trn_section','wiz_id','mat_id',string='Mat Main Proposal Line')
    @api.one
    def remove_link(self):
        context = self.env.context
        for line in self.mat_ids:
            line['trn_section_id'] = False
