# -*- coding: utf-8 -*-
from openerp import models, fields, api
class costgroup_wiz(models.TransientModel):
    _name = 'costgroup.wiz'
    mat_ids = fields.Many2many('od.cost.mat.main.pro.line','rel_wiz_material_costgroup','wiz_id','mat_id',string='Mat Main Proposal Line')
    @api.one
    def link(self):
        context = self.env.context
        active_id = context.get('active_id')
        cost_grp_line_obj = self.env['od.cost.costgroup.material.line'].browse(active_id)
        vat_id = cost_grp_line_obj.tax_id and cost_grp_line_obj.tax_id.id or False
        for line in self.mat_ids:
            line['group'] = active_id
            line['tax_id'] = vat_id


class costgroup_remove_wiz(models.TransientModel):
    _name = 'costgroup.remove.wiz'
    mat_ids = fields.Many2many('od.cost.mat.main.pro.line','rel_wiz_material_remove_costgroup','wiz_id','mat_id',string='Mat Main Proposal Line')
    @api.one
    def remove_link(self):
        context = self.env.context
        for line in self.mat_ids:
            line['group'] = False

class costgroup_opt_wiz(models.TransientModel):
    _name = 'costgroup.opt.wiz'
    mat_ids = fields.Many2many('od.cost.mat.optional.item.line','rel_wiz_material_opt_costgroup','wiz_id','mat_id',string='Mat Main Proposal Line')
    @api.one
    def link(self):
        context = self.env.context
        active_id = context.get('active_id')
        for line in self.mat_ids:
            line['group_id'] = active_id

class costgroup_opt_remove_wiz(models.TransientModel):
    _name = 'costgroup.opt.remove.wiz'
    mat_ids = fields.Many2many('od.cost.mat.optional.item.line','rel_wiz_remove_material_opt_costgroup','wiz_id','mat_id',string='Mat Main Proposal Line')
    @api.one
    def remove_link(self):
        context = self.env.context
        for line in self.mat_ids:
            line['group_id'] = False

class costgroup_extra_wiz(models.TransientModel):
    _name = 'costgroup.extra.wiz'
    mat_ids = fields.Many2many('od.cost.mat.extra.expense.line','rel_wiz_material_extra_costgroup','wiz_id','mat_id',string='Mat Main Proposal Line')
    @api.one
    def link(self):
        context = self.env.context
        active_id = context.get('active_id')
        for line in self.mat_ids:
            line['group2'] = active_id

class costgroup_extra_remove_wiz(models.TransientModel):
    _name = 'costgroup.extra.remove.wiz'
    mat_ids = fields.Many2many('od.cost.mat.extra.expense.line','rel_wiz_remove_material_extra_costgroup','wiz_id','mat_id',string='Mat Main Proposal Line')
    @api.one
    def remove_link(self):
        context = self.env.context
        for line in self.mat_ids:
            line['group2'] = False
