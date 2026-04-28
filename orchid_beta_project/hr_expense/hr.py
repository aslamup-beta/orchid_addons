# -*- coding: utf-8 -*-
from openerp import models,fields,api,_
from openerp.exceptions import Warning
import re
from datetime import date as dt
from datetime import timedelta,datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT
class hr_employee(models.Model):
    _inherit ="hr.employee"
    
    
    hr_subt = fields.Float(string="Hour Subtract")
    hr_subt_1 = fields.Float(string="Hour Subtract")
    hr_subt_2 = fields.Float(string="Hour Subtract")
    hr_subt_3 = fields.Float(string="Hour Subtract")
    hr_subt_4 = fields.Float(string="Hour Subtract")
    hr_subt_5 = fields.Float(string="Hour Subtract")
    hr_subt_6 = fields.Float(string="Hour Subtract")
    hr_subt_7 = fields.Float(string="Hour Subtract")
    hr_subt_8 = fields.Float(string="Hour Subtract")
    hr_subt_9 = fields.Float(string="Hour Subtract")
    hr_subt_10 = fields.Float(string="Hour Subtract")
    hr_subt_11 = fields.Float(string="Hour Subtract")
    hr_subt_12 = fields.Float(string="Hour Subtract")
    mgr_score_selection =[(x, x) for x in [-5,-10,-15,-20]]
    #audit fileds
    audit_temp_id = fields.Many2one('audit.template',string="Audit Template")
    annual_target = fields.Float(string="Annual Target")
    aud_date_start1 = fields.Date(string="Audit Start")
    aud_date_end1 = fields.Date(string="Audit End")
    execute1 = fields.Boolean("Execute")
    weight1 = fields.Float(string="Weight")
    audit_sample1 = fields.Many2one('audit.sample',string="Audit Sample")
    score1  = fields.Float(string="Score")
    cert1 = fields.Boolean(string="Certificate Required")
    cert_id1 = fields.Many2one('employee.certificate',string="Certificate")
    cert_weight1 = fields.Float(string="Certificate Weight")
    cert_status1 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    mgr_feedback1 = fields.Boolean(string="Manager Feedback")
    mgr_score1 = fields.Selection(mgr_score_selection,string="Manager Score")
    utl1= fields.Float(string="Utilization")
    
    
    aud_date_start2 = fields.Date(string="Audit Start")
    aud_date_end2 = fields.Date(string="Audit End")
    execute2 = fields.Boolean("Currently Executing")
    weight2 = fields.Float(string="Weight")
    audit_sample2 = fields.Many2one('audit.sample',string="Audit Sample")
    score2  = fields.Float(string="Score")
    cert2 = fields.Boolean(string="Certificate Required")
    cert_id2 = fields.Many2one('employee.certificate',string="Certificate")
    cert_weight2 = fields.Float(string="Certificate Weight")
    cert_status2 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    mgr_feedback2 = fields.Boolean(string="Manager Feedback")
    mgr_score2 = fields.Selection(mgr_score_selection,string="Manager Score")
    utl2= fields.Float(string="Utilization")
    
    aud_date_start3 = fields.Date(string="Audit Start")
    aud_date_end3 = fields.Date(string="Audit End")
    execute3 = fields.Boolean("Currently Executing")
    weight3 = fields.Float(string="Weight")
    audit_sample3 = fields.Many2one('audit.sample',string="Audit Sample")
    score3  = fields.Float(string="Score")
    cert3 = fields.Boolean(string="Certificate Required")
    cert_id3 = fields.Many2one('employee.certificate',string="Certificate")
    cert_weight3 = fields.Float(string="Certificate Weight")
    cert_status3 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    mgr_feedback3 = fields.Boolean(string="Manager Feedback")
    mgr_score3 = fields.Selection(mgr_score_selection,string="Manager Score")
    utl3= fields.Float(string="Utilization")
    
    
    aud_date_start4 = fields.Date(string="Audit Start")
    aud_date_end4 = fields.Date(string="Audit End")
    execute4 = fields.Boolean("Currently Executing")
    weight4 = fields.Float(string="Weight")
    audit_sample4 = fields.Many2one('audit.sample',string="Audit Sample")
    score4  = fields.Float(string="Score")
    cert4 = fields.Boolean(string="Certificate Required")
    cert_id4 = fields.Many2one('employee.certificate',string="Certificate")
    cert_weight4 = fields.Float(string="Certificate Weight")
    cert_status4 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    mgr_feedback4 = fields.Boolean(string="Manager Feedback")
    mgr_score4 = fields.Selection(mgr_score_selection,string="Manager Score")
    utl4= fields.Float(string="Utilization")
    
    
    aud_date_start5 = fields.Date(string="Audit Start")
    aud_date_end5 = fields.Date(string="Audit End")
    execute5 = fields.Boolean("Currently Executing")
    weight5 = fields.Float(string="Weight")
    audit_sample5 = fields.Many2one('audit.sample',string="Audit Sample")
    score5  = fields.Float(string="Score")
    cert5 = fields.Boolean(string="Certificate Required")
    cert_id5 = fields.Many2one('employee.certificate',string="Certificate")
    cert_weight5 = fields.Float(string="Certificate Weight")
    cert_status5 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    mgr_feedback5 = fields.Boolean(string="Manager Feedback")
    mgr_score5 = fields.Selection(mgr_score_selection,string="Manager Score")
    utl5= fields.Float(string="Utilization")
    
    
    aud_date_start6 = fields.Date(string="Audit Start")
    aud_date_end6 = fields.Date(string="Audit End")
    execute6 = fields.Boolean("Currently Executing")
    weight6 = fields.Float(string="Weight")
    audit_sample6 = fields.Many2one('audit.sample',string="Audit Sample")
    score6  = fields.Float(string="Score")
    cert6 = fields.Boolean(string="Certificate Required")
    cert_id6 = fields.Many2one('employee.certificate',string="Certificate")
    cert_weight6 = fields.Float(string="Certificate Weight")
    cert_status6 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    mgr_feedback6 = fields.Boolean(string="Manager Feedback")
    mgr_score6 = fields.Selection(mgr_score_selection,string="Manager Score")
    utl6= fields.Float(string="Utilization")
    
    
    aud_date_start7 = fields.Date(string="Audit Start")
    aud_date_end7 = fields.Date(string="Audit End")
    execute7 = fields.Boolean("Currently Executing")
    weight7 = fields.Float(string="Weight")
    audit_sample7 = fields.Many2one('audit.sample',string="Audit Sample")
    score7  = fields.Float(string="Score")
    cert7 = fields.Boolean(string="Certificate Required")
    cert_id7 = fields.Many2one('employee.certificate',string="Certificate")
    cert_weight7 = fields.Float(string="Certificate Weight")
    cert_status7 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    mgr_feedback7 = fields.Boolean(string="Manager Feedback")
    mgr_score7 = fields.Selection(mgr_score_selection,string="Manager Score")
    utl7= fields.Float(string="Utilization")
    
    
    aud_date_start8 = fields.Date(string="Audit Start")
    aud_date_end8 = fields.Date(string="Audit End")
    execute8 = fields.Boolean("Currently Executing")
    weight8 = fields.Float(string="Weight")
    audit_sample8 = fields.Many2one('audit.sample',string="Audit Sample")
    score8  = fields.Float(string="Score")
    cert8 = fields.Boolean(string="Certificate Required")
    cert_id8 = fields.Many2one('employee.certificate',string="Certificate")
    cert_weight8 = fields.Float(string="Certificate Weight")
    cert_status8 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    mgr_feedback8 = fields.Boolean(string="Manager Feedback")
    mgr_score8 = fields.Selection(mgr_score_selection,string="Manager Score")
    utl8= fields.Float(string="Utilization")

    
    aud_date_start9 = fields.Date(string="Audit Start")
    aud_date_end9 = fields.Date(string="Audit End")
    execute9 = fields.Boolean("Currently Executing")
    weight9 = fields.Float(string="Weight")
    audit_sample9 = fields.Many2one('audit.sample',string="Audit Sample")
    score9  = fields.Float(string="Score")
    cert9 = fields.Boolean(string="Certificate Required")
    cert_id9 = fields.Many2one('employee.certificate',string="Certificate")
    cert_weight9 = fields.Float(string="Certificate Weight")
    cert_status9 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    mgr_feedback9 = fields.Boolean(string="Manager Feedback")
    mgr_score9 = fields.Selection(mgr_score_selection,string="Manager Score")
    utl9= fields.Float(string="Utilization")
    
    
    aud_date_start10 = fields.Date(string="Audit Start")
    aud_date_end10 = fields.Date(string="Audit End")
    execute10 = fields.Boolean("Currently Executing")
    weight10 = fields.Float(string="Weight")
    audit_sample10 = fields.Many2one('audit.sample',string="Audit Sample")
    score10  = fields.Float(string="Score")
    cert10 = fields.Boolean(string="Certificate Required")
    cert_id10 = fields.Many2one('employee.certificate',string="Certificate")
    cert_weight10 = fields.Float(string="Certificate Weight")
    cert_status10 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    mgr_feedback10 = fields.Boolean(string="Manager Feedback")
    mgr_score10 = fields.Selection(mgr_score_selection,string="Manager Score")
    utl10= fields.Float(string="Utilization")

    
    aud_date_start11 = fields.Date(string="Audit Start")
    aud_date_end11 = fields.Date(string="Audit End")
    execute11 = fields.Boolean("Currently Executing")
    weight11 = fields.Float(string="Weight")
    audit_sample11 = fields.Many2one('audit.sample',string="Audit Sample")
    score11  = fields.Float(string="Score")
    cert11 = fields.Boolean(string="Certificate Required")
    cert_id11 = fields.Many2one('employee.certificate',string="Certificate")
    cert_weight11 = fields.Float(string="Certificate Weight")
    cert_status11 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    mgr_feedback11 = fields.Boolean(string="Manager Feedback")
    mgr_score11 = fields.Selection(mgr_score_selection,string="Manager Score")
    utl11= fields.Float(string="Utilization")
    
    
    aud_date_start12 = fields.Date(string="Audit Start")
    aud_date_end12 = fields.Date(string="Audit End")
    execute12 = fields.Boolean("Currently Executing")
    weight12 = fields.Float(string="Weight")
    audit_sample12 = fields.Many2one('audit.sample',string="Audit Sample")
    score12  = fields.Float(string="Score")
    cert12 = fields.Boolean(string="Certificate Required")
    cert_id12 = fields.Many2one('employee.certificate',string="Certificate")
    cert_weight12 = fields.Float(string="Certificate Weight")
    cert_status12 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    mgr_feedback12 = fields.Boolean(string="Manager Feedback")
    mgr_score12 = fields.Selection(mgr_score_selection,string="Manager Score")
    utl12= fields.Float(string="Utilization")
    
    commit_total = fields.Float(string="Current Month Commit Total")
    
    brand_id1= fields.Many2one('od.product.brand',string="Brand")
    brand_id2= fields.Many2one('od.product.brand',string="Brand")
    brand_id3= fields.Many2one('od.product.brand',string="Brand")
    brand_id4= fields.Many2one('od.product.brand',string="Brand")
    brand_id5= fields.Many2one('od.product.brand',string="Brand")
    brand_id6= fields.Many2one('od.product.brand',string="Brand")
    brand_id7= fields.Many2one('od.product.brand',string="Brand")
    brand_id8= fields.Many2one('od.product.brand',string="Brand")
    brand_id9= fields.Many2one('od.product.brand',string="Brand")
    brand_id10= fields.Many2one('od.product.brand',string="Brand")
    brand_id11= fields.Many2one('od.product.brand',string="Brand")
    brand_id12= fields.Many2one('od.product.brand',string="Brand")
    
    sale_cert_id1= fields.Many2one('sale.certificate',string="Sales Certificate")
    sale_cert_id2= fields.Many2one('sale.certificate',string="Sales Certificate")
    sale_cert_id3= fields.Many2one('sale.certificate',string="Sales Certificate")
    sale_cert_id4= fields.Many2one('sale.certificate',string="Sales Certificate")
    sale_cert_id5= fields.Many2one('sale.certificate',string="Sales Certificate")
    sale_cert_id6= fields.Many2one('sale.certificate',string="Sales Certificate")
    sale_cert_id7= fields.Many2one('sale.certificate',string="Sales Certificate")
    sale_cert_id8= fields.Many2one('sale.certificate',string="Sales Certificate")
    sale_cert_id9= fields.Many2one('sale.certificate',string="Sales Certificate")
    sale_cert_id10= fields.Many2one('sale.certificate',string="Sales Certificate")
    sale_cert_id11= fields.Many2one('sale.certificate',string="Sales Certificate")
    sale_cert_id12= fields.Many2one('sale.certificate',string="Sales Certificate")
    
    
    
    engineer_cert_id1= fields.Many2one('engineer.certificate',string="engineers Certificate")
    engineer_cert_id2= fields.Many2one('engineer.certificate',string="engineers Certificate")
    engineer_cert_id3= fields.Many2one('engineer.certificate',string="engineers Certificate")
    engineer_cert_id4= fields.Many2one('engineer.certificate',string="engineers Certificate")
    engineer_cert_id5= fields.Many2one('engineer.certificate',string="engineers Certificate")
    engineer_cert_id6= fields.Many2one('engineer.certificate',string="engineers Certificate")
    engineer_cert_id7= fields.Many2one('engineer.certificate',string="engineers Certificate")
    engineer_cert_id8= fields.Many2one('engineer.certificate',string="engineers Certificate")
    engineer_cert_id9= fields.Many2one('engineer.certificate',string="engineers Certificate")
    engineer_cert_id10= fields.Many2one('engineer.certificate',string="engineers Certificate")
    engineer_cert_id11= fields.Many2one('engineer.certificate',string="engineers Certificate")
    engineer_cert_id12= fields.Many2one('engineer.certificate',string="engineers Certificate")
    
    sess1 = fields.Boolean(string="Sales Enablement")
    sale_enab_id1 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    sess_status1 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    sess2 = fields.Boolean(string="Sales Enablement")
    sale_enab_id2 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    sess_status2 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    sess3 = fields.Boolean(string="Sales Enablement")
    sale_enab_id3 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    sess_status3 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    sess4 = fields.Boolean(string="Sales Enablement")
    sale_enab_id4 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    sess_status4 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    sess4 = fields.Boolean(string="Sales Enablement")
    sale_enab_id4 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    sess_status4 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    sess5 = fields.Boolean(string="Sales Enablement")
    sale_enab_id5 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    sess_status5 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    sess6 = fields.Boolean(string="Sales Enablement")
    sale_enab_id6 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    sess_status6 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    sess7 = fields.Boolean(string="Sales Enablement")
    sale_enab_id7 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    sess_status7 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    sess8 = fields.Boolean(string="Sales Enablement")
    sale_enab_id8 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    sess_status8 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    sess9 = fields.Boolean(string="Sales Enablement")
    sale_enab_id9 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    sess_status9 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    sess10 = fields.Boolean(string="Sales Enablement")
    sale_enab_id10 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    sess_status10 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    sess11 = fields.Boolean(string="Sales Enablement")
    sale_enab_id11 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    sess_status11 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    sess12 = fields.Boolean(string="Sales Enablement")
    sale_enab_id12 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    sess_status12 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    
    
    
    
     
    second_sess1 = fields.Boolean(string="Sales Enablement")
    second_sale_enab_id1 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    second_sess_status1 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    second_sess2 = fields.Boolean(string="Sales Enablement")
    second_sale_enab_id2 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    second_sess_status2 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    second_sess3 = fields.Boolean(string="Sales Enablement")
    second_sale_enab_id3 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    second_sess_status3 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    second_sess4 = fields.Boolean(string="Sales Enablement")
    second_sale_enab_id4 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    second_sess_status4 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    second_sess4 = fields.Boolean(string="Sales Enablement")
    second_sale_enab_id4 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    second_sess_status4 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    second_sess5 = fields.Boolean(string="Sales Enablement")
    second_sale_enab_id5 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    second_sess_status5 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    second_sess6 = fields.Boolean(string="Sales Enablement")
    second_sale_enab_id6 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    second_sess_status6 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    second_sess7 = fields.Boolean(string="Sales Enablement")
    second_sale_enab_id7 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    second_sess_status7 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    second_sess8 = fields.Boolean(string="Sales Enablement")
    second_sale_enab_id8 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    second_sess_status8 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    second_sess9 = fields.Boolean(string="Sales Enablement")
    second_sale_enab_id9 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    second_sess_status9 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    second_sess10 = fields.Boolean(string="Sales Enablement")
    second_sale_enab_id10 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    second_sess_status10 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    second_sess11 = fields.Boolean(string="Sales Enablement")
    second_sale_enab_id11 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    second_sess_status11 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    second_sess12 = fields.Boolean(string="Sales Enablement")
    second_sale_enab_id12 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    second_sess_status12 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    
    third_sess1 = fields.Boolean(string="Sales Enablement")
    third_sale_enab_id1 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    third_sess_status1 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    third_sess2 = fields.Boolean(string="Sales Enablement")
    third_sale_enab_id2 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    third_sess_status2 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    third_sess3 = fields.Boolean(string="Sales Enablement")
    third_sale_enab_id3 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    third_sess_status3 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    third_sess4 = fields.Boolean(string="Sales Enablement")
    third_sale_enab_id4 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    third_sess_status4 = fields.Selection([('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    third_sess4 = fields.Boolean(string="Sales Enablement")
    third_sale_enab_id4 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    third_sess_status4 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    third_sess5 = fields.Boolean(string="Sales Enablement")
    third_sale_enab_id5 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    third_sess_status5 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    third_sess6 = fields.Boolean(string="Sales Enablement")
    third_sale_enab_id6 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    third_sess_status6 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    third_sess7 = fields.Boolean(string="Sales Enablement")
    third_sale_enab_id7 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    third_sess_status7 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    third_sess8 = fields.Boolean(string="Sales Enablement")
    third_sale_enab_id8 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    third_sess_status8 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    third_sess9 = fields.Boolean(string="Sales Enablement")
    third_sale_enab_id9 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    third_sess_status9 = fields.Selection([('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    third_sess10 = fields.Boolean(string="Sales Enablement")
    third_sale_enab_id10 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    third_sess_status10 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    third_sess11 = fields.Boolean(string="Sales Enablement")
    third_sale_enab_id11 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    third_sess_status11 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")
    
    third_sess12 = fields.Boolean(string="Sales Enablement")
    third_sale_enab_id12 = fields.Many2one('sale.enablement',string="Sale Session Enablement")
    third_sess_status12 = fields.Selection([('assigned','Assigned'),('not_achieved','Not Achieved'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Certificate Status")

    
    def od_send_mail(self,template,context):
        ir_model_data = self.env['ir.model.data']
        email_obj = self.pool.get('email.template')
        saudi_comp =6
        emp_company_id = self.company_id.id
        if emp_company_id == saudi_comp:
            template = template +'_saudi'
        template_id = ir_model_data.get_object_reference('orchid_beta_project', template)[1]
        sale_enab_id = context['sale_enab_id']
        email_obj.send_mail(self.env.cr, self.env.uid, template_id,sale_enab_id,context)
        return True
    
    def sale_cert_achieve(self,number):
        audit_temp_id = self.audit_temp_id and self.audit_temp_id.id or False
        cert_status ='cert_status'+ str(number)
        
        if audit_temp_id ==5:
            sale_cert =eval('self.'+'sale_cert_id'+str(number))
            sale_cert_id = sale_cert and sale_cert.id or False
            user_id = self.user_id and self.user_id.id or False
            domain = [('user_id','=',user_id)]
            if sale_cert_id:
                domain += [('sale_cert_id','=',sale_cert_id)]
            if domain:
                sale_cert_line = self.env['sale.certificate.attendees'].search(domain,limit=1)
                sale_cert_line.write({'status':'waiting'})
        else:
            engineer_cert_id =eval('self.'+'engineer_cert_id'+str(number))
            engineer_cert_id = engineer_cert_id and engineer_cert_id.id or False
            user_id = self.user_id and self.user_id.id or False
            domain = [('user_id','=',user_id)]
            if engineer_cert_id:
                domain += [('engineer_cert_id','=',engineer_cert_id)]
            if domain:
                engineer_cert_line = self.env['engineer.certificate.attendees'].search(domain,limit=1)
                engineer_cert_line.write({'status':'waiting'})
            
        self.sudo().write({cert_status:'waiting'})
        
    
    
    def sale_enab_achieve(self,number):
        context = self.env.context
        audit_temp_id = self.audit_temp_id and self.audit_temp_id.id or False
        sess_status ='sess_status'+ str(number)
        template = "od_sale_enablement_achieve_notification"
       
        sale_enab =eval('self.'+'sale_enab_id'+str(number))
        sale_enab_id = sale_enab and sale_enab.id or False
        user_id = self.user_id and self.user_id.id or False
        domain = [('user_id','=',user_id)]
        if sale_enab_id:
            domain += [('sale_enab_id','=',sale_enab_id)]
        if domain:
            sale_enab_line = self.env['sale.enablement.attendees'].search(domain,limit=1)
            sale_enab_line.write({'status':'waiting'})
#         ctx =  context.copy()
#         ctx['sale_enab_id'] = sale_enab_id
#         ctx['emp_name'] = self.name
#         sale_enable_obj = self.env['sale.enablement'].search([('id','=',sale_enab_id)])
#         sale_enable_obj.od_send_mail(template,ctx)
            
        self.sudo().write({sess_status:'waiting'})
    
    
    
    def second_sale_enab_achieve(self,number):
        context = self.env.context
        audit_temp_id = self.audit_temp_id and self.audit_temp_id.id or False
        sess_status ='second_sess_status'+ str(number)
        template = "od_sale_enablement_achieve_notification"
       
        sale_enab =eval('self.'+'second_sale_enab_id'+str(number))
        sale_enab_id = sale_enab and sale_enab.id or False
        user_id = self.user_id and self.user_id.id or False
        domain = [('user_id','=',user_id)]
        if sale_enab_id:
            domain += [('sale_enab_id','=',sale_enab_id)]
        if domain:
            sale_enab_line = self.env['sale.enablement.attendees'].search(domain,limit=1)
            sale_enab_line.write({'status':'waiting'})
#         ctx =  context.copy()
#         ctx['sale_enab_id'] = sale_enab_id
#         ctx['emp_name'] = self.name
#         sale_enable_obj = self.env['sale.enablement'].search([('id','=',sale_enab_id)])
#         sale_enable_obj.od_send_mail(template,context=ctx)

            
        self.sudo().write({sess_status:'waiting'})
        
    def third_sale_enab_achieve(self,number):
        context = self.env.context
        audit_temp_id = self.audit_temp_id and self.audit_temp_id.id or False
        sess_status ='third_sess_status'+ str(number)
        template = "od_sale_enablement_achieve_notification"
       
        sale_enab =eval('self.'+'third_sale_enab_id'+str(number))
        sale_enab_id = sale_enab and sale_enab.id or False
        user_id = self.user_id and self.user_id.id or False
        domain = [('user_id','=',user_id)]
        if sale_enab_id:
            domain += [('sale_enab_id','=',sale_enab_id)]
        if domain:
            sale_enab_line = self.env['sale.enablement.attendees'].search(domain,limit=1)
            sale_enab_line.write({'status':'waiting'})
#         ctx =  context.copy()
#         ctx['sale_enab_id'] = sale_enab_id
#         ctx['emp_name'] = self.name
#         sale_enable_obj = self.env['sale.enablement'].search([('id','=',sale_enab_id)])
#         sale_enable_obj.od_send_mail(template,context=ctx)

            
        self.sudo().write({sess_status:'waiting'})
        
    @api.one 
    def btn_second_sess_achieved1(self):
        self.second_sale_enab_achieve(1)
    
       
    @api.one 
    def btn_second_sess_achieved2(self):
        self.second_sale_enab_achieve(2)
        
       
    @api.one 
    def btn_second_sess_achieved3(self):
        self.second_sale_enab_achieve(3)
    
       
    @api.one 
    def btn_second_sess_achieved4(self):
        self.second_sale_enab_achieve(4)
    
       
    @api.one 
    def btn_second_sess_achieved5(self):
        self.second_sale_enab_achieve(5)
        
       
    @api.one 
    def btn_second_sess_achieved6(self):
        self.second_sale_enab_achieve(6)
    
       
    @api.one 
    def btn_second_sess_achieved7(self):
        self.second_sale_enab_achieve(7)
        
    
       
    @api.one 
    def btn_second_sess_achieved8(self):
        self.second_sale_enab_achieve(8)
        
    
       
    @api.one 
    def btn_second_sess_achieved9(self):
        self.second_sale_enab_achieve(9)
    
       
    @api.one 
    def btn_second_sess_achieved10(self):
        self.second_sale_enab_achieve(10)
    
       
    @api.one 
    def btn_second_sess_achieved11(self):
        self.second_sale_enab_achieve(11)
    
       
    @api.one 
    def btn_second_sess_achieved12(self):
        self.second_sale_enab_achieve(12)
    
    
    @api.one 
    def btn_third_sess_achieved1(self):
        self.third_sale_enab_achieve(1)
    
       
    @api.one 
    def btn_third_sess_achieved2(self):
        self.third_sale_enab_achieve(2)
        
       
    @api.one 
    def btn_third_sess_achieved3(self):
        self.third_sale_enab_achieve(3)
    
       
    @api.one 
    def btn_third_sess_achieved4(self):
        self.third_sale_enab_achieve(4)
    
       
    @api.one 
    def btn_third_sess_achieved5(self):
        self.third_sale_enab_achieve(5)
        
       
    @api.one 
    def btn_third_sess_achieved6(self):
        self.third_sale_enab_achieve(6)
    
       
    @api.one 
    def btn_third_sess_achieved7(self):
        self.third_sale_enab_achieve(7)
        
    
       
    @api.one 
    def btn_third_sess_achieved8(self):
        self.third_sale_enab_achieve(8)
        
    
       
    @api.one 
    def btn_third_sess_achieved9(self):
        self.third_sale_enab_achieve(9)
    
       
    @api.one 
    def btn_third_sess_achieved10(self):
        self.third_sale_enab_achieve(10)
    
       
    @api.one 
    def btn_third_sess_achieved11(self):
        self.third_sale_enab_achieve(11)
    
       
    @api.one 
    def btn_third_sess_achieved12(self):
        self.third_sale_enab_achieve(12)

    
    
    @api.one 
    def btn_sess_achieved1(self):
        self.sale_enab_achieve(1)
    
        
    @api.one 
    def btn_sess_achieved2(self):
        self.sale_enab_achieve(2)
        
        
    @api.one 
    def btn_sess_achieved3(self):
        self.sale_enab_achieve(3)
        
            
    @api.one 
    def btn_sess_achieved4(self):
        self.sale_enab_achieve(4)
            
    @api.one 
    def btn_sess_achieved5(self):
        self.sale_enab_achieve(5)
            
    @api.one 
    def btn_sess_achieved6(self):
        self.sale_enab_achieve(6)
            
    @api.one 
    def btn_sess_achieved7(self):
        self.sale_enab_achieve(7)
            
    @api.one 
    def btn_sess_achieved8(self):
        self.sale_enab_achieve(8)
            
    @api.one 
    def btn_sess_achieved9(self):
        self.sale_enab_achieve(9)
        
              
    @api.one 
    def btn_sess_achieved10(self):
        self.sale_enab_achieve(10)
        
              
    @api.one 
    def btn_sess_achieved11(self):
        self.sale_enab_achieve(11)
    
              
    @api.one 
    def btn_sess_achieved12(self):
        self.sale_enab_achieve(12)
        
    
    
    
    @api.one 
    def btn_sale_cert_achieved1(self):
        self.sale_cert_achieve(1)
    
    @api.one 
    def btn_sale_cert_achieved2(self):
        self.sale_cert_achieve(2)                                                                                                                                                                                   
    
    @api.one 
    def btn_sale_cert_achieved3(self):
        self.sale_cert_achieve(3)
    
    @api.one 
    def btn_sale_cert_achieved4(self):
        self.sale_cert_achieve(4)
    
    @api.one 
    def btn_sale_cert_achieved5(self):
        self.sale_cert_achieve(5)
    
    @api.one 
    def btn_sale_cert_achieved6(self):
        self.sale_cert_achieve(6)
    
    @api.one 
    def btn_sale_cert_achieved7(self):
        self.sale_cert_achieve(7)
    
    @api.one 
    def btn_sale_cert_achieved8(self):
        self.sale_cert_achieve(8)
    
    @api.one 
    def btn_sale_cert_achieved9(self):
        self.sale_cert_achieve(9)
    
    @api.one 
    def btn_sale_cert_achieved10(self):
        self.sale_cert_achieve(10)
    
      
    @api.one 
    def btn_sale_cert_achieved11(self):
        self.sale_cert_achieve(11)
    
      
    @api.one 
    def btn_sale_cert_achieved12(self):
        self.sale_cert_achieve(12)
        
   
    
    def get_product_id_from_param(self,product_param):
        parameter_obj = self.env['ir.config_parameter']
        key =[('key', '=', product_param)]
        product_param_obj = parameter_obj.search(key)
        if not product_param_obj:
            raise Warning(_('Settings Warning!'),_('NoParameter Not defined\nconfig it in System Parameters with %s'%product_param))
        product_id = product_param_obj.od_model_id and product_param_obj.od_model_id.id or False
        return product_id
    
    
    def get_default_product_id(self):
        company_id = self.env.user.company_id.id
        param ='uae_engineer_product'
        if company_id ==6:
            param ='ksa_engineer_product'
        product_id = self.get_product_id_from_param(param)
        return product_id
    
    def get_default_timesheet_journal_id(self):
        company_id = self.env.user.company_id.id
        param ='uae_engineer_timesheet'
        if company_id ==6:
            param ='ksa_engineer_timesheet'
        journal_id = self.get_product_id_from_param(param)
        return journal_id
    
    
    
    
    product_id = fields.Many2one('product.product',string="Product",domain=[('type','=','service')],default=get_default_product_id)
    journal_id = fields.Many2one('account.analytic.journal',string="Analytic Journal",default=get_default_timesheet_journal_id)
    
    
      
    
   
    
    
    
    
    def get_execution_number(self):
        mstr = 'execute'
        res = {}
        for i in range(1,13):
            fnm =mstr+str(i)
            val =eval('self'+'.'+fnm)
            res[i] = val
        result  =[]
        for key,value in res.iteritems():
            if value:
                result.append(key)
#         if len(result) >1:
#             raise Warning("Only 1 Execution Allowed and At least One Execution Needed ")
        return result[0]
    
    def get_avg_score(self,score_board):
        avg_score =0.0
        if score_board:
            avg_score =sum(score_board)/float(len(score_board))
        return avg_score
    
    def get_post_sales_vals(self,sample_id,aud_date_start,aud_date_end):
        user_id  = self.user_id and self.user_id.id
        result = []
        employee_id = self.id
        avl_time = self.get_available_time(employee_id,aud_date_start,aud_date_end) or 1
        data_model = 'project.task'
        domain = [('od_type','=','activities'),('user_id','=',user_id),('od_stage','=','done')]
        aud_date_start = aud_date_start +' 04:00:00'
        aud_date_end = aud_date_end + ' 23:58:58'
        domain.extend([('date_start','>=',aud_date_start),('date_start','<=',aud_date_end)]) 
        data_ids =self.env[data_model].search(domain)
       
        spent_time  = sum([dat.od_actual for dat in data_ids])
        utilization = (spent_time/float(avl_time)) *100
        score_board = []
        comp_data =[]
        for data in data_ids: 
            result.append((0,0,{'task_id':data.id,'score':data.od_total_kpi}))
            score_board.append(data.od_total_kpi)
            
        res = self.get_certificate_status()
        wt_cert = wt_task =cert_score =0.0
        if res.get('required'):
            wt_cert =20.0
            wt_task =80
            if res.get('achieved'):
                cert_score =100.0
        else:
            wt_cert =0.0
            wt_task =100
        mgr_score = self.get_mgr_feedback()
        if mgr_score:
            comp_data.append((0,0,
                              {'name':'Direct Manager Feedback',
                               'weight':-20,
                               'score':mgr_score,
                               'final_score':mgr_score}
                              ))

        avg_score =self.get_avg_score(score_board)
        comp_data.append((0,0,{'name':'Activity Integrity','weight':wt_task,'score':avg_score,'final_score':(wt_task/100.0)*avg_score}))
        if wt_cert:
            comp_data.append((0,0,{'name':'Certificate','weight':wt_cert,'score':cert_score,'final_score':(wt_cert/100.0)*cert_score}))
        return result,comp_data,utilization
        
    
    
    
    
    def get_x_days(self,date_start,date_end):
        fromdate = datetime.strptime(date_start, DEFAULT_SERVER_DATE_FORMAT)
        todate = datetime.strptime(date_end, DEFAULT_SERVER_DATE_FORMAT)
        daygenerator = (fromdate + timedelta(x + 1) for x in xrange((todate - fromdate).days))
        days =sum(1 for day in daygenerator)
        days = days+1
        return days  
    
    
    def get_hr_subt(self,employee_id,aud_date_start,aud_date_end):
        ex_num = self.get_execution_number()
        ex_num = str(ex_num)
        subt='hr_subt_'+ ex_num
        emp_data = self.browse(employee_id)
        eval_str ='emp_data.'+subt
        hr = eval(eval_str) or 0.0
        return hr
    def get_no_of_leave(self,employee_id,aud_date_start,aud_date_end):
        holi = self.env['hr.holidays']
        holi_ids =holi.search([('employee_id','=',employee_id),('date_from','>=',aud_date_start),('date_from','<=',aud_date_end),('state','not in',('draft','cancel','refuse','confirm')),('holiday_status_id','!=',5)])
        days =sum([a.number_of_days_temp for a in holi_ids])
        short_leave_ids = holi.search([('employee_id','=',employee_id),('date_from','>=',aud_date_start),('date_from','<=',aud_date_end),('state','not in',('draft','cancel','refuse','confirm')),('holiday_status_id','=',5)])
        hours = sum([a.od_hour for a in short_leave_ids])
        return days,hours
    def get_available_time(self,employee_id,aud_date_start,aud_date_end):
        aud_date_start = aud_date_start[:10]
        aud_date_end = aud_date_end[:10]
        fromdate = datetime.strptime(aud_date_start, DEFAULT_SERVER_DATE_FORMAT)
        todate = datetime.today()
        date_end = datetime.strptime(aud_date_end, DEFAULT_SERVER_DATE_FORMAT)
        if todate > date_end:
            todate = date_end
        daygenerator = (fromdate + timedelta(x + 1) for x in xrange((todate - fromdate).days))
        days =sum(1 for day in daygenerator if day.weekday() not in (4,5)) 
        days = days+1
        todate_str = datetime.strftime(todate,DEFAULT_SERVER_DATE_FORMAT)
        lv_days,hours = 0,0
        
        result = days
        subt = self.get_hr_subt(employee_id, aud_date_start, aud_date_end)
        result = result 
#         #ramadan month less utilization almost 6 hours
#         if aud_date_start =='2018-05-01':
#             if days >12:
#                 sdays = days-12
#                 if self.company_id.id ==6:
#                     print "company id in get availabel time function>>>>>>>>>>>>>>>>>>",self.company_id.id
#                     sdays_hrs = sdays *6
#                     rm_hrs = 12*9
#                     result = sdays_hrs + rm_hrs 
#                 else:
#                     sdays_hrs = sdays *6.5
#                     rm_hrs = 12*9
#                     result = sdays_hrs + rm_hrs 
#          
#         elif aud_date_start == '2018-06-01':
#             if days >10:
#                 sdays = days-10
#                 if self.company_id.id ==6:
#                     print "company id in get availabel time function>>>>>>>>>>>>>>>>>>",self.company_id.id
#                     sdays_hrs = sdays *9
#                     rm_hrs = 10*6
#                     result = sdays_hrs + rm_hrs 
#                 else:
#                     sdays_hrs = sdays *9
#                     rm_hrs = 10*6.5
#                     result = sdays_hrs + rm_hrs 
#             else:
#                 if self.company_id.id ==6:
#                     result = days *6.0
#                 else:
#                     result =days *6.5
#         else: 
        
        #Added by Aslam on 17/12/2019
        if self.company_id.id ==6:
            result = result *8.0
        else:
            result = result *8.5
        result = result -subt
        if not result:
            result =1
        
        return result
             
         
         
         
        if (days -lv_days)> lv_days:
            result = days -lv_days 
            if aud_date_start =='2018-05-01':
                if result >12:
                    sdays = result-12
                    if self.company_id.id ==6:
                        sdays_hrs = sdays *6
                        rm_hrs = 12*9
                        result = sdays_hrs + rm_hrs 
                    else:
                        sdays_hrs = sdays *6.5
                        rm_hrs = 12*9
                        result = sdays_hrs + rm_hrs 
            elif aud_date_start == '2018-06-01':
                if days >10:
                    sdays = days-10
                    if self.company_id.id ==6:
                        sdays_hrs = sdays *9
                        rm_hrs = 10*6.0
                        result = sdays_hrs + rm_hrs 
                    else:
                        sdays_hrs = sdays *9
                        rm_hrs = 10*6.5
                        result = sdays_hrs + rm_hrs 
                else:
                    if self.company_id.id ==6:
                        result = days *6.0
                    else:
                        result =days *6.5
                         
            else:
                #Added by Aslam on 17/12/2019
                if self.company_id.id ==6:
                    result = result *8.0
                else:
                    result = result *8.5
                result = result - hours
         
        if lv_days >22:
            #Added by Aslam on 17/12/2019
            if self.company_id.id ==6:
                result = abs((30 - lv_days) *8.0)
            else:
                result = abs((30 - lv_days) *8.5)
        if not result:
            result =1.0
        
    
    def get_cancelled_activities(self,user_id,aud_date_start,aud_date_end,engineer_task_count):
        task = self.env['project.task']
        domain = [('od_type','=','activities'),('cancel_tl_id','=',user_id),('od_stage','=','cancel_by_tl')]
        domain.extend([('date_start','>=',aud_date_start),('date_start','<=',aud_date_end)]) 
        task_ids  =task.search(domain)
        if task_ids:
            no_of_cancel_act = len(task_ids)
            tolerance =0.0
            if engineer_task_count:
                tolerance = no_of_cancel_act/float(engineer_task_count)
            if tolerance>10:
                return {'score':0.0,'weight_task':True}
            else:
                return {'score':100.0,'weight_task':True}
                
        else:
            return {'weight_task':False,'score':0.0}
    def get_escalation_activities(self,aud_date_start,aud_date_end,user_ids):
        resolved =0
        escalated =0
        for user_id in user_ids:
            domain = [('od_type','=','activities'),('user_id','=',user_id)]
            domain2=[('od_type','=','activities'),('user_id','=',user_id)]
            domain.extend([('date_start','>=',aud_date_start),('date_start','<=',aud_date_end),('od_owner_esc_status','=','resolved')]) 
            resolved_ids =self.env['project.task'].search(domain)
            domain2.extend([('date_start','>=',aud_date_start),('date_start','<=',aud_date_end),('od_owner_esc_status','in',('escalated','not_solved'))])
            resolved +=len(resolved_ids)
            escalated_ids  = self.env['project.task'].search(domain2)
            escalated += len(escalated_ids)
        total_count = resolved + escalated
        if total_count ==0:
            return {'weight_escalate':False,'score':0}
        else:   
            return {'weight_escalate':True,'score':resolved/float(total_count)}
        
    
    def get_employee_from_user(self,user):
        emp = self.search([('user_id','=',user)],limit=1)
        return emp and emp.id
    def get_ttl_vals(self,sample_id,user_id,aud_date_start,aud_date_end,audit_temp_id):
        type = audit_temp_id.type
#         user_id  = self.user_id and self.user_id.id
        employee = self.search([('user_id','=',user_id)],limit=1)
        employee_id = employee.id
        dt_start = aud_date_start
        result = []
        eng_ids = self.search([('coach_id','=',employee_id)]) 
        user_ids = [emp.user_id.id for emp in eng_ids] 
        data_model = 'project.task'
#         avl_time = self.get_available_time(dt_start,aud_date_end) or 1
        aud_date_start = aud_date_start +' 04:00:00'
        aud_date_end = aud_date_end + ' 23:58:58'
        fot_data = []
        engineer_task_count = 0
        utl_list = []
        fot_list =[]
        for user in user_ids:
            domain = [('od_type','=','activities'),('user_id','=',user),('od_stage','=','done')]
            domain.extend([('date_start','>=',aud_date_start),('date_start','<=',aud_date_end)]) 
            data_ids =self.env[data_model].search(domain)
            spent_time = sum([dat.od_actual for dat in data_ids])
            fot_board = [dat.od_end_kpi*(100/60.0) for dat in data_ids]
            fot = self.get_avg_score(fot_board)
            engineer_task_count += len(data_ids)
#             for data in data_ids:
#                 spent_time += sum([work.hours for work in data.work_ids])
            emp_id = self.get_employee_from_user(user)
            avl_time = self.get_available_time(emp_id,dt_start,aud_date_end) or 1
            utl = spent_time/float(avl_time)
            planned_time = sum([dat.b_plan_hr for dat in data_ids if dat.project_id.od_type_of_project != 'comp_gen'])
            planned_utl = planned_time/float(avl_time)
            result.append((0,0,{'user_id':user,'available_time':avl_time,'actual_time_spent':spent_time,'utl':(spent_time/avl_time)*100.0,'planned_time':planned_time,'planned_utl':planned_utl*100.0}))
            fot_data.append((0,0,{'user_id':user,'fot':fot}))
            pl_utl  = (planned_utl/0.7)
            if pl_utl>1.0:
                pl_utl = 1.0
            utl_list.append(pl_utl)
            fot_list.append(fot)
            
        utl_score =  self.get_avg_score(utl_list)  
        fot_score  = self.get_avg_score(fot_list)   
        cancelled_activities = self.get_cancelled_activities(user_id,aud_date_start,aud_date_end,engineer_task_count) 
        escalation_activities = self.get_escalation_activities(aud_date_start,aud_date_end,user_ids)
        weight_escalate = escalation_activities.get('weight_escalate',False)
        weight_task_cancel = cancelled_activities.get('weight_task',False)
        wt_esc = wt_tsk_cncl = wt_utl = wt_fot =0.0
        if weight_escalate and not weight_task_cancel:
            wt_esc= 10+ (10 *(30/70.0))
            wt_tsk_cncl =0.0
            wt_utl = 30+ (30 *(30/70.0))
            wt_fot = 30+ (30 *(30/70.0))
        if not weight_escalate and weight_task_cancel:
            wt_esc= 0.0
            wt_tsk_cncl =30+ (30 *(10/90.0))
            wt_utl = 30+ (30 *(10/90.0))
            wt_fot = 30+ (30 *(10/90.0))
        if not weight_escalate and not weight_task_cancel:
            wt_esc= 0.0
            wt_tsk_cncl =0.0
            wt_utl = 30+ (30 *(40/60.0))
            wt_fot = 30+ (30 *(40/60.0))
                
        if weight_escalate and weight_task_cancel:
                
            wt_esc= 10
            wt_tsk_cncl =30
            wt_utl = 30
            wt_fot = 30
        tsk_cncl_scr = cancelled_activities.get('score',0.0)
        esc_scr =escalation_activities.get('score',0.0)
        comp_data = []
        mgr_score = self.get_mgr_feedback()
        if mgr_score:
            comp_data.append((0,0,
                              {'name':'Direct Manager Feedback',
                               'weight':-20,
                               'score':mgr_score,
                               'final_score':mgr_score}
                              ))

        comp_data.append((0,0,{'name':'Finished On Time','weight':wt_fot,'score':fot_score,'final_score':(wt_fot/100.0) * fot_score}))
        comp_data.append((0,0,{'name':'Team Utilization','weight':wt_utl,'score':utl_score*100,'final_score':wt_utl * utl_score}))
        if wt_tsk_cncl:
            comp_data.append((0,0,{'name':'Percentage Of Cancelled Activities','weight':wt_tsk_cncl,'score':tsk_cncl_scr,'final_score':(wt_tsk_cncl/100.0) * tsk_cncl_scr}))
        if wt_esc:
            comp_data.append((0,0,{'name':'Escalation From Activity Owner','weight':wt_esc,'score':esc_scr*100,'final_score':wt_esc * esc_scr})) 
        return result,fot_data,comp_data
    
    
    def get_tech_hoo_comp_line(self,fot_score,utl_score,c_score,c_wt):
        comp_data = []
        wt_fot =.1 
        wt_utl =.1
        wt_cancel =.1 
        exclude_wt =0.0 
        if not c_wt:
            exclude_wt += wt_cancel
            wt_cancel =0.0
        if exclude_wt:
            wt_fot =  wt_fot + .05
            wt_utl=wt_utl + .05
         
        if wt_fot:
            score = fot_score 
            if score>100.0:
                score=100.0
            final_score = wt_fot * score
            comp_data.append((0,0,{'name':'Average of Team -Finished On Time','weight':wt_fot*100.0,'final_score':final_score,'score':score}))
        
        if wt_utl:
            score = utl_score 
            if score>100.0:
                score=100.0
            final_score = wt_utl * score
            comp_data.append((0,0,{'name':'Average of Team Utilization','weight':wt_utl*100.0,'final_score':final_score,'score':score}))
        if wt_cancel:
            score = c_score 
            if score>100.0:
                score=100.0
            final_score = wt_cancel * score
            comp_data.append((0,0,{'name':'Average of Team Percentage Of Cancelled Activities','weight':wt_cancel*100.0,'final_score':final_score,'score':score}))
        return comp_data
    def get_tech_comp_hoo(self,tl_comp_line):
        res =[]
        fot_score_board =[]
        utl_score_board = []
        c_board =[]
        for _,_,val in tl_comp_line:
            if val.get('name','') == 'Finished On Time':
                score = val.get('score')
                fot_score_board.append(score)
            
            if val.get('name','') == 'Team Utilization':
                score = val.get('score')
                utl_score_board.append(score)
            
            if val.get('name','') == 'Percentage Of Cancelled Activities':
                score = val.get('score')
                c_board.append(score)
        c_wt = False
        fot_score = self.get_avg_score(fot_score_board)
        utl_score  = self.get_avg_score(utl_score_board)
        c_score = self.get_avg_score(c_board)
        if c_board:
            c_wt = True
        tech_comp_line= self.get_tech_hoo_comp_line(fot_score, utl_score, c_score, c_wt)
        return tech_comp_line
    
    def get_pmo_score_from_comp(self,pmo_comp_line):
        final_score =0.0
        for _,_,val in pmo_comp_line:
            final_score += val.get('final_score')
        return final_score
    def get_hoo_data(self,sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id):
        employee = self.search([('user_id','=',user_id)],limit=1)
        employee_id = employee.id
        team_ids = self.search([('parent_id','=',employee_id)]) 
        tl_user_ids = [emp.user_id.id for emp in team_ids if (emp.audit_temp_id and emp.audit_temp_id.type =='ttl')]
        
        
        utl_vals = []
        fot_vals = []
        tl_comp_line = []
        for user in tl_user_ids:
            utl_data,fot_data,ttl_comp = self.get_ttl_vals(sample_id, user, aud_date_start, aud_date_end, audit_temp_id)
            utl_vals += utl_data
            fot_vals += fot_data 
            tl_comp_line += ttl_comp
        
        sd_user_ids = [emp.user_id.id for emp in team_ids if (emp.audit_temp_id and emp.audit_temp_id.type =='sde')]
        team_score = []
        team_vals =[]
        for user in sd_user_ids:
            dum1,dum2,dum3,comp_line = self.get_sde_data_ksa(sample_id,user, aud_date_start, aud_date_end, audit_temp_id)
            
            score = self.get_score_from_comp_data(comp_line)
            team_score.append(score)
            team_vals.append((0,0,{'user_id':user,'score':score}))
        #Commenetd by Aslam on 01/06/2020 to remove FOT and Team utilisation from khalid eqthifan
        #tech_comp_line = self.get_tech_comp_hoo(tl_comp_line)
        open_projects,closed_projects,pmo_comp_line = self.get_pmo_dir_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
        pmo_score = self.get_pmo_score_from_comp(pmo_comp_line)
        pmo_comp_line = [(0,0,{'name':'Cash Flow Management','weight':70,'score':pmo_score,'final_score':pmo_score* 0.7})]
        team_avg_score = self.get_avg_score(team_score)
        if team_avg_score >100:
            team_avg_score =100.0
        sde_comp_line = [(0,0,{'name':'Average Of Service Desk Engineer','weight':30,'score':team_avg_score,'final_score':team_avg_score* 0.3})]
        mgr_score = self.get_mgr_feedback()
        if mgr_score:
            sde_comp_line.append((0,0,
                              {'name':'Direct Manager Feedback',
                               'weight':-20,
                               'score':mgr_score,
                               'final_score':mgr_score}
                              ))
        #Commenetd by Aslam on 01/06/2020 to remove FOT and Team utilisation from khalid eqthifan
        #comp_line = tech_comp_line + pmo_comp_line + sde_comp_line
        comp_line = pmo_comp_line + sde_comp_line
        
        
        return utl_vals,fot_vals,open_projects,closed_projects,team_vals,comp_line
    def get_tech_cons_ps_vals(self,sample_id,aud_date_start,aud_date_end,audit_temp_id):
        type = audit_temp_id.type
        usr_id  = self.user_id and self.user_id.id
        employee_id = self.id
        dt_start = aud_date_start
        result = []
        eng_ids = self.search([('coach_id','=',employee_id)]) 
        user_ids = [emp.user_id.id for emp in eng_ids if (emp.audit_temp_id and emp.audit_temp_id.type =='post_sales')] + [usr_id]
        data_model = 'project.task'
#         avl_time = self.get_available_time(dt_start,aud_date_end) or 1
        aud_date_start = aud_date_start +' 04:00:00'
        aud_date_end = aud_date_end + ' 23:58:58'
        fot_data = []
        engineer_task_count = 0
        utl_list = []
        fot_list =[]
        for user_id in user_ids:
            domain = [('od_type','=','activities'),('user_id','=',user_id),('od_stage','=','done')]
            domain.extend([('date_start','>=',aud_date_start),('date_start','<=',aud_date_end)]) 
            data_ids =self.env[data_model].search(domain)
            spent_time = sum([dat.od_actual for dat in data_ids])
            fot_board = [dat.od_end_kpi*(100/60.0) for dat in data_ids]
            fot = self.get_avg_score(fot_board)
            engineer_task_count += len(data_ids)
#             for data in data_ids:
#                 spent_time += sum([work.hours for work in data.work_ids])
            emp_id = self.get_employee_from_user(user_id)
            avl_time = self.get_available_time(emp_id,dt_start,aud_date_end) or 1
            utl = spent_time/float(avl_time)
            planned_time = sum([dat.b_plan_hr for dat in data_ids if dat.project_id.od_type_of_project != 'comp_gen'])
            planned_utl = planned_time/float(avl_time)
            if user_id !=usr_id:
                result.append((0,0,{'user_id':user_id,'available_time':avl_time,'actual_time_spent':spent_time,'utl':(spent_time/avl_time)*100.0,'planned_time':planned_time,'planned_utl':planned_utl*100.0}))
                pl_utl  = (planned_utl/0.7)
                if pl_utl >1.0:
                    pl_utl = 1.0
                utl_list.append(pl_utl)
            if data_ids:
                fot_data.append((0,0,{'user_id':user_id,'fot':fot}))
                fot_list.append(fot)
            
        utl_score =  self.get_avg_score(utl_list)  
        fot_score  = self.get_avg_score(fot_list)   
        cancelled_activities = self.get_cancelled_activities(self.user_id.id,aud_date_start,aud_date_end,engineer_task_count) 
        escalation_activities = self.get_escalation_activities(aud_date_start,aud_date_end,user_ids)
        weight_escalate = escalation_activities.get('weight_escalate',False)
        weight_task_cancel = cancelled_activities.get('weight_task',False)
        wt_esc = wt_tsk_cncl = wt_utl = wt_fot =0.0
        if weight_escalate and not weight_task_cancel:
            wt_esc= 10+ (10 *(30/70.0))
            wt_tsk_cncl =0.0
            wt_utl = 30+ (30 *(30/70.0))
            wt_fot = 30+ (30 *(30/70.0))
        if not weight_escalate and weight_task_cancel:
            wt_esc= 0.0
            wt_tsk_cncl =30+ (30 *(10/90.0))
            wt_utl = 30+ (30 *(10/90.0))
            wt_fot = 30+ (30 *(10/90.0))
        if not weight_escalate and not weight_task_cancel:
            wt_esc= 0.0
            wt_tsk_cncl =0.0
            wt_utl = 30+ (30 *(40/60.0))
            wt_fot = 30+ (30 *(40/60.0))
                
        if weight_escalate and weight_task_cancel:
                
            wt_esc= 10
            wt_tsk_cncl =30
            wt_utl = 30
            wt_fot = 30
        tsk_cncl_scr = cancelled_activities.get('score',0.0)
        esc_scr =escalation_activities.get('score',0.0)
        comp_data = []
        comp_data.append((0,0,{'name':'Finished On Time','weight':wt_fot,'score':fot_score,'final_score':(wt_fot/100.0) * fot_score}))
        comp_data.append((0,0,{'name':'Team Utilization','weight':wt_utl,'score':utl_score*100,'final_score':wt_utl * utl_score}))
        if wt_tsk_cncl:
            comp_data.append((0,0,{'name':'Percentage Of Cancelled Activities','weight':wt_tsk_cncl,'score':tsk_cncl_scr,'final_score':(wt_tsk_cncl/100.0) * tsk_cncl_scr}))
        if wt_esc:
            comp_data.append((0,0,{'name':'Escalation From Activity Owner','weight':wt_esc,'score':esc_scr*100,'final_score':wt_esc * esc_scr})) 
        return result,fot_data,comp_data
    
    def get_opportunity_score(self, data):
        score_list = []
        financial_proposal = data.financial_proposal
        fp_req = data.od_req_on_7
        fp_finished_on = data.finished_on_7
        
        #Finished case checking for On time finishing
        if financial_proposal and fp_finished_on:
            if fp_finished_on <= fp_req:
                score_list.append(100.0)
            else:
                score_list.append(0.0)
                
        if data.budget_proposal and data.od_budg_finished_on:
            if data.od_budg_finished_on <= data.od_budg_req_on:
                score_list.append(100.0)
            else:
                score_list.append(0.0)
        if data.management_presentation and data.finished_on_1:
            if data.finished_on_1 <= data.man_pre_date:
                score_list.append(100.0)
            else:
                score_list.append(0.0)
        if data.technical_presentation and data.finished_on_2:
            if data.finished_on_2 <= data.tech_pre_date:
                score_list.append(100.0)
            else:
                score_list.append(0.0)
        if data.help_customer_rfp and data.finished_on_4:
            if data.finished_on_4 <= data.rfp_date:
                score_list.append(100.0)
            else:
                score_list.append(0.0)
        if data.tech_proposal and data.finished_on_5:
            if data.finished_on_5 <= data.proposal_date:
                score_list.append(100.0)
            else:
                score_list.append(0.0)
        if data.hld_proposal and data.finished_on_6:
            if data.finished_on_6 <= data.hld_date:
                score_list.append(100.0)
            else:
                score_list.append(0.0)
        if data.site_survey and data.finished_on_8:
            if data.finished_on_8 <= data.od_req_on_8:
                score_list.append(100.0)
            else:
                score_list.append(0.0)
        if data.req_tech_workshop and data.finished_on_9:
            if data.finished_on_9 <= data.od_req_on_9:
                score_list.append(100.0)
            else:
                score_list.append(0.0)
        if data.proof_of_concept and data.finished_on_3:
            if data.finished_on_3 <= data.proof_date:
                score_list.append(100.0)
            else:
                score_list.append(0.0)             
        #Not finished case    
        if financial_proposal and not fp_finished_on:
            score_list.append(0.0)
        if data.budget_proposal and not data.od_budg_finished_on:
            score_list.append(0.0)
        if data.management_presentation and not data.finished_on_1:
            score_list.append(0.0)
        if data.technical_presentation and not data.finished_on_2:
            score_list.append(0.0)
        if data.help_customer_rfp and not data.finished_on_4:
            score_list.append(0.0)
        if data.tech_proposal and not data.finished_on_5:
            score_list.append(0.0)
        if data.hld_proposal and not data.finished_on_6:
            score_list.append(0.0)
        if data.site_survey and not data.finished_on_8:
            score_list.append(0.0)
        if data.req_tech_workshop and not data.finished_on_9:
            score_list.append(0.0)
        if data.proof_of_concept and not data.finished_on_3:
            score_list.append(0.0)
        #check 0 val in score list    
        if 0.0 in score_list:
            return 0.0
        else:
            return 100.0
    
    #for technology consultant kpi
    def get_presale_data(self,user_id, aud_date_start, aud_date_end, audit_temp_id):
        result = []
        data_model = 'crm.lead'
        domain = [('stage_id','not in',(7,8)),('od_responsible_id','=',user_id)]
        aud_date_start = aud_date_start 
        aud_date_end = aud_date_end 
        domain.extend([('od_req_on_7','>=',aud_date_start),('od_req_on_7','<=',aud_date_end)])
        domain1 = [('stage_id','=',7),('od_responsible_id','=',user_id)]
        domain1.extend([('od_req_on_7','>=',aud_date_start),('od_req_on_7','<=',aud_date_end)])
        # for Lost, if there is no cost sheet at all (not created), then it should not be considered.
        lost_opp_ids = self.env[data_model].search(domain1)
        lost_opp_with_cost_sheet_ids = []
        for opp in lost_opp_ids:
            cost_sheet = self.env['od.cost.sheet'].search([('lead_id','=',opp.id)])
            if cost_sheet:
                lost_opp_with_cost_sheet_ids.append(opp.id)
        lost_opp_data_ids = self.env[data_model].search([('id','in',lost_opp_with_cost_sheet_ids)])
        data_ids =self.env[data_model].search(domain) + lost_opp_data_ids
        score_boards = []
        comp_data =[]
        for data in data_ids:
            score = self.get_opportunity_score(data)
            score_boards.append(score) 
            result.append((0,0,{'opp_id':data.id,'score':score,'user_id':user_id,'required_date': data.od_req_on_7}))
        avg_score = self.get_avg_score(score_boards)
        return result,avg_score
    
    #for presales kpi
    def get_presale_vals(self,sample_id, aud_date_start, aud_date_end, audit_temp_id):
        user_id  = self.user_id and self.user_id.id
        result = []
        data_model = 'crm.lead'
        domain = [('stage_id','not in',(7,8)),('od_responsible_id','=',user_id),('od_approval_state','=','approved')]
        aud_date_start = aud_date_start 
        aud_date_end = aud_date_end 
        domain.extend([('od_req_on_7','>=',aud_date_start),('od_req_on_7','<=',aud_date_end)]) 
        domain1 = [('stage_id','=',7),('od_responsible_id','=',user_id)]
        domain1.extend([('od_req_on_7','>=',aud_date_start),('od_req_on_7','<=',aud_date_end)])
        # for Lost, if there is no cost sheet at all (not created), then it should not be considered.
        lost_opp_ids = self.env[data_model].search(domain1)
        lost_opp_with_cost_sheet_ids = []
        for opp in lost_opp_ids:
            cost_sheet = self.env['od.cost.sheet'].search([('lead_id','=',opp.id)])
            if cost_sheet:
                lost_opp_with_cost_sheet_ids.append(opp.id)
        lost_opp_data_ids = self.env[data_model].search([('id','in',lost_opp_with_cost_sheet_ids)])
        data_ids =self.env[data_model].search(domain) + lost_opp_data_ids
        score_boards = []
        comp_data =[]
        for data in data_ids:
            score = self.get_opportunity_score(data)
            score_boards.append(score) 
            result.append((0,0,{'opp_id':data.id,'score':score,'user_id':user_id, 'required_date': data.od_req_on_7}))
        avg_score = self.get_avg_score(score_boards)
        res = self.get_certificate_status()
        wt_cert = wt_opp =cert_score =0.0
        
        if res.get('required'):
            wt_cert =20.0
            wt_opp =80
            if res.get('achieved'):
                cert_score =100.0
        else:
            wt_cert =0.0
            wt_opp =100
        comp_data.append((0,0,{'name':'Productivity','weight':wt_opp,'score':avg_score,'final_score':(wt_opp/100.0)*avg_score}))
        if wt_cert:
            comp_data.append((0,0,{'name':'Certificate','weight':wt_cert,'score':cert_score,'final_score':(wt_cert/100.0)*cert_score}))
        
        mgr_score = self.get_mgr_feedback()
        if mgr_score:
            comp_data.append((0,0,
                              {'name':'Direct Manager Feedback',
                               'weight':-20,
                               'score':mgr_score,
                               'final_score':mgr_score}
                              ))
        
        return result,comp_data
    
    def get_presale_mgr_vals_tc(self,sample_id, aud_date_start, aud_date_end, audit_temp_id):
        user_id  = self.user_id and self.user_id.id
        employee_id = self.id
        team_ids = self.search([('coach_id','=',employee_id)]) 
        user_ids = [emp.user_id.id for emp in team_ids if (emp.audit_temp_id and emp.audit_temp_id.type=='pre_sales')]
        result = []
        team_score =[]
        team_vals =[] 
        for uid in user_ids:
            data,avg_score = self.get_presale_data(uid, aud_date_start, aud_date_end, audit_temp_id)
            team_score.append(avg_score)
            team_vals.append((0,0,{'user_id':uid,'score':avg_score}))
            result.extend(data)
            
        team_avg_score =  self.get_avg_score(team_score)  
        comp_data =[(0,0,{'name':'Productivity','weight':100.0,'score':team_avg_score,'final_score':team_avg_score})]
        return result,team_vals,comp_data
    
    def get_presale_mgr_vals(self,sample_id, aud_date_start, aud_date_end, audit_temp_id):
        user_id  = self.user_id and self.user_id.id
        employee_id = self.id
        team_ids = self.search([('coach_id','=',employee_id)]) 
        user_ids = [emp.user_id.id for emp in team_ids if (emp.audit_temp_id and emp.audit_temp_id.type=='pre_sales')] + [user_id]
        result = []
        team_score =[]
        team_vals =[]
        for uid in user_ids:
            data,avg_score = self.get_presale_data(uid, aud_date_start, aud_date_end, audit_temp_id)
            team_score.append(avg_score)
            team_vals.append((0,0,{'user_id':uid,'score':avg_score}))
            result.extend(data)
            
        team_avg_score =  self.get_avg_score(team_score)
        mgr_score = self.get_mgr_feedback()
        

        comp_data =[(0,0,{'name':'Productivity','weight':100,'score':team_avg_score,'final_score':team_avg_score})]
        if mgr_score:
            comp_data.append((0,0,
                              {'name':'Direct Manager Feedback',
                               'weight':-20,
                               'score':mgr_score,
                               'final_score':mgr_score}
                              ))
        return result,team_vals,comp_data
    def get_sales_commit_data(self,sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id):
        lead_ids =self.env['crm.lead'].search([('stage_id','=',5)]).ids
        total_gp = 0.0
        month_start = aud_date_end[:8]+'01'
        result =[]
        domain = [('sales_acc_manager','=',user_id),('status','=','active'),('lead_id','in', lead_ids)]
        domain.extend([('op_expected_booking','>=',aud_date_start),('op_expected_booking','<=',aud_date_end)])
        domain1 = domain + [('state','not in',('approved','done','cancel','modify','change','analytic_change','change_processed','redistribution_processed','draft','design_ready','submitted'))]
        domain2 = domain + [('state','in',('draft','design_ready','submitted'))]
        
#         domain3 = domain + [('state','in',('approved','done','modify','change','analytic_change')),('op_expected_booking','>=',aud_date_start),('op_expected_booking','<=',month_start)]
        
        sheet_ids =self.env['od.cost.sheet'].search(domain1)
        
        for sheet in sheet_ids:
            stage_id = sheet.op_stage_id and sheet.op_stage_id.id 
            if stage_id not in (7,8,13):
                gp =sheet.total_gp
                result.append((0,0,{'cost_sheet_id':sheet.id,'gp':gp,'user_id':user_id}))
                total_gp += gp
        
#         sheet_ids = self.env['od.cost.sheet'].search(domain3)
#         for sheet in sheet_ids:
#             stage_id = sheet.op_stage_id and sheet.op_stage_id.id 
#             if stage_id not in (7,8):
#                 gp =sheet.total_gp
#                 result.append((0,0,{'cost_sheet_id':sheet.id,'gp':gp}))
#                 total_gp += gp
        
        sheet_ids =self.env['od.cost.sheet'].search(domain2)
        for sheet in sheet_ids:
            stage_id = sheet.op_stage_id and sheet.op_stage_id.id 
            if stage_id ==5:
                gp = sheet.total_gp
                result.append((0,0,{'cost_sheet_id':sheet.id,'gp':gp,'user_id':user_id}))
                total_gp +=gp
        return result,total_gp
    def get_sales_achieved_data(self,sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id):
        
        result =[]
        total_gp = 0.0
        domain = [('sales_acc_manager','=',user_id),('status','=','active')]
        domain.extend([('approved_date','>=',aud_date_start),('approved_date','<=',aud_date_end)])
        domain1 = domain + [('state','in',('approved','done','modify','change','analytic_change','change_processed','redistribution_processed',))]
        sheet_ids =self.env['od.cost.sheet'].search(domain1)
        for sheet in sheet_ids:
            gp = sheet.total_gp
            result.append((0,0,{'cost_sheet_id':sheet.id,'gp':sheet.total_gp,'user_id':user_id}))
            total_gp +=gp
        return result,total_gp
    def get_sales_acc_mgr_component(self,commit_total,achieved_total):
        target = self.annual_target/12.0
        result =0.0
        exclude_wt = 0.0
        comp_data =[]
        if target:
            if achieved_total >= commit_total:
#                 result = commit_total/max(target,commit_total)
                result = commit_total/target
                if result >3.0:
                    result =3
            elif achieved_total < commit_total:
                result = achieved_total/max(target,commit_total)
#                 result = achieved_total/target
                if result > 1.5:
                    result =1.5
        if result <.5:
            result =0.0
            
        
        wt_cmt = 80.0
        wt_cert =0.0
        wt_sess =0.0

        mgr_score = self.get_mgr_feedback()
        cert = self.get_certificate_status()
        cert_ach = cert.get('achieved',False)
        cert_req = cert.get('required',False)
        
        sess = self.get_sess_enab_status()
        sess_ach = sess.get('achieved',False)
        sess_req = sess.get('required',False)
        
        second_sess = self.get_second_sess_enab_status()
        second_sess_ach = second_sess.get('achieved',False)
        second_sess_req = second_sess.get('required',False)
        
        third_sess = self.get_third_sess_enab_status()
        third_sess_ach = third_sess.get('achieved',False)
        third_sess_req = third_sess.get('required',False)
        
        
        
        
        if cert_req:
            wt_cert =10  
        if not cert_req:
            exclude_wt += 10     
        if sess_req:
            wt_sess =10.0
        
        if not sess_req:
            exclude_wt += 10 
        
        if exclude_wt:
            wt_cmt =  wt_cmt + exclude_wt
            
        if second_sess_req:
           
            wt_sess =5
            wt_sess2=5
        if third_sess_req:
            wt_sess= wt_sess2 = wt_sess3 =10.0/3.0   
            
        
        comp_data.append((0,0,
                              {'name':'Commitment Performance',
                               'weight':wt_cmt,
                               'score':result*100,
                               'final_score':wt_cmt *result}
                              ))
            
        if cert_req:
            cert_score  =0.0
            if cert_ach:
                cert_score = 100
            comp_data.append((0,0,
                              {'name':'Certificate',
                               'weight':wt_cert,
                               'score':cert_score,
                               'final_score':(wt_cert/100.0)*cert_score}
                              ))
        
        if sess_req:
            sess_score  =0.0
            if sess_ach:
                sess_score = 100
            comp_data.append((0,0,
                              {'name':'Session Enablement',
                               'weight':wt_sess,
                               'score':sess_score,
                               'final_score':(wt_sess/100.0)*sess_score}
                              ))
        if second_sess_req:
            sess_score  =0.0
            if second_sess_ach:
                sess_score = 100
            comp_data.append((0,0,
                              {'name':'Session Enablement',
                               'weight':wt_sess2,
                               'score':sess_score,
                               'final_score':(wt_sess2/100.0)*sess_score}
                              ))
        
        if third_sess_req:
            sess_score  =0.0
            if third_sess_ach:
                sess_score = 100
            comp_data.append((0,0,
                              {'name':'Session Enablement',
                               'weight':wt_sess3,
                               'score':sess_score,
                               'final_score':(wt_sess3/100.0)*sess_score}
                              ))
            
        if mgr_score:
            comp_data.append((0,0,
                              {'name':'Direct Manager Feedback',
                               'weight':-20,
                               'score':mgr_score,
                               'final_score':mgr_score}
                              ))
        
        return comp_data,target
    
    
    
    
    def get_sales_spl_commit_data(self,sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id):
        
        total_gp = 0.0
        month_start = aud_date_end[:8]+'01'
        result =[]
        domain = [('sale_team_id','=',33),('status','=','active')]
        domain.extend([('op_expected_booking','>=',aud_date_start),('op_expected_booking','<=',aud_date_end)])
        domain1 = domain + [('state','not in',('approved','done','cancel','modify','change','analytic_change','change_processed','redistribution_processed','draft','design_ready','submitted'))]
        domain2 = domain + [('state','in',('draft','design_ready','submitted'))]
        
#         domain3 = domain + [('state','in',('approved','done','modify','change','analytic_change')),('op_expected_booking','>=',aud_date_start),('op_expected_booking','<=',month_start)]
        
        sheet_ids =self.env['od.cost.sheet'].search(domain1)
        
        for sheet in sheet_ids:
            stage_id = sheet.op_stage_id and sheet.op_stage_id.id 
            if stage_id not in (7,8,13):
                gp =sheet.total_gp
                result.append((0,0,{'cost_sheet_id':sheet.id,'gp':gp}))
                total_gp += gp
        
#         sheet_ids = self.env['od.cost.sheet'].search(domain3)
#         for sheet in sheet_ids:
#             stage_id = sheet.op_stage_id and sheet.op_stage_id.id 
#             if stage_id not in (7,8):
#                 gp =sheet.total_gp
#                 result.append((0,0,{'cost_sheet_id':sheet.id,'gp':gp}))
#                 total_gp += gp
        
        sheet_ids =self.env['od.cost.sheet'].search(domain2)
        for sheet in sheet_ids:
            stage_id = sheet.op_stage_id and sheet.op_stage_id.id 
            if stage_id ==5:
                gp = sheet.total_gp
                result.append((0,0,{'cost_sheet_id':sheet.id,'gp':gp,'user_id':user_id}))
                total_gp +=gp
        return result,total_gp
    def get_sales_spl_achieved_data(self,sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id):
        
        result =[]
        total_gp = 0.0
        domain = [('sale_team_id','=',33),('status','=','active')]
        domain.extend([('op_expected_booking','>=',aud_date_start),('op_expected_booking','<=',aud_date_end)])
        domain1 = domain + [('state','in',('approved','done','modify','change','analytic_change','change_processed','redistribution_processed'))]
        sheet_ids =self.env['od.cost.sheet'].search(domain1)
        for sheet in sheet_ids:
            gp = sheet.total_gp
            result.append((0,0,{'cost_sheet_id':sheet.id,'gp':sheet.total_gp,'user_id':user_id}))
            total_gp +=gp
        return result,total_gp
    def get_sales_spl_component(self,commit_total,achieved_total):
        
        result =0.0
        exclude_wt = 0.0
        comp_data =[]
        
        if commit_total:
            result = achieved_total/commit_total 
            if result >1.5:
                result =1.5
        
        mgr_score = self.get_mgr_feedback()
        cert = self.get_certificate_status()
        cert_ach = cert.get('achieved',False)
        cert_req = cert.get('required',False)
        sess = self.get_sess_enab_status()
        sess_ach = sess.get('achieved',False)
        sess_req = sess.get('required',False)
        if not mgr_score:
            exclude_wt += 10
        if not cert_req:
            exclude_wt += 10
        
        wt_cmt = 80.0
        wt_cert =10.0
        wt_sess =10.0
        if exclude_wt:
            wt_cmt =  wt_cmt + (wt_cmt*exclude_wt)/float(100-exclude_wt)
            wt_cert =  wt_cert + (wt_cert*exclude_wt)/float(100-exclude_wt)
            wt_sess =  wt_sess + (wt_sess*exclude_wt)/float(100-exclude_wt)
        
        comp_data.append((0,0,
                              {'name':'Commitment Performance',
                               'weight':wt_cmt,
                               'score':result*100,
                               'final_score':wt_cmt *result}
                              ))
            
        if cert_req:
            cert_score  =0.0
            if cert_ach:
                cert_score = 100
            comp_data.append((0,0,
                              {'name':'Certificate',
                               'weight':wt_cert,
                               'score':cert_score,
                               'final_score':(wt_cert/100.0)*cert_score}
                              ))
        
         
        if sess_req:
            sess_score  =0.0
            if sess_ach:
                sess_score = 100
            comp_data.append((0,0,
                              {'name':'Session Enablement',
                               'weight':wt_sess,
                               'score':sess_score,
                               'final_score':(wt_sess/100.0)*sess_score}
                              ))
        if mgr_score:
            comp_data.append((0,0,
                              {'name':'Direct Manager Feedback',
                               'weight':-20,
                               'score':mgr_score,
                               'final_score':mgr_score}
                              ))
         
        return comp_data
    
    def get_sales_acc_mgr_component_sm(self,emp_id,commit_total,achieved_total):
        
        sale_enab_data =[]
        sale_enab_score =0.0
        execution_num = self.get_execution_number()
        emp = self.browse(emp_id)
        usr_id = emp.user_id and emp.user_id.id
        target = emp.annual_target/12.0
        result =0.0
        exclude_wt = 0.0
        comp_data =[]
        comp_data2=[]
        if target:
            if achieved_total >= commit_total:
#                 result = commit_total/max(target,commit_total)
                result = commit_total/target
                if result >3.0:
                    result =3
            elif achieved_total < commit_total:
                result = achieved_total/max(target,commit_total)
#                 result = achieved_total/target
                if result > 1.5:
                    result =1.5
        result2= result
        if result2 <.5:
            result2=0.0
            
        
        wt_cmt = 80.0
        wt_cert =0.0
        wt_sess =0.0

        mgr_score = emp.get_mgr_feedback(execution_num=execution_num)
        cert = emp.get_certificate_status(execution_num=execution_num)
        cert_ach = cert.get('achieved',False)
        cert_req = cert.get('required',False)
        
        sess = emp.get_sess_enab_status(execution_num=execution_num)
        sess_ach = sess.get('achieved',False)
        sess_req = sess.get('required',False)
        
        second_sess = emp.get_second_sess_enab_status(execution_num=execution_num)
        second_sess_ach = second_sess.get('achieved',False)
        second_sess_req = second_sess.get('required',False)
        
        third_sess = emp.get_third_sess_enab_status(execution_num=execution_num)
        third_sess_ach = third_sess.get('achieved',False)
        third_sess_req = third_sess.get('required',False)
        
        
        
        
        if cert_req:
            wt_cert =10  
        if not cert_req:
            exclude_wt += 10     
        if sess_req:
            wt_sess =10.0
        
        if not sess_req:
            
            exclude_wt += 10
        
        print "cert REQ...............: ",cert_req
        
        if exclude_wt:
            wt_cmt =  wt_cmt + exclude_wt
        
        print "WT CMT ...........:",wt_cmt
        if second_sess_req:
           
            wt_sess =5
            wt_sess2=5
        if third_sess_req:
            wt_sess= wt_sess2 = wt_sess3 =10.0/3.0   
            
        
        comp_data.append((0,0,
                              {'name':'Commitment Performance',
                               'weight':wt_cmt,
                               'score':result*100,
                               'final_score':wt_cmt *result}
                              ))
        
        comp_data2.append((0,0,
                              {'name':'Commitment Performance',
                               'weight':wt_cmt,
                               'score':result2*100,
                               'final_score':wt_cmt *result2}
                              ))
            
        if cert_req:
            cert_score  =0.0
            if cert_ach:
                cert_score = 100
            comp_data.append((0,0,
                              {'name':'Certificate',
                               'weight':wt_cert,
                               'score':cert_score,
                               'final_score':(wt_cert/100.0)*cert_score}
                              ))
            comp_data2.append((0,0,
                              {'name':'Certificate',
                               'weight':wt_cert,
                               'score':cert_score,
                               'final_score':(wt_cert/100.0)*cert_score}
                              ))
        
        if sess_req:
            sess_score  =0.0
            if sess_ach:
                sess_score = 100
            comp_data.append((0,0,
                              {'name':'Session Enablement',
                               'weight':wt_sess,
                               'score':sess_score,
                               'final_score':(wt_sess/100.0)*sess_score}
                              ))
            sale_enab_data.append((0,0,{'name':'Sale Enab Slot 1','kpi_point':wt_sess,'score':(wt_sess/100.0)*sess_score,'achieved':sess_ach,'user_id':usr_id}))
            sale_enab_score +=(wt_sess/100.0)*sess_score
            
            comp_data2.append((0,0,
                              {'name':'Session Enablement',
                               'weight':wt_sess,
                               'score':sess_score,
                               'final_score':(wt_sess/100.0)*sess_score}
                              ))
        if second_sess_req:
            sess_score  =0.0
            if second_sess_ach:
                sess_score = 100
            comp_data.append((0,0,
                              {'name':'Session Enablement',
                               'weight':wt_sess2,
                               'score':sess_score,
                               'final_score':(wt_sess2/100.0)*sess_score}
                              ))
            comp_data2.append((0,0,
                              {'name':'Session Enablement',
                               'weight':wt_sess2,
                               'score':sess_score,
                               'final_score':(wt_sess2/100.0)*sess_score}
                              ))
            
            sale_enab_data.append((0,0,{'name':'Sale Enab Slot 2','kpi_point':wt_sess2,'score':(wt_sess2/100.0)*sess_score,'achieved':second_sess_ach,'user_id':usr_id}))
            sale_enab_score +=(wt_sess2/100.0)*sess_score
        
        if third_sess_req:
            sess_score  =0.0
            if third_sess_ach:
                sess_score = 100
            comp_data.append((0,0,
                              {'name':'Session Enablement',
                               'weight':wt_sess3,
                               'score':sess_score,
                               'final_score':(wt_sess3/100.0)*sess_score}
                              ))
            comp_data2.append((0,0,
                              {'name':'Session Enablement',
                               'weight':wt_sess3,
                               'score':sess_score,
                               'final_score':(wt_sess3/100.0)*sess_score}
                              ))
            
            sale_enab_data.append((0,0,{'name':'Sale Enab Slot 3','kpi_point':wt_sess3,'score':(wt_sess3/100.0)*sess_score,'achieved':third_sess_ach,'user_id':usr_id}))
            sale_enab_score +=(wt_sess3/100.0)*sess_score
            
        if mgr_score:
            comp_data.append((0,0,
                              {'name':'Direct Manager Feedback',
                               'weight':-20,
                               'score':mgr_score,
                               'final_score':mgr_score}
                              ))
        return comp_data,target,comp_data2,wt_cmt,cert_req,cert_ach,sale_enab_data,sale_enab_score
    
    def get_sales_acc_commit(self,sample_id,employee_id, usr_id, aud_date_start, aud_date_end, audit_temp_id):
        commit,monthly_target =0.0,0.0
        samp_obj = self.env['audit.sample']
        samp_id =samp_obj.search([('employee_id','=',employee_id),('date_start','=',aud_date_start)],limit=1)
        if samp_id:
            commit = sum([com.gp for com in samp_id.commit_gp_line])
            monthly_target = samp_id.target
        return commit,monthly_target
    
    
    def get_sm_data(self,sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id):
        type = audit_temp_id.type
        employee_id = self.id
        sam_ids = self.search([('parent_id','=',employee_id)]) 
        emp_ids = [emp for emp in sam_ids if (emp.audit_temp_id and emp.audit_temp_id.type =='sales_acc_mgr')]
        ach_data =[]
        team_comp_data = []
        score_board =[]
        cf_data =[]
        cf_summary=[]
        cf_board =[]
        kpi_point_board=[]
        total_target ,total_commit,total_achieved =0,0,0
        cert_data = []
        cert_score_board=[]
        cert_summary = []
        sale_enab_board = []
        sale_enab_detail =[]
        sale_enab_summary =[]
        comp_line  =[]
        for emp in emp_ids:
            commit_total = emp.commit_total 
            
            
            usr_id = emp.user_id and emp.user_id.id or False
            ach_val,ach_total = self.get_sales_achieved_data(sample_id, usr_id, aud_date_start, aud_date_end, audit_temp_id)
            commit,monthly_target = self.get_sales_acc_commit(sample_id, emp.id, usr_id, aud_date_start, aud_date_end, audit_temp_id)
#             cf_fact = min(commit,ach_total)/max(monthly_target,commit)
            cf_fact = min(commit,ach_total)/monthly_target
            
            if ach_total >= commit:
#                 result = commit_total/max(target,commit_total)
                cf_fact = commit/monthly_target
                if cf_fact >3.0:
                    cf_fact =3
            elif ach_total < commit:
                cf_fact = ach_total/max(monthly_target,commit_total)
#                 cf_fact = ach_total/monthly_target
                if cf_fact > 1.5:
                    cf_fact =1.5
            
            
            cf = cf_fact * 100.0 
            team_comp_val,target,emp_val,kpi_point,cert_req,cert_ach,sale_enab_data,sale_enab_score = self.get_sales_acc_mgr_component_sm(emp.id,commit, ach_total)
            cf_data.append((0,0,{'user_id':usr_id,'commit':commit,'month_target':monthly_target,'achieved':ach_total,'cf_fact':cf,'kpi_point':kpi_point}))
            ach_data.extend(ach_val)
            cf_board.append(cf)
            kpi_point_board.append(kpi_point)
            cert_score =0.0
            kp_point =0.0
            sale_enab_detail += sale_enab_data
            if sale_enab_data:
                sale_enab_board.append(sale_enab_score)
            if cert_req:
                kp_point =10.0
                if cert_ach:
                    cert_score =10.0
                cert_score_board.append(cert_score)
            cert_data.append((0,0,{'user_id':usr_id,'required':cert_req,'cert_ach':cert_ach,'kpi_point':kp_point,'score':cert_score}))
            total_target +=monthly_target
            total_achieved +=ach_total 
            total_commit+=commit
            score = self.get_score_from_comp_data(team_comp_val)
            emp_score = self.get_score_from_comp_data(emp_val)
            team_comp_data.append((0,0,{'user_id':usr_id,'score':score,'emp_score':emp_score,}))
            score_board.append(score)
        
        certicate_avg_scr = self.get_avg_score(cert_score_board)
        cert_stat_name = 'n_a'
        if cert_score_board:
            cert_stat_name ='10'
            comp_line.append((0,0,{'name':'Certificate Score','weight':10,'score':certicate_avg_scr,'final_score':certicate_avg_scr}))
        cert_summary.append((0,0,{'name':cert_stat_name,'score':certicate_avg_scr}))
        
        sale_enab_avg_scr = self.get_avg_score(sale_enab_board)
        sale_enab_stat_name ='n_a'
        if sale_enab_board:
            sale_enab_stat_name ='10'
            comp_line.append((0,0,{'name':'Sale Enablement Score','weight':10,'score':sale_enab_avg_scr,'final_score':sale_enab_avg_scr}))
        sale_enab_summary.append((0,0,{'name':sale_enab_stat_name,'score':sale_enab_avg_scr}))
        
        cf_avg = self.get_avg_score(cf_board)
        kpi_point = min(kpi_point_board)
        scr = (kpi_point/100.0) * cf_avg
        cf_summary.append((0,0,{'total_target':total_target,'total_commit':total_commit,'total_achieved':total_achieved,'cf':cf_avg,'kpi_point':kpi_point,'score':scr}))
        avg_score = self.get_avg_score(score_board)
        wt =1.0
        score =avg_score 
        final_score = wt * avg_score
        comp_line.append((0,0, {'name':'Average Team Performance -CF','weight':kpi_point,'score':cf_avg,'final_score':(kpi_point/100.0) * cf_avg}))
        mgr_score = self.get_mgr_feedback()
        if mgr_score:
            comp_line.append((0,0,
                              {'name':'Direct Manager Feedback',
                               'weight':-20,
                               'score':mgr_score,
                               'final_score':mgr_score}
                              ))
        return ach_data,team_comp_data,comp_line,cf_data,cf_summary,cert_data,cert_summary,sale_enab_detail,sale_enab_summary
        
    
    def get_sdm_component(self,avg_day_score,avg_hd_score):
        comp_data = []
        wt_day = .2 
        wt_hd = .8
        
        score = avg_day_score
        final_score = score * wt_day
        comp_data.append((0,0,{'name':'Average Of Team Performance - 5 Day Processing','score':score,'weight':wt_day*100.0,'final_score':final_score}))
       
        score = avg_hd_score
        final_score = score * wt_hd
        comp_data.append((0,0,{'name':'Average Of Team Performance -Help Desk Issue Management','score':score,'weight':wt_hd*100.0,'final_score':final_score}))
        mgr_score = self.get_mgr_feedback()
        if mgr_score:
            comp_data.append((0,0,
                              {'name':'Direct Manager Feedback',
                               'weight':-20,
                               'score':mgr_score,
                               'final_score':mgr_score}
                              ))
        return comp_data
    
          
    
    def get_sdm_data(self,sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id):
        type = audit_temp_id.type
        employee_id = self.id
        team_ids = self.search([('parent_id','=',employee_id)]) 
        user_ids = [emp.user_id.id for emp in team_ids if (emp.audit_temp_id and emp.audit_temp_id.type =='sde')]
        day_score_board = []
        team_day_score_val = []
        
        team_hd_vals  =[]
        team_hd_score_board =[]
        for user in user_ids:
            dum1,dum2,dum3,comp_line = self.get_sde_data_ksa(sample_id,user, aud_date_start, aud_date_end, audit_temp_id)
            for _,_,val in comp_line:
                if val.get('name','') == '5 Day Processing Score':
                    score =val.get('score',0.0)
                    team_day_score_val.append((0,0,{'user_id':user,'score':score}))
                    day_score_board.append(score)
                    
                if val.get('name','') == 'Help Desk Issue Management':
                    score =val.get('score',0.0)
                    team_hd_vals.append((0,0,{'user_id':user,'score':score}))
                    team_hd_score_board.append(score)
        avg_day_score = self.get_avg_score(day_score_board)    
        avg_hd_score = self.get_avg_score(team_hd_score_board) 
        comp_line = self.get_sdm_component(avg_day_score,avg_hd_score)   
        return team_day_score_val,team_hd_vals,comp_line
    
    
    
    def check_date_in_audit(self,aud_date_start, aud_date_end,date):
        res = False
        if aud_date_start <= date <= aud_date_end:
            res = True
        if date <= aud_date_start:
            res = True
        return res
#     def get_pm_invoice_data(self,sample_id, aud_date_start, aud_date_end, audit_temp_id):        
#         user_id  = self.user_id and self.user_id.id
#         analytic_pool = self.env['account.analytic.account']
#         analytic_ids = analytic_pool.search([('od_owner_id','=',user_id),('state','not in',('close','cancelled'))])
#         project_closed_on_audit = analytic_pool.search([('od_owner_id','=',user_id),('state','=','close'),('date','>=',aud_date_start),('date','<=',aud_date_end)])
#         
#         pr_ids  = [a.id for a in analytic_ids] 
#         closed_ids =[y.id for y in project_closed_on_audit]
#         project_ids = pr_ids + closed_ids 
#         project_ids = list(set(project_ids))
#         planned_date_vals = []
#         customer_invoice_vals = []
#         pl_amounts = []
#         inv_amounts = []
#         print "project ids>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",project_ids
#         if project_ids:
#             print "inside the looooooooooooooooooooooooooooooop"
#             for proj in analytic_pool.browse(project_ids):
#                 pl_amount =0.0
#                 type = proj.od_type_of_project 
# #                 if type == 'amc':
# #                     for line in proj.od_amc_invoice_schedule_line:
# #                         date = line.date 
# #                         check = self.check_date_in_audit(aud_date_start, aud_date_end, date)
# #                         if check:
# #                             pl_amount += line.amount
# #                             pl_amounts.append(line.amount)
# #                     if pl_amount:
# #                         planned_date_vals.append((0,0,{'analytic_id':proj.id,'amount':pl_amount}))
# #                 if type  == 'o_m':
# #                     for line in proj.od_om_invoice_schedule_line:
# #                         date = line.date 
# #                         check = self.check_date_in_audit(aud_date_start, aud_date_end, date)
# #                         if check:
# #                             pl_amount += line.amount
# #                             pl_amounts.append(line.amount)
# #                     if pl_amount:
# #                         planned_date_vals.append((0,0,{'analytic_id':proj.id,'amount':pl_amount}))
#                 if type not in ('credit','amc','o_m'):
#                     for line in proj.od_project_invoice_schedule_line:
#                         date = line.date 
#                         check = self.check_date_in_audit(aud_date_start, aud_date_end, date)
#                         if check:
#                             pl_amount += line.amount
#                             pl_amounts.append(line.amount)
#                     if pl_amount:
#                         planned_date_vals.append((0,0,{'analytic_id':proj.id,'amount':pl_amount}))
#                 
#                 invoice_ids = self.env['account.invoice'].search([('od_analytic_account','=',proj.id),('state','in',('open','paid'))])
#                 for inv in invoice_ids:
#                     customer_invoice_vals.append((0,0,{'invoice_id':inv.id,'analytic_id':proj.id,'amount':inv.amount_total}))
#                     inv_amounts.append(inv.amount_total)
#         return planned_date_vals,customer_invoice_vals,sum(pl_amounts),sum(inv_amounts)
            
#     def get_pm_component(self,planned_amount,invoice_amount):
#         comp_data  =[]
#         wt_inv =30
#         if planned_amount:
#             inv_scr = (invoice_amount/float(planned_amount))*100
#             comp_data.append((0,0,{'name':'Invoice Schedule','weight':wt_inv,'final_score':(wt_inv/100.0)*inv_scr,'score':inv_scr}))
#         return comp_data
    
    
    def get_pm_component(self,day_weight_scr,cc_weight_scr,inv_weight_scr,comp_weight_scr,sc_weight_scr,day_flag,cost_flag,inv_flag,comp_flag,sc_flag):
        comp_data =[]
        day_wt  =.1
        cc_wt = .2
        inv_wt =.3
        comp_wt =.1
        sc_wt = .3
        exclude_wt = 0.0
        if not day_flag:
            exclude_wt += day_wt
            day_wt =0.0 
        if not cost_flag:
            exclude_wt += cc_wt
            cc_wt =0.0
        if not inv_flag:
            exclude_wt += inv_wt
            inv_wt =0.0
        if not comp_flag:
            exclude_wt += comp_wt 
            comp_wt =0.0
        if not sc_flag:
            exclude_wt += sc_wt
            sc_wt =0.0
        if exclude_wt == 1.0:
            return comp_data
        if exclude_wt:
            day_wt =  day_wt + (day_wt*exclude_wt)/float(1.0-exclude_wt)
            cc_wt =  cc_wt + (cc_wt*exclude_wt)/float(1.0-exclude_wt)
            inv_wt =  inv_wt + (inv_wt*exclude_wt)/float(1.0-exclude_wt)
            comp_wt =  comp_wt + (comp_wt*exclude_wt)/float(1.0-exclude_wt)
            sc_wt = sc_wt + (sc_wt*exclude_wt)/float(1.0-exclude_wt)
        if day_wt:
            score = (day_weight_scr/10.0) *100.0
            final_score = day_wt * score
            comp_data.append((0,0,{'name':'5 Day Processing Score','weight':day_wt*100.0,'final_score':final_score,'score':score}))
        
        if cc_wt:
            score = (cc_weight_scr/20.0) *100.0
            final_score = cc_wt * score
            comp_data.append((0,0,{'name':'Cost Control','weight':cc_wt*100.0,'final_score':final_score,'score':score}))
            
        if inv_wt:
            score = (inv_weight_scr/30.0) *100.0
            final_score = inv_wt * score
            comp_data.append((0,0,{'name':'Invoice Schedule','weight':inv_wt*100,'final_score':final_score,'score':score}))
            
        if comp_wt:
            score = (comp_weight_scr/10.0) *100.0
            final_score = comp_wt * score
            comp_data.append((0,0,{'name':'Compliance Provided By PMO','weight':comp_wt*100.0,'final_score':final_score,'score':score}))
         
        if sc_wt:
            score = (sc_weight_scr/30.0) *100.0
            final_score = sc_wt * score
            comp_data.append((0,0,{'name':'Schedule Control','weight':sc_wt*100.0,'final_score':final_score,'score':score}))
            
        mgr_score = self.get_mgr_feedback()
        if mgr_score:
            comp_data.append((0,0,
                              {'name':'Direct Manager Feedback',
                               'weight':-20,
                               'score':mgr_score,
                               'final_score':mgr_score}
                              ))    
        return comp_data
    
    def get_sde_component(self,day_weight_scr,comp_weight_scr,hd_score,cert_score,day_flag,comp_flag,hd_flag,cert_flag):
        comp_data =[]
        day_wt  =.2
        hd_wt = .6
        cert_wt =.1
        comp_wt =.1
        
        exclude_wt = 0.0
        if not day_flag:
            exclude_wt += day_wt
            day_wt =0.0 
        if not hd_flag:
            exclude_wt += hd_wt
            hd_wt =0.0
        if not cert_flag:
            exclude_wt += cert_wt
            cert_wt =0.0
        if not comp_flag:
            exclude_wt += comp_wt 
            comp_wt =0.0
       
        if exclude_wt == 1.0:
            return comp_data
        if exclude_wt:
            day_wt =  day_wt + (day_wt*exclude_wt)/float(1.0-exclude_wt)
            comp_wt =  comp_wt + (comp_wt*exclude_wt)/float(1.0-exclude_wt)
            hd_wt = hd_wt + (hd_wt*exclude_wt)/float(1.0-exclude_wt)
            cert_wt =  cert_wt + (cert_wt*exclude_wt)/float(1.0-exclude_wt)
        if day_wt:
            score = (day_weight_scr/10.0) *100.0
            final_score = day_wt * score
            comp_data.append((0,0,{'name':'5 Day Processing Score','weight':day_wt*100.0,'final_score':final_score,'score':score}))
        
        if comp_wt:
            score = (comp_weight_scr/10.0) *100.0
            final_score = comp_wt * score
            comp_data.append((0,0,{'name':'Compliance Provided By PMO','weight':comp_wt*100.0,'final_score':final_score,'score':score}))
         
        if hd_wt:
            score = hd_score 
            final_score = hd_wt * score
            comp_data.append((0,0,{'name':'Help Desk Issue Management','weight':hd_wt*100.0,'final_score':final_score,'score':score}))
        
        if cert_wt:
            score = cert_score
            final_score = cert_wt * score
            comp_data.append((0,0,{'name':'Certificate','weight':cert_wt*100.0,'final_score':final_score,'score':score}))
            
        mgr_score = self.get_mgr_feedback()
        if mgr_score:
            comp_data.append((0,0,
                              {'name':'Direct Manager Feedback',
                               'weight':-20,
                               'score':mgr_score,
                               'final_score':mgr_score}
                              ))    
                   
        return comp_data
        
    
    def check_inv_sch_dates(self,inv_sch_dates,aud_date_start,aud_date_end):
        for date in inv_sch_dates:
            if date <=aud_date_end:
                return True
        return False
#     def get_inv_sch_score(self,proj,aud_date_start,aud_date_end):
#         project_start_date = proj.od_project_start
#         if not project_start_date:
#             raise Warning("Project Date Start Not Set in Project : %s"%proj.name) 
#         score_board = []
#         check = False
#         for line in proj.od_project_invoice_schedule_line:
#             planned_date = line.date
#             if not planned_date:
#                 raise Warning("Planning Date not In Project : %s"%proj.name) 
#             pl_dt = self.get_x_days(project_start_date, planned_date)
#             today = str(dt.today())
#             td_dt =self.get_x_days(project_start_date, today)
#             if td_dt>=pl_dt:
#                 invoice = line.invoice_id
#                 if aud_date_start<=planned_date <= aud_date_end:
#                     check =True
#                     planned_amount = line.amount
#                     invoice_amount = line.invoice_amount
#                     diff =  invoice_amount -planned_amount
#                     diff = diff +1
#                     if diff <0.0:
#                         score =0.0
#                         check =True
#                     else:
#                         score =30.0
#                         score_board.append(score)
#                         continue
#                 if invoice and invoice.state in ('open','paid','accept'):
#                     cust_date = invoice.cust_date 
#                     if aud_date_start<=cust_date <= aud_date_end:
#                         check = True
#                         score = 0.0
#                         if cust_date <= planned_date:
#                             score = 30.0
#                         score_board.append(score)
#         avg_score = self.get_avg_score(score_board)
#         return check,avg_score
    
    
    def get_inv_sch_score(self,proj,aud_date_start,aud_date_end):
        project_start_date = proj.od_project_start
        if not project_start_date:
            raise Warning("Project Date Start Not Set in Project : %s"%proj.name) 
        score_board = []
        check = False
        planned_amount = 0.0
        for line in proj.od_project_invoice_schedule_line:
            planned_date = line.date
            if not planned_date:
                raise Warning("Planning Date not In Project : %s"%proj.name) 
            pl_dt = self.get_x_days(project_start_date, planned_date)
            today = str(dt.today())
            td_dt =self.get_x_days(project_start_date, today)
            if td_dt>=pl_dt:
                invoice = line.invoice_id
                invoice_state = invoice.state
                if invoice and invoice_state in ('open','paid','accept'):
                    cust_date = invoice.cust_date
                    if cust_date:
                        if aud_date_start<=cust_date <= aud_date_end:
                            if cust_date <= planned_date:
                                check = True
                                score =30.0
                                score_board.append(score)
                                planned_amount +=line.amount
                            else:
                                check = True
                                score =0.0
                                score_board.append(score)
                                planned_amount +=line.amount
                    else:
                        check = True
                        score =0.0
                        score_board.append(score)
                        planned_amount +=line.amount
                            
                else:
                    check = True
                    score =0.0
                    score_board.append(score)
                    planned_amount +=line.amount
                
        avg_score = self.get_avg_score(score_board)
        return check,avg_score,planned_amount
                                    
                    
        
    
    def get_pm_data(self,sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id):
        
        analytic_pool = self.env['account.analytic.account']
        analytic_ids = analytic_pool.search([('od_owner_id','=',user_id),('od_type_of_project','in',('sup','imp','sup_imp','cust_trn')),('state','not in',('close','cancelled'))])
        project_closed_on_audit_old_type = analytic_pool.search([('od_owner_id','=',user_id),('od_type_of_project','in',('sup','imp','sup_imp','cust_trn')),('state','=','close'),('od_analytic_level','=','level_old'),('od_project_end','>=',aud_date_start),('od_project_end','<=',aud_date_end)])
        project_closed_on_audit = analytic_pool.search([('od_owner_id','=',user_id),('od_type_of_project','in',('sup','imp','sup_imp','cust_trn')),('state','=','close'),('od_analytic_level','!=','level_old'),('od_date_end_original','>=',aud_date_start),('od_date_end_original','<=',aud_date_end)])
        project_closed = analytic_pool.search([('od_owner_id','=',user_id),('od_type_of_project','in',('sup','imp','sup_imp','cust_trn')),('state','=','close'),('od_analytic_level','!=','level_old'),('od_closing_date','>=',aud_date_start),('od_closing_date','<=',aud_date_end)])
        
        sample_project_ids = analytic_ids + project_closed_on_audit + project_closed_on_audit_old_type 
        
        diff_project = project_closed - project_closed_on_audit
        
        day_score_vals  =[]
#         total_sale_value = sum([a.od_project_sale for a in sample_project_ids])
#         max_day_sore =aud_date_endaud_date_endaud_date_end 20 * len(sample_project_ids)
        
        
        cost_control_vals = []
#         total_gp_value = sum([a.od_amended_profit for a in sample_project_ids])
#         max_cc_sore = 30 * len(sample_project_ids)
        
        invoice_schedule_vals =[] 
        compliance_vals =[]
        schedule_control_vals =[]
        schedule_control_vals_main =[]
        day_weight =[]
        cc_weight =[]
        inv_weight =[]
        comp_weight =[]
        sc_weight =[]
        tot_sale_day =0.0
        tot_gp =0.0
        sch_gp =0.0
        tot_sal_inv =0.0
        tot_sal_comp =0.0
        day_score_main = []
        cost_control_val_main =[]
        invoice_schedule_main =[]
        compliance_vals_main =[]
        a0_ids = []
        
        for proj in project_closed:
            if proj.state == 'close':
                closed_date = proj.od_closing_date
                if closed_date and aud_date_start <= closed_date <= aud_date_end:
                    gp_value = proj.od_amended_profit 
                    actual_gp = proj.od_actual_profit
                    original_gp = proj.od_original_sale_profit
                    tot_gp += gp_value
                    cost_control_score = proj.cost_control_score 
                    cost_control_vals.append({'analytic_id':proj.id,'gp_value':gp_value,'score':cost_control_score,'form_wt':20.0,'actual_gp':actual_gp,'original_gp':original_gp})
               
            
        for proj in sample_project_ids:
            processed_date = proj.od_cost_sheet_id and proj.od_cost_sheet_id.processed_date and proj.od_cost_sheet_id.processed_date[:10]
            if processed_date and aud_date_start <= processed_date <= aud_date_end:
                sale_val = proj.od_amended_sale_price or 1.0
                tot_sale_day += sale_val
                dayscore = proj.day_process_score
                day_score_vals.append({'analytic_id':proj.id,'sale_value':sale_val,'score':dayscore,'cost_sheet_id':proj.od_cost_sheet_id.id,'form_wt':10.0})
            #cost control score
#             if proj.state == 'close':
#                 closed_date = proj.od_closing_date
#                 if closed_date and aud_date_start <= closed_date <= aud_date_end:
#                     gp_value = proj.od_amended_profit 
#                     actual_gp = proj.od_actual_profit
#                     original_gp = proj.od_original_sale_profit
#                     tot_gp += gp_value
#                     cost_control_score = proj.cost_control_score 
#                     cost_control_vals.append({'analytic_id':proj.id,'gp_value':gp_value,'score':cost_control_score,'form_wt':20.0,'actual_gp':actual_gp,'original_gp':original_gp})
                #invoice Schedule Score
#             inv_sch_dates = [a.date for a in proj.od_project_invoice_schedule_line]
#             check = self.check_inv_sch_dates(inv_sch_dates,aud_date_start,aud_date_end)
#             check2,inv_score,plan_amount = self.get_inv_sch_score(proj,aud_date_start,aud_date_end)
#             if check2:
#                 invoice_sc_score = inv_score
#                 tot_sal_inv  += plan_amount
#                 invoice_schedule_vals.append({'analytic_id':proj.id,'sale_value':plan_amount,'score':invoice_sc_score,'form_wt':30.0})
            
            #Added by Aslam to include A0 INV1 Analytic Accounts
            if proj.fin_approved_date and proj.fin_approved_date[:10] > '2020-09-01':
                
                today = str(dt.today())
                parent_analytic = proj.parent_id or False
                if parent_analytic and parent_analytic.id not in a0_ids:
                    for inv_sch in parent_analytic.prj_inv_sch_line:
                        if inv_sch.name == 'INV1' and inv_sch.date > '01-Nov-20' and not inv_sch.invoice_id:
                            if today >= inv_sch.date:
                                a0_ids.append(proj.parent_id.id)
                                score =0.0
                                plan_amount = inv_sch.amount
                                tot_sal_inv  += plan_amount
                                invoice_schedule_vals.append({'analytic_id':proj.parent_id.id,'sale_value':plan_amount,'score':score,'form_wt':30.0})
            
            for inv_line in proj.od_project_invoice_schedule_line:
                today = str(dt.today())
                planned_date = inv_line.date
                if today >= planned_date:
                    invoice = inv_line.invoice_id
                    invoice_state = invoice.state
                    if invoice and invoice_state in ('open','paid','accept'):
                        cust_date = invoice.cust_date
                        if cust_date:
                            if aud_date_start<=cust_date <= aud_date_end:
                                if cust_date <= planned_date:
                                    score =30.0
                                    plan_amount = inv_line.amount
                                    tot_sal_inv  += plan_amount
                                    invoice_schedule_vals.append({'analytic_id':proj.id,'sale_value':plan_amount,'score':score,'form_wt':30.0})
                                else:
                                    score =0.0
                                    plan_amount = inv_line.amount
                                    tot_sal_inv  += plan_amount
                                    invoice_schedule_vals.append({'analytic_id':proj.id,'sale_value':plan_amount,'score':score,'form_wt':30.0})
                        else:
                            score =0.0
                            plan_amount = inv_line.amount
                            tot_sal_inv  += plan_amount
                            invoice_schedule_vals.append({'analytic_id':proj.id,'sale_value':plan_amount,'score':score,'form_wt':30.0})
                                
                    else:
                        score =0.0
                        plan_amount = inv_line.amount
                        tot_sal_inv  += plan_amount
                        invoice_schedule_vals.append({'analytic_id':proj.id,'sale_value':plan_amount,'score':score,'form_wt':30.0})
                        
                    
            
                    
            
            if proj.start_project_comp:
                compliance_score = proj.compliance_score
                #sale_val = proj.od_project_sale
                sale_val = proj.od_amended_sale_price or 1.0
                tot_sal_comp  += sale_val 
                compliance_vals.append({'analytic_id':proj.id,'sale_value':sale_val,'score':compliance_score,'form_wt':10.0})
            
            
            #schedule control score
            current_day = str(dt.today())
#             project_planned_end = proj.od_project_end or proj.date
            project_planned_end = proj.od_date_end_original
            closed_date = proj.od_closing_date 
            if current_day >=project_planned_end:
                if proj.state == 'close':
                    if aud_date_start <= closed_date <=aud_date_end:
                        sc_scr =30.0
                        gp_value = proj.od_amended_profit 
                        sch_gp += gp_value
                        schedule_control_vals.append({'analytic_id':proj.id,'gp_value':gp_value,'score':sc_scr,'form_wt':30.0})
                        
                else:
                    sc_scr =0.0
                    gp_value = proj.od_amended_profit 
                    sch_gp += gp_value
                    schedule_control_vals.append({'analytic_id':proj.id,'gp_value':gp_value,'score':sc_scr,'form_wt':30.0})
                
#             if proj.od_project_status == 'close':
#                 project_planned_end = proj.od_project_end 
#                 closed_date = proj.od_project_closing 
#                 if closed_date <= project_planned_end:
#                     sc_scr =30.0
#                     gp_value = proj.od_project_amend_profit 
#                     sch_gp += gp_value
#                     schedule_control_vals.append({'analytic_id':proj.id,'gp_value':gp_value,'score':sc_scr,'form_wt':30.0})
#                 else:
#                     sc_scr =0.0
#                     gp_value = proj.od_project_amend_profit 
#                     sch_gp += gp_value
#                     schedule_control_vals.append({'analytic_id':proj.id,'gp_value':gp_value,'score':sc_scr,'form_wt':30.0})
                    
        max_day_sore = 10 * len(day_score_vals)
        for data in day_score_vals:
            sal_val_percent =0.0
            sale_value  = data.get('sale_value')
            
            if tot_sale_day:
                sal_val_percent = sale_value/float(tot_sale_day)
            dayscore = data.get('score')
            weight_day = max_day_sore * sal_val_percent * (dayscore/10.0)
            data['sale_value_percent'] = sal_val_percent *100.0
            data['weight'] = weight_day
            day_weight.append(weight_day)
            day_score_main.append((0,0,data))
        max_cc_sore = 20 * len(cost_control_vals)
        for data in cost_control_vals:
            gp_val_percent =0.0
            gp_value = data.get('gp_value')
            if tot_gp:
                gp_val_percent = gp_value/float(tot_gp)
            score = data.get('score')
            weight_cc = max_cc_sore * gp_val_percent * (score/20.0)
            data['weight'] = weight_cc
            data['gp_value_percent'] = gp_val_percent *100.0
            cc_weight.append(weight_cc)
            cost_control_val_main.append((0,0,data))
        
        
        max_sc_sore = 30 * len(schedule_control_vals)
        for data in schedule_control_vals:
            gp_val_percent =0.0
            gp_value = data.get('gp_value')
            if sch_gp:
                gp_val_percent = gp_value/float(sch_gp)
            score = data.get('score')
            weight_sc = max_sc_sore * gp_val_percent * (score/30.0)
            data['weight'] = weight_sc
            data['gp_value_percent'] = gp_val_percent *100.0
            sc_weight.append(weight_sc)
            schedule_control_vals_main.append((0,0,data))
        
        max_inv_scr = 30 * len(invoice_schedule_vals)
        for data in invoice_schedule_vals:
            sal_val_percent =0.0
            sale_value  = data.get('sale_value')
            if tot_sal_inv:
                sal_val_percent = sale_value/float(tot_sal_inv)
            score = data.get('score')
            weight_inv = max_inv_scr * sal_val_percent * (score/30.0)
            data['sale_value_percent'] = sal_val_percent *100.0
            data['weight'] = weight_inv
            inv_weight.append(weight_inv)
            invoice_schedule_main.append((0,0,data))
        
        max_comp_scr = 10 * len(compliance_vals)
        for data in compliance_vals:
            sal_val_percent =0.0
            sale_value  = data.get('sale_value')
            if tot_sal_comp:
                sal_val_percent = sale_value/float(tot_sal_comp)
            score = data.get('score')
            weight_comp = max_comp_scr * sal_val_percent * (score/10.0)
            data['sale_value_percent'] = sal_val_percent *100.0
            data['weight'] = weight_comp
            comp_weight.append(weight_comp)
            compliance_vals_main.append((0,0,data))
        
            
        day_weight_scr = self.get_avg_score(day_weight)
        cc_weight_scr = self.get_avg_score(cc_weight)
        inv_weight_scr = self.get_avg_score(inv_weight)
        comp_weight_scr = self.get_avg_score(comp_weight )
        sc_weight_scr = self.get_avg_score(sc_weight)
        day_flag = cost_flag = inv_flag= comp_flag= sc_flag=False 
        if day_score_main:
            day_flag =True 
        if cost_control_val_main:
            cost_flag = True
        if invoice_schedule_main:
            inv_flag = True 
        if compliance_vals_main:
            comp_flag = True
        if schedule_control_vals_main:
            sc_flag = True
        comp_line = self.get_pm_component(day_weight_scr,cc_weight_scr,inv_weight_scr,comp_weight_scr,sc_weight_scr,day_flag,cost_flag,inv_flag,comp_flag,sc_flag)
        
        
            
        return day_score_main,cost_control_val_main,invoice_schedule_main,compliance_vals_main,schedule_control_vals_main,comp_line
    
    
    
    def get_hd_data(self,sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id):
        hd_pool = self.env['crm.helpdesk']
        domain  = [('user_id','=',user_id),('categ_id','in',(16,17))]
        domain.extend([('date_deadline','>=',aud_date_start),('date_deadline','<=',aud_date_end)])
        hd_data = hd_pool.search(domain)
        hd_vals =[]
        score_board =[]
        for hd in hd_data:
            score =hd.od_hd_kpi
            hd_vals.append((0,0,{'hd_id':hd.id,'score':score}))
            score_board.append(score)
        hd_score = self.get_avg_score(score_board)
        return hd_vals,hd_score
            
    
    def get_sde_data(self,sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id):
        analytic_pool = self.env['account.analytic.account']
        analytic_ids = analytic_pool.search([('od_amc_owner_id','=',user_id),('od_type_of_project','=','amc'),('state','not in',('close','cancelled'))])
        project_closed_on_audit = analytic_pool.search([('od_amc_owner_id','=',user_id),('od_type_of_project','=','amc'),('state','=','close'),('date','>=',aud_date_start),('date','<=',aud_date_end)])
        sample_project_ids = analytic_ids + project_closed_on_audit
        day_score_vals  =[]
        day_weight =[]
        tot_sale_day =0.0
        day_score_main = []
        compliance_vals =[]
        comp_weight =[]
        tot_sal_comp =0.0
        compliance_vals_main =[]
        
        for proj in sample_project_ids:
            processed_date = proj.od_cost_sheet_id and proj.od_cost_sheet_id.processed_date
            owner_id = proj.od_cost_sheet_id and proj.od_cost_sheet_id.reviewed_id and  proj.od_cost_sheet_id.reviewed_id.id or False 
            if user_id == owner_id:
                if processed_date and aud_date_start <= processed_date <= aud_date_end:
                    sale_val = proj.od_amc_sale or proj.od_amended_sale_price
                    tot_sale_day += sale_val
                    dayscore = proj.day_process_score
                    day_score_vals.append({'analytic_id':proj.id,'sale_value':sale_val,'score':dayscore,'cost_sheet_id':proj.od_cost_sheet_id.id,'form_wt':20.0})
            
            if proj.start_amc_comp:
                compliance_score = proj.compliance_score
                sale_val = proj.od_amc_sale or proj.od_amended_sale_price
                tot_sal_comp  += sale_val 
                compliance_vals.append({'analytic_id':proj.id,'sale_value':sale_val,'score':compliance_score,'form_wt':10.0})
        
        max_day_sore = 10.0 * len(day_score_vals)
        for data in day_score_vals:
            sal_val_percent =0.0
            sale_value  = data.get('sale_value')
            if tot_sale_day:
                sal_val_percent = sale_value/float(tot_sale_day)
            dayscore = data.get('score')
            weight_day = max_day_sore * sal_val_percent * (dayscore/10.0)
            data['sale_value_percent'] = sal_val_percent *100.0
            data['weight'] = weight_day
            day_weight.append(weight_day)
            day_score_main.append((0,0,data))
        
        
        max_comp_scr = 10 * len(compliance_vals)
        for data in compliance_vals:
            sal_val_percent =0.0
            sale_value  = data.get('sale_value')
            if tot_sal_comp:
                sal_val_percent = sale_value/float(tot_sal_comp)
            score = data.get('score')
            weight_comp = max_comp_scr * sal_val_percent * (score/10.0)
            data['sale_value_percent'] = sal_val_percent *100.0
            data['weight'] = weight_comp
            comp_weight.append(weight_comp)
            compliance_vals_main.append((0,0,data))
        
        day_weight_scr = self.get_avg_score(day_weight)
        comp_weight_scr = self.get_avg_score(comp_weight )
        cert_score =0.0
        day_flag = comp_flag =cert_flag=hd_flag=  False
        if day_score_main:
            day_flag =True 
        if compliance_vals_main:
            comp_flag = True
        employee = self.search([('user_id','=',user_id)],limit=1)
        cert = employee.get_certificate_status()
        cert_ach = cert.get('achieved',False)
        cert_req = cert.get('required',False)
        
        if cert_req:
            cert_flag = True
        if cert_ach:
            cert_score =100.0
        
        hd_vals,hd_score = self.get_hd_data(sample_id, user_id, aud_date_start, aud_date_end, audit_temp_id)
        if hd_vals:
            hd_flag = True
        
        comp_line = self.get_sde_component(day_weight_scr,comp_weight_scr,hd_score,cert_score,day_flag,comp_flag,hd_flag,cert_flag)
        
        return day_score_main,hd_vals,compliance_vals_main,comp_line
    
    
    
    def get_sde_data_ksa(self,sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id):
        analytic_pool = self.env['account.analytic.account']
        analytic_ids = analytic_pool.search([('od_amc_owner_id','=',user_id),('od_type_of_project','=','amc'),('state','not in',('close','cancelled'))])
        project_closed_on_audit = analytic_pool.search([('od_amc_owner_id','=',user_id),('od_type_of_project','=','amc'),('state','=','close'),('date','>=',aud_date_start),('date','<=',aud_date_end)])
        sample_project_ids = analytic_ids + project_closed_on_audit
        day_score_vals  =[]
        day_weight =[]
        tot_sale_day =0.0
        day_score_main = []
        compliance_vals =[]
        comp_weight =[]
        tot_sal_comp =0.0
        compliance_vals_main =[]
        
        for proj in sample_project_ids:
            processed_date = proj.od_cost_sheet_id and proj.od_cost_sheet_id.processed_date
            owner_id = proj.od_cost_sheet_id and proj.od_cost_sheet_id.reviewed_id and  proj.od_cost_sheet_id.reviewed_id.id or False 
#             if user_id == owner_id:
#                 if processed_date and aud_date_start <= processed_date <= aud_date_end:
#                     sale_val = proj.od_amc_sale or proj.od_amended_sale_price
#                     tot_sale_day += sale_val
#                     dayscore = proj.day_process_score
#                     day_score_vals.append({'analytic_id':proj.id,'sale_value':sale_val,'score':dayscore,'cost_sheet_id':proj.od_cost_sheet_id.id,'form_wt':20.0})
#              
            if proj.start_amc_comp:
                compliance_score = proj.compliance_score
                sale_val = proj.od_amc_sale or proj.od_amended_sale_price
                tot_sal_comp  += sale_val 
                compliance_vals.append({'analytic_id':proj.id,'sale_value':sale_val,'score':compliance_score,'form_wt':10.0})
         
#         max_day_sore = 10.0 * len(day_score_vals)
#         for data in day_score_vals:
#             sal_val_percent =0.0
#             sale_value  = data.get('sale_value')
#             if tot_sale_day:
#                 sal_val_percent = sale_value/float(tot_sale_day)
#             dayscore = data.get('score')
#             weight_day = max_day_sore * sal_val_percent * (dayscore/10.0)
#             data['sale_value_percent'] = sal_val_percent *100.0
#             data['weight'] = weight_day
#             day_weight.append(weight_day)
#             day_score_main.append((0,0,data))
        
        
        max_comp_scr = 10 * len(compliance_vals)
        for data in compliance_vals:
            sal_val_percent =0.0
            sale_value  = data.get('sale_value')
            if tot_sal_comp:
                sal_val_percent = sale_value/float(tot_sal_comp)
            score = data.get('score')
            weight_comp = max_comp_scr * sal_val_percent * (score/10.0)
            data['sale_value_percent'] = sal_val_percent *100.0
            data['weight'] = weight_comp
            comp_weight.append(weight_comp)
            compliance_vals_main.append((0,0,data))
        
        day_weight_scr = self.get_avg_score(day_weight)
        comp_weight_scr = self.get_avg_score(comp_weight )
        cert_score =0.0
        day_flag = comp_flag =cert_flag=hd_flag=  False
        
        if day_score_main:
            day_flag =True 
        if compliance_vals_main:
            comp_flag = True
        employee = self.search([('user_id','=',user_id)],limit=1)
        cert = employee.get_certificate_status()
        cert_ach = cert.get('achieved',False)
        cert_req = cert.get('required',False)
        
        if cert_req:
            cert_flag = True
        if cert_ach:
            cert_score =100.0
        
        hd_vals,hd_score = self.get_hd_data(sample_id, user_id, aud_date_start, aud_date_end, audit_temp_id)
        if hd_vals:
            hd_flag = True
        
        comp_line = self.get_sde_component(day_weight_scr,comp_weight_scr,hd_score,cert_score,day_flag,comp_flag,hd_flag,cert_flag)
        
        return day_score_main,hd_vals,compliance_vals_main,comp_line
    
    def get_pdm_data(self,sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id):
        employee_id = self.id
        team_ids = self.search([('parent_id','=',employee_id)]) 
        user_ids = [emp.user_id.id for emp in team_ids if (emp.audit_temp_id and emp.audit_temp_id.type=='pm') ]
        result = []
        team_vals =[]
        score_board =[] 
        day_score_vals = cost_control_vals = invoice_schedule_vals = compliance_vals = schedule_control_vals = my_comp_data=[]
        for uid in user_ids:
            day_score_main,cost_control_val_main,invoice_schedule_main,compliance_vals_main,schedule_control_vals_main,team_comp_data = self.get_pm_data(sample_id,uid, aud_date_start, aud_date_end, audit_temp_id)
            if uid == user_id:
                day_score_vals, cost_control_vals,invoice_schedule_vals,compliance_vals, schedule_control_vals,my_comp_data = day_score_main,cost_control_val_main,invoice_schedule_main,compliance_vals_main,schedule_control_vals_main,team_comp_data
            score = self.get_score_from_comp_data(team_comp_data)
            team_vals.append((0,0,{'user_id':uid,'score':score}))
            score_board.append(score)

        team_avg_score =  self.get_avg_score(score_board)  
        comp_line =[(0,0,{'name':'Average Of Team Performance','weight':100,'score':team_avg_score,'final_score':team_avg_score})]
        mgr_score = self.get_mgr_feedback()
        if mgr_score:
            comp_line.append((0,0,
                              {'name':'Direct Manager Feedback',
                               'weight':-20,
                               'score':mgr_score,
                               'final_score':mgr_score}
                              ))
        return day_score_vals,cost_control_vals,invoice_schedule_vals,compliance_vals, schedule_control_vals,team_vals,my_comp_data,comp_line
        
        
    def get_session_score_bdm(self,audit_month,target):
        user_id = self.user_id and self.user_id.id 
        sale_enb =self.env['sale.enablement']
        
        sale_enab_ids = sale_enb.search([('user_id','=',user_id),('month','=',audit_month),('state','=','done')])
        score = len(sale_enab_ids)/float(target)
        if score >1.0:
            score =1
        return score 
    
    def get_bdm_component(self,total_gp,audit_date_start=False):
        target = self.annual_target/12.0
        result =0.0
        
        comp_data = []
        wt_lead = .7 
        wt_cert = .1
        wt_sess =.2
        cert_score = 0.0
        audit_date_start = datetime.strptime(audit_date_start,'%Y-%m-%d')
        audit_month = audit_date_start.month
        tgt=2.0
        sale_enab_session_score = self.get_session_score_bdm(audit_month,tgt) 
        cert = self.get_certificate_status()
        cert_ach = cert.get('achieved',False)
        cert_req = cert.get('required',False)
        
        if cert_ach:
            cert_score =100
        if target:
            result = total_gp/target 
            if result >1.5:
                result =1.5
        
        if not cert_req:
            wt_lead =  .8
            wt_cert =0.0
        if wt_lead:
            score = result *100
            final_score = score * wt_lead
            comp_data.append((0,0,{'name':'Lead Performance','score':score,'weight':wt_lead*100.0,'final_score':final_score}))
        if wt_sess:
            score = sale_enab_session_score *100
            final_score = score * wt_sess
            comp_data.append((0,0,{'name':'Sale Enablement Session','score':score,'weight':wt_sess*100.0,'final_score':final_score}))
        
        if wt_cert:
            score = cert_score
            final_score = score * wt_cert
            comp_data.append((0,0,{'name':'Career Certificate','score':score,'weight':wt_cert*100.0,'final_score':final_score}))
        
        mgr_score = self.get_mgr_feedback()
        if mgr_score:
            comp_data.append((0,0,
                              {'name':'Direct Manager Feedback',
                               'weight':-20,
                               'score':mgr_score,
                               'final_score':mgr_score}
                              ))
            
        return comp_data,target
    
    def get_tum_bdm_comp(self,total_gp,audit_date_start=False,branch_data=[]):
        target = self.annual_target/12.0
        result =0.0
        
        comp_data = []
        wt_lead = 1 
        
        cert_score = 0.0
        audit_date_start = datetime.strptime(audit_date_start,'%Y-%m-%d')
        audit_month = audit_date_start.month
        tgt=2
        sale_enab_session_score = self.get_session_score_bdm(audit_month,tgt) 
        cert = self.get_certificate_status()
        cert_ach = cert.get('achieved',False)
        cert_req = cert.get('required',False)
#         if target:
#             result = total_gp/target 
#             if result >1.5:
#                 result =1.5
        score =0.0      
        for _,_,dat in branch_data:
            score += dat.get('score',0.0)
        
        if wt_lead:
            
            final_score = score  *.25
            comp_data.append((0,0,{'name':'Lead Performance','score':score,'weight':25.0,'final_score':final_score}))
        
        
       
            
        return comp_data,target
    
    def get_bdm_ksa_component(self,total):
        comp_data = []
        comp_data.append((0,0,{'name':'Lead Performance','score':total,'weight':100.0,'final_score':total}))
        mgr_score = self.get_mgr_feedback()
        if mgr_score:
            comp_data.append((0,0,
                              {'name':'Direct Manager Feedback',
                               'weight':-20,
                               'score':mgr_score,
                               'final_score':mgr_score}
                              ))
        return comp_data
    
    def get_bdm_data(self,sample_id, aud_date_start, aud_date_end, audit_temp_id):
        result =[]
        total_gp =0.0
        user_id  = self.user_id and self.user_id.id
        
        domain = [('status','=','active')]
        domain.extend([('submit_to_customer_date','>=',aud_date_start),('submit_to_customer_date','<=',aud_date_end)])
        company_id = self.company_id and self.company_id.id
        domain.extend([('company_id','=',company_id)])
        domain1 = domain + [('state','in',('submitted','handover','processed'))]
        sheet_ids =self.env['od.cost.sheet'].search(domain1)
        for sheet in sheet_ids:
            gp = sheet.total_gp
            result.append((0,0,{'cost_sheet_id':sheet.id,'gp':sheet.total_gp}))
            total_gp +=gp
        comp_data,target = self.get_bdm_component(total_gp,aud_date_start)
        return result,comp_data,target
        
    
    
    def get_bdm_sec_pip_data(self,sample_id, aud_date_start, aud_date_end, audit_temp_id):
        result =[]
        
       
        domain = [('status','=','active')]
#         domain.extend([('submit_to_customer_date','>=',aud_date_start),('submit_to_customer_date','<=',aud_date_end)])
        company_id = self.company_id and self.company_id.id
        domain.extend([('company_id','=',company_id)])
        domain1 = domain + [('state','in',('submitted','handover','processed'))]
        sheet_ids =self.env['od.cost.sheet'].search(domain1)
        for sheet in sheet_ids:
#             sheet.update_cost_sheet()
            for line in sheet.summary_weight_line:
                if line.pdt_grp_id.id ==2:
                    gp = line.total_gp
                    if not gp:
                        sheet.update_cost_sheet()
                        break
                    else:
                        result.append((0,0,{'cost_sheet_id':sheet.id,'gp':line.total_gp,'sales':line.total_sale,
                                        'sales_aftr_disc':line.sale_aftr_disc,'cost':line.total_cost,'profit':line.profit,'profit_percent':line.profit_percent,'manpower_cost':line.manpower_cost,'product_group_id':line.pdt_grp_id.id}))
                   
       
        return result
    
    
    def get_aruba_juniper_gp(self,sheet):
        
        gp =0.0
        for line in sheet.mat_brand_weight_line:
            if line.manufacture_id.id in (26,29):
                profit = line.profit 
                gp += profit
        return gp
    
    def get_brand_sec(self,sheet):
        gp =0.0
        all_brand_cost = 0.0
        result = []
        total_sale = 0.0
        total_manpower = 0.0
        for line in sheet.summary_weight_line:
            if line.pdt_grp_id.id ==2:
                total_manpower += line.manpower_cost
                total_sale += line.sale_aftr_disc
        for line in sheet.mat_main_pro_line:

            if line.product_group_id.id ==2 and line.manufacture_id.id in (29,13,419):
                profit = (line.line_price - line.line_cost_local_currency)
                manpower = (line.line_price / total_sale) * total_manpower
                profit += manpower
                result.append((0,0,{'cost_sheet_id':sheet.id,'gp':profit,'sales':line.line_price,'cost':line.line_cost_local_currency,
                                        'profit':line.profit,'product_group_id':line.product_group_id.id,
                                        'brand_id':line.manufacture_id.id,'part_no':line.part_no and line.part_no.id,'manpower_cost':manpower
                                        }))
                gp += profit
        for line in sheet.trn_customer_training_line:
            if line.product_group_id.id ==2 and line.manufacture_id.id in (29,13,419):
                profit = (line.line_price - line.line_cost_local_currency)
                manpower = (line.line_price / total_sale) * total_manpower
                profit += manpower
                gp += profit
                result.append((0,0,{'cost_sheet_id':sheet.id,'gp':profit,'sales':line.line_price,'cost':line.line_cost_local_currency,
                                        'profit':line.profit,'product_group_id':line.product_group_id.id,
                                        'brand_id':line.manufacture_id.id,'part_no':line.part_no and line.part_no.id,'manpower_cost':manpower}))
        return gp,result
    
    
#     def get_citrix_ded_net(self,sheet):
#         gp =0.0
#         all_brand_cost = 0.0
#         for line in sheet.mat_main_pro_line:
#             if line.product_group_id.id ==2 and line.manufacture_id.id ==13:
#                 profit = (line.line_price - line.line_cost_local_currency)
#                 gp += profit
#         for line in sheet.trn_customer_training_line:
#             if line.product_group_id.id ==2 and line.manufacture_id.id ==13:
#                 profit = (line.line_price - line.line_cost_local_currency)
#                 gp += profit
#         return gp
    
    
    def get_bdm_sec_data(self,sample_id, aud_date_start, aud_date_end, audit_temp_id):
        result =[]
        total_gp =0.0
        aud_date_end = aud_date_end + ' 23:59:59'
        user_id  = self.user_id and self.user_id.id
        domain = [('status','=','active')]
        domain.extend([('submit_to_customer_date','>=',aud_date_start),('submit_to_customer_date','<=',aud_date_end)])
        company_id = self.company_id and self.company_id.id
        domain.extend([('company_id','=',company_id)])
        domain1 = domain + [('state','not in',('draft','design_ready','cancelled'))]
        
        sheet_ids =self.env['od.cost.sheet'].search(domain1)
        
        for sheet in sheet_ids:
            kpi_considered_sec = sheet.lead_id.kpi_considered_sec
            if not kpi_considered_sec:
                opp_id = sheet.lead_id
                opp_id.write({'kpi_considered_sec': True})

#             sheet.update_cost_sheet()
                aruba_juniper_citrix_gp,res2 = self.get_brand_sec(sheet)
                
                for line in sheet.summary_weight_line:
                    if line.pdt_grp_id.id ==2:
                        gp = line.total_gp
                        result.append((0,0,{'cost_sheet_id':sheet.id,'gp':line.total_gp,'sales':line.total_sale,'sales_aftr_disc':line.sale_aftr_disc,'cost':line.total_cost,
                                            'profit':line.profit,'profit_percent':line.profit_percent,'manpower_cost':line.manpower_cost,'product_group_id':line.pdt_grp_id.id}))
                        
                        total_gp +=gp 
                total_gp -= aruba_juniper_citrix_gp
            
        comp_data,target = self.get_bdm_component(total_gp,aud_date_start)
        return result,comp_data,target
    
    
    def get_bdm_net_data(self,sample_id, aud_date_start, aud_date_end, audit_temp_id):
        result =[]
        total_gp =0.0
        user_id  = self.user_id and self.user_id.id
        domain = [('status','=','active')]
        domain.extend([('submit_to_customer_date','>=',aud_date_start),('submit_to_customer_date','<=',aud_date_end)])
        company_id = self.company_id and self.company_id.id
        domain.extend([('company_id','=',company_id)])
        domain1 = domain + [('state','not in',('draft','design_ready','cancelled'))]
        sheet_ids =self.env['od.cost.sheet'].search(domain1)
        res_extra =[]
        for sheet in sheet_ids:
            kpi_considered = sheet.lead_id.kpi_considered
            if not kpi_considered:
                opp_id = sheet.lead_id
                opp_id.write({'kpi_considered': True})
    #             sheet.update_cost_sheet()
                aruba_juniper_citrix_gp,res2 = self.get_brand_sec(sheet)
                res_extra += res2
                for line in sheet.summary_weight_line:
                    if line.pdt_grp_id.id in (1,3):
                        gp = line.total_gp
                        result.append((0,0,{'cost_sheet_id':sheet.id,'gp':line.total_gp,'sales':line.total_sale,'sales_aftr_disc':line.sale_aftr_disc,'cost':line.total_cost,
                                            'profit':line.profit,'profit_percent':line.profit_percent,'manpower_cost':line.manpower_cost,'product_group_id':line.pdt_grp_id.id}))
                        total_gp +=gp
                total_gp += aruba_juniper_citrix_gp
           
        comp_data,target = self.get_bdm_component(total_gp,aud_date_start)
        return result,comp_data,target,res_extra        
    
    def get_bdm_net_pip_data(self,sample_id, aud_date_start, aud_date_end, audit_temp_id):
        result =[]
        
        user_id  = self.user_id and self.user_id.id
        domain = [('status','=','active')]
#         domain.extend([('submit_to_customer_date','>=',aud_date_start),('submit_to_customer_date','<=',aud_date_end)])
        
        company_id = self.company_id and self.company_id.id
        domain.extend([('company_id','=',company_id)])
        domain1 = domain + [('state','in',('submitted','handover','processed'))]
        sheet_ids =self.env['od.cost.sheet'].search(domain1)
        for sheet in sheet_ids:
#             sheet.update_cost_sheet()
            for line in sheet.summary_weight_line:
                if line.pdt_grp_id.id in (1,3):
                    gp = line.total_gp
                    if not gp:
                        sheet.update_cost_sheet()
                        break
                    else:
                        result.append((0,0,{'cost_sheet_id':sheet.id,'gp':line.total_gp,'sales':line.total_sale,'sales_aftr_disc':line.sale_aftr_disc,'cost':line.total_cost,
                                        'profit':line.profit,'profit_percent':line.profit_percent,'manpower_cost':line.manpower_cost,'product_group_id':line.pdt_grp_id.id}))
                  
        return result
    
    
    def get_bdm_dc_data(self,sample_id, aud_date_start, aud_date_end, audit_temp_id):
        result =[]
        total_gp =0.0
        user_id  = self.user_id and self.user_id.id
        domain = [('status','=','active')]
        domain.extend([('submit_to_customer_date','>=',aud_date_start),('submit_to_customer_date','<=',aud_date_end)])
        company_id = self.company_id and self.company_id.id
        domain.extend([('company_id','=',company_id)])
        domain1 = domain + [('state','not in',('draft','design_ready','cancelled'))]
        sheet_ids =self.env['od.cost.sheet'].search(domain1)
        for sheet in sheet_ids:
#             sheet.update_cost_sheet()
            
            
            for line in sheet.summary_weight_line:
                if line.pdt_grp_id.id ==3:
                    gp = line.total_gp
                    result.append((0,0,{'cost_sheet_id':sheet.id,'gp':line.total_gp,'sales':line.total_sale,'sales_aftr_disc':line.sale_aftr_disc,'cost':line.total_cost,
                                        'profit':line.profit,'profit_percent':line.profit_percent,'manpower_cost':line.manpower_cost,'product_group_id':line.pdt_grp_id.id}))
                    total_gp +=gp
            
        comp_data,target = self.get_bdm_component(total_gp,aud_date_start)
        return result,comp_data,target
    
    def tum_bdm_data(self,sample_id, aud_date_start, aud_date_end, audit_temp_id,division_id):
        result =[]
        total_gp =0.0
        domain = [('status','=','active')]
        domain.extend([('submit_to_customer_date','>=',aud_date_start),('submit_to_customer_date','<=',aud_date_end)])
        company_id = self.company_id and self.company_id.id
        domain.extend([('company_id','=',company_id)])
        domain1 = domain + [('state','not in',('draft','design_ready','cancelled'))]
        
        
        domain2=[('status','=','active')]
        domain2.extend([('approved_date','>=',aud_date_start),('approved_date','<=',aud_date_end)])
        domain2 =domain2 + [('state','not in',('draft','design_ready','cancelled','commit','returned_by_pmo','handover','waiting_po','processed','pmo'))]
        
        pdt_grp_id = self.od_division_id and self.od_division_id.pdt_grp_id and self.od_division_id.pdt_grp_id.id
        mp_sale_data = []
        mp_sale_detail_data =[]
        total_mp_sale =0.0
        branch_ids ={4:40,5:30,6:30}
       
        branch_data =[]
        annual_target = self.annual_target 
        monthly_target = annual_target/12.0
        for branch,dx in branch_ids.items():
            domain1.extend([('od_branch_id','=',branch)])
            sheet_ids =self.env['od.cost.sheet'].search(domain1)
            achieved_gp = 0.0
            for sheet in sheet_ids:
                for line in sheet.summary_weight_line:
                    if line.pdt_grp_id.id ==pdt_grp_id:
                        gp = line.total_gp
                        achieved_gp += gp
                        result.append((0,0,{'cost_sheet_id':sheet.id,'gp':line.total_gp,'sales_aftr_disc':line.sale_aftr_disc,'branch_id':branch,
                                            'product_group_id':line.pdt_grp_id.id}))
                        total_gp +=gp
            ach_target = 0.0
            branch_target = monthly_target * (dx/100.0)
            if branch_target:
                ach_target = (achieved_gp/branch_target) *100
            if ach_target>150:
                ach_target =150
            score = ach_target * (dx/100.0)
            branch_data.append((0,0,{'branch_id':branch,'branch_percent':dx,'achieved_gp':achieved_gp,'branch_target':branch_target,'ach_target':ach_target,'score':score}))
        sheet2_ids = self.env['od.cost.sheet'].search(domain2)
        for sheet in sheet2_ids:
            for line in sheet.summary_weight_line:
                if line.pdt_grp_id.id ==pdt_grp_id: 
                    total_mp_sale += line.manpower_sale
                    mp_sale_detail_data.append((0,0,{'cost_sheet_id':sheet.id,
                                        'manpower_sale':line.manpower_sale,'approved_date':sheet.approved_date}))       
        
        div_ob =self.env['od.cost.division'].browse(division_id)
        mp_sale_target =div_ob.mp_target/12.0
        target_percent =0.0
        if mp_sale_target:
            target_percent = (total_mp_sale/mp_sale_target) *100.0
        mp_sale_data.append((0,0,{'manpower_sale':total_mp_sale,'target':mp_sale_target,'target_percent':target_percent,'weight':25.0,'score':(25.0/100.0)*target_percent}))   
        comp_data,target = self.get_tum_bdm_comp(total_gp,aud_date_start,branch_data)
        return result,comp_data,mp_sale_data,mp_sale_detail_data,branch_data
        
    
   
        
    
    def get_staff_data(self,sample_id, aud_date_start, aud_date_end, audit_temp_id,division_id):
       
        branch_ids =[4,5,6]
        job_ids = [78,107]
        data=[]
        details_line =[]
        
        
        def get_required_staff(job_id,branch_id):
            ob=self.env['division.staff.req'].search([('division_id','=',division_id),('branch_id','=',branch_id),('job_id','=',job_id)],limit=1)
            required = ob.required or 1
            weight = ob.weight or 0.0
            return required ,weight
        
        def check_available(job_id,branch_id):
            emp_recs = self.env['hr.employee'].search([('job_id','=',job_id),('od_branch_id','=',branch_id),('company_id','=',6),('od_division_id','=',division_id)])
            available = 0.0
            score=0.0
            for emp in emp_recs:
                contract = self.env['hr.contract'].search([('employee_id','=',emp.id),('od_active','=',True)])
                trial_date_end = contract.trial_date_end
                today = str(dt.today())
                if today > trial_date_end:
                    details_line.append((0,0, {'user_id': emp.user_id.id,'job_id':job_id ,'branch_id':branch_id, 'joining_date': emp.od_joining_date, 'termination_date': emp.od_last_day}) )
                    available += 1
            if available >= 1:
                score = 1.0
            return score,available
        
        for branch_id in branch_ids:
            for job_id in job_ids:
                score,available = check_available(job_id,branch_id)
                required,wt = get_required_staff(job_id, branch_id)
                score = available/required
                weight = (wt/100.0) *(70.0/3.0)
                final_score = weight * score
                if score >1:
                    score=1.0
                res = {'branch_id':branch_id,
                       'job_id':job_id,
                       'required':required,
                       'available':available,
                       'req_avail': score,
                       'weight':weight,
                       'score':final_score
                    }
                data.append((0,0,res))
                
        tech_cons_job_id = 87
        ob=self.env['od.cost.division'].search([('id','=',division_id)])
        tc_req = ob.tc or 1.0
        available=0.0
        score=0.0
        emp_recs = self.env['hr.employee'].search([('job_id','=',tech_cons_job_id),('company_id','=',6),('od_division_id','=',division_id)],limit=1)
        for emp in emp_recs:
            contract = self.env['hr.contract'].search([('employee_id','=',emp.id),('od_active','=',True)])
            trial_date_end = contract.trial_date_end
            today = str(dt.today())
            if today > trial_date_end:
                details_line.append((0,0,{'user_id': emp.user_id.id,'job_id':tech_cons_job_id ,'branch_id':emp.od_branch_id.id ,'joining_date': emp.od_joining_date, 'termination_date': emp.od_last_day}))
                available += 1.0
        if available >= 1.0:
            score = 1.0
        
        weight =0.3
        score =available/tc_req
        res = {'branch_id':emp_recs.od_branch_id.id,
                   'job_id':tech_cons_job_id,
                   'required':tc_req,
                   'available':available,
                   'req_avail':available/tc_req,
                    'weight':30,
                       'score':score * 30
                       
                   
                }
        data.append((0,0,res))
        
        return data, details_line
        
 
    
    def get_tum_comp_data(self,bdm_comp,mp_sale_data,tc_comp_line,staff_data,sale_enab_score):
        wt_bdm =25.0
        wt_enab=5.0
        wt_mp =25.0
        wt_staff =20.0
        wt_tc =25.0
        bdm_score =0.0
        comp_data = []
        
        
        
        
        
        for _,_,dat in bdm_comp:
            
            bdm_score += dat.get('final_score',0.0)
        
        comp_data.append((0,0,
                              {'name':'BDM Score',
                               'weight':wt_bdm,
                               'score':bdm_score,
                               'final_score':bdm_score}
                              ))
        
        
        comp_data.append((0,0,
                              {'name':'Sale Enablement Score',
                               'weight':wt_enab,
                               'score':sale_enab_score,
                               'final_score':sale_enab_score*(wt_enab/100.0)}
                              ))
        
        
        
        mp_score =0.0
        for _,_,dat in mp_sale_data:
            mp_score += dat.get('target_percent')
        
        if mp_score >150:
            mp_score =150
        comp_data.append((0,0,
                              {'name':'MP Sales Score',
                               'weight':wt_mp,
                               'score':mp_score,
                               'final_score':mp_score*(wt_mp/100.0)}
                              ))
        
        tc_score =0.0
        for _,_,dat in tc_comp_line:
            tc_score += dat.get('final_score',0.0)
        
        comp_data.append((0,0,
                              {'name':'Technology Consultant Score',
                               'weight':wt_tc,
                               'score':tc_score,
                               'final_score':tc_score*(wt_tc/100.0)}
                              ))
        
        
        staff_score=0.0
        for _,_,dat in staff_data:
            staff_score += dat.get('score',0.0)
            
        
        comp_data.append((0,0,
                              {'name':'Staff Score',
                               'weight':wt_staff,
                               'score':staff_score,
                               'final_score':staff_score*(wt_staff/100.0)}
                              ))
        
        
        
         
        return comp_data
    
    
    
    def get_tum_session_data(self,audit_month,divsion_id,tgt):
        data =[]
        sale_enb =self.env['sale.enablement']
        
        sale_enab_ids = sale_enb.search([('od_division_id','=',divsion_id),('month','=',audit_month)])
        score_board =[]
        for enab in sale_enab_ids:
            if enab.score:
                score_board.append(1.0)
            data.append((0,0,{'sale_enab_id':enab.id,'score':enab.score,'division_id':enab.od_division_id and enab.od_division_id.id or False,
                              'user_id':enab.user_id and enab.user_id.id ,'date':enab.date
                              }))
        score = (len(score_board)/tgt ) *100.0
        if score >100.0:
            score =100.0
        return data,score
    
    
    def get_tum_data(self,sample_id, aud_date_start, aud_date_end, audit_temp_id,division_id):
        bdm_sample_data,bdm_comp,mp_sale_data,mp_sale_detail_data,branch_data = self.tum_bdm_data(sample_id, aud_date_start, aud_date_end, audit_temp_id,division_id)
        audit_date_start = aud_date_start
        audit_date_start = datetime.strptime(audit_date_start,'%Y-%m-%d')
        audit_month = audit_date_start.month
        tgt=2.0
        sale_enab_data,sale_enab_score = self.get_tum_session_data(audit_month, division_id, tgt)
        
        tc = self.search([('od_division_id','=',division_id),('job_id','=',87)],limit=1)
        tc_comp_line =[]
        if tc:
            opp_sample_line,team_line,presale_comp_data,utl_data,fot_data,tech_comp_data,tc_comp_line = tc.get_tc_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
        staff_data,staff_detail_line = self.get_staff_data(sample_id, aud_date_start, aud_date_end, audit_temp_id, division_id)
        comp_data = self.get_tum_comp_data(bdm_comp, mp_sale_data, tc_comp_line, staff_data,sale_enab_score)
        return bdm_sample_data,bdm_comp,mp_sale_data,tc_comp_line,staff_data,staff_detail_line,comp_data,sale_enab_score,sale_enab_data,mp_sale_detail_data,branch_data
    
    def get_bdm_ksa_data(self,sample_id, aud_date_start, aud_date_end, audit_temp_id):
        result = []
        user_id  = self.user_id and self.user_id.id
        domain = [('status','=','active')]
        domain.extend([('submit_to_customer_date','>=',aud_date_start),('submit_to_customer_date','<=',aud_date_end)])
        company_id = self.company_id and self.company_id.id
        domain.extend([('company_id','=',company_id)])
        
        domain1 = domain + [('state','not in',('draft','design_ready','cancelled'))]
        ksa_aud_conf = audit_temp_id.bdm_ksa_line 
        total_month_incent = sum([line.month_incent for line in ksa_aud_conf])
        total_target = sum([line.gp_target for line in ksa_aud_conf])
        total = 0.0
        for line in ksa_aud_conf:
            branch_id = line.branch_id and line.branch_id.id or False
            gp_target = line.gp_target 
            month_incent = line.month_incent
            domain1 = domain1 + [('od_branch_id','=',branch_id)]     
            achieved_gp =0.0 
            sheet_ids = self.env['od.cost.sheet'].search(domain1)
            for sheet in sheet_ids:
                for line in sheet.summary_weight_line:
                    if line.pdt_grp_id.id ==3:
                        gp = line.total_gp
                        
                        achieved_gp +=gp
            
            branch_gp_point = (achieved_gp/gp_target)*100.0
            
            result.append((0,0,{'branch_id':branch_id,'gp_target':gp_target,'gp':achieved_gp,
                                'branch_gp_point':branch_gp_point,'month_incent':month_incent}))
            total += branch_gp_point * (month_incent/total_month_incent)
            comp_data = self.get_bdm_ksa_component(total)
        return result,comp_data,total_target
    
    def get_bdm_dc_pip_data(self,sample_id, aud_date_start, aud_date_end, audit_temp_id):
        result =[]
        
        user_id  = self.user_id and self.user_id.id
        domain = [('status','=','active')]
#         domain.extend([('submit_to_customer_date','>=',aud_date_start),('submit_to_customer_date','<=',aud_date_end)])
        
        company_id = self.company_id and self.company_id.id
        domain.extend([('company_id','=',company_id)])
        domain1 = domain + [('state','in',('submitted','handover','processed'))]
        sheet_ids =self.env['od.cost.sheet'].search(domain1)
        for sheet in sheet_ids:
#             sheet.update_cost_sheet()
            for line in sheet.summary_weight_line:
                if line.pdt_grp_id.id ==3:
                    gp = line.total_gp
                    if not gp:
                        sheet.update_cost_sheet()
                        break
                    else:
                        result.append((0,0,{'cost_sheet_id':sheet.id,'gp':line.total_gp,'sales':line.total_sale,'sales_aftr_disc':line.sale_aftr_disc,'cost':line.total_cost,
                                        'profit':line.profit,'profit_percent':line.profit_percent,'manpower_cost':line.manpower_cost,'product_group_id':line.pdt_grp_id.id}))
                  
        return result
    
    
    
    def get_supplier_paid(self,supplier_invoice):
        paid = 0.0
        for sup_inv in supplier_invoice:
            currency = sup_inv.currency_id
            company_currency = sup_inv.company_id.currency_id
            bal  = sup_inv.amount_total - sup_inv.residual 
            paid += currency.compute(bal,company_currency,round=False)
        paid = (paid/1.05)
        if abs(paid) <1:
            paid =0.0
        return paid
    
    def get_supplier_amount(self,supplier_invoice):
        amount = 0.0
        for sup_inv in supplier_invoice:
            currency = sup_inv.currency_id
            company_currency = sup_inv.company_id.currency_id
            bal  = sup_inv.amount_total
            amount += currency.compute(bal,company_currency,round=False)
        amount = (amount/1.05)
        if abs(amount) <1:
            amount =0.0
        return amount
    
    def get_supplier_amount_from_lines(self, analytic_id):
        amount = 0.0
        invoice_line_pool = self.env['account.invoice.line']
        invoice_ids = self.env['account.invoice'].search([('type','=','in_invoice'),('state','not in',('draft','cancel'))]).ids
        domain = [('account_analytic_id','=',analytic_id), ('invoice_id','in',invoice_ids)]
        invoice_lines = invoice_line_pool.search(domain)
        for line in invoice_lines:
            sup_inv = line.invoice_id
            qty = line.quantity
            unit_price = line.price_unit
            price_total = qty*unit_price
            currency = sup_inv.currency_id
            company_currency = sup_inv.company_id.currency_id
            amount += currency.compute(price_total,company_currency,round=False)
        return amount
    
    def get_general_cost(self,analytic):
        analytic_id = analytic.id
        move_line_pool = self.env['account.move.line']
        company_id = analytic.company_id and analytic.company_id.id 
        wip_account = [False]
        journal_id = False
        if company_id ==6:
            wip_account = [5732]
            journal_id =41
        if company_id ==1:
            wip_account = [2128,2137]
            journal_id =5
       
        domain = [('analytic_account_id','=',analytic_id),('journal_id','=',journal_id),('account_id','in',wip_account)]
        move_line_ids = move_line_pool.search(domain)
        general_cost = sum([(mvl.debit-mvl.credit) for mvl in move_line_ids if mvl.od_state =='posted'])
        if company_id ==6:
            supplier_account_ids = [5296,5297]
            domain2= [('analytic_account_id','=',analytic_id),('journal_id','=',journal_id),('account_id','in',supplier_account_ids),('credit','>',0.0),('reconcile_id','=',False)]
            move_lines =move_line_pool.search(domain2)
            move_ids = [mvl.move_id.id for mvl in move_lines]
            domain3=[('analytic_account_id','=',analytic_id),('journal_id','=',journal_id),('account_id','in',wip_account),('move_id','not in',move_ids)]
            move_line_ids = move_line_pool.search(domain3)
            general_cost = sum([(mvl.debit-mvl.credit) for mvl in move_line_ids if mvl.od_state =='posted'])
        return general_cost
    
    def get_refunded_invoices(self,project_id):
        invoice_pool = self.env['account.invoice']
        customer_refund = invoice_pool.search([('od_analytic_account','=',project_id),('type','=','out_refund'),('state','not in',('draft','cancel'))])
        inv_ids = []
        for inv in customer_refund:
            origin = inv.origin
            invoice = invoice_pool.search([('name','=',origin),('type','=','out_invoice')],limit=1)
            if invoice:
                inv_ids.append(invoice.id)
        return tuple(set(inv_ids))
    
    def get_collected_invoice_amt(self,analytic_id):
        already_invoiced  = self.env['account.invoice'].search([('od_analytic_account','=',analytic_id),('type','=','out_invoice'),('state','in',('manual','paid'))])
        already_invoiced_amt = sum([inv.amount_total for inv in already_invoiced])  
        partially_collected = self.env['account.invoice'].search([('od_analytic_account','=',analytic_id),('type','=','out_invoice'),('state','in',('accept','open'))])
        partially_collected_amt = sum([inv.amount_total  - inv.residual for inv in partially_collected])
        already_invoiced_amt += partially_collected_amt
        customer_refund = self.env['account.invoice'].search([('od_analytic_account','=',analytic_id),('type','=','out_refund'),('state','not in',('draft','cancel'))])
        customer_refund_amount = sum([inv.amount_total for inv in customer_refund])
        in_collected = already_invoiced_amt - customer_refund_amount
        collected = (in_collected/1.05)
        if abs(collected) <1:
            collected =0.0
        
        dist_line = self.env['od.dist.line']
        dom3 = [('analytic_id','=',analytic_id)]
        dist_line_ids = dist_line.search(dom3)
        for line in dist_line_ids:
            inv_id = line.invoice_id
            if not inv_id.od_refund:
                value = line.value
                if inv_id.state == 'paid':
                    collected +=(value/100.0) * inv_id.amount_untaxed
        
        return collected
    
    
    def get_cust_invoice_untaxed_amount(self,analytic_id):
        invoice_pool = self.env['account.invoice']
        domain = [('od_analytic_account','=',analytic_id),('type','=','out_refund'),('state','not in',('draft','cancel'))]
        inv_ids = invoice_pool.search(domain)
        refund_amount_total = sum([inv.amount_untaxed for inv in inv_ids])
        
        domain2 = [('od_analytic_account','=',analytic_id),('type','=','out_invoice'),('state','not in',('draft','cancel'))]
        inv_ids = invoice_pool.search(domain2)
        amount_total = sum([inv.amount_untaxed for inv in inv_ids])
        

        dist_line = self.env['od.dist.line']
        dom3 = [('analytic_id','=',analytic_id)]
        dist_line_ids = dist_line.search(dom3)
        for line in dist_line_ids:
            inv_id = line.invoice_id
            if not inv_id.od_refund:
                value = line.value
                if inv_id.state not in ('draft','cancel'):
                    amount_total +=(value/100.0) * inv_id.amount_untaxed
    
        return amount_total -refund_amount_total
            
    #original function
    def get_pmo_dir_data(self,sample_id, aud_date_start, aud_date_end, audit_temp_id):
        open_projects = []
        closed_projects =[]
        analytic_pool = self.env['account.analytic.account']
        company_id = self.company_id and self.company_id.id
        open_project_ids = analytic_pool.search([('company_id','=',company_id),('od_type_of_project','not in',('credit','comp_gen','poc','amc_view','o_m_view','parent_level0')),('state','not in',('close','cancelled')),('exclude_pmo_kpi','=',False)])
        closed_project_ids = analytic_pool.search([('company_id','=',company_id),('od_type_of_project','not in',('credit','comp_gen','poc','amc_view','o_m_view','parent_level0')),('state','=','close'),('od_closing_date','>','31-Dec-18'), ('exclude_pmo_kpi','=',False)])
        sale_pool = self.env['sale.order']
        invoice_pool = self.env['account.invoice']
        total_collected =0.0
        total_paid =0.0
        inv_amount = 0.0
        timesheet_pool = self.env['hr.analytic.timesheet']
        for project in open_project_ids:
  
            sale = sale_pool.search([('project_id','=',project.id),('state','!=','cancel')],limit=1)
            amount_total = project.od_amended_sale_price
            discount = abs(sale.od_discount) or 0.0
            project_value = amount_total
#             refunded_invoices = self.get_refunded_invoices(project.id)
#             print "refunded invoicesss>>>>>>>>open",refunded_invoices
            domain1 = [('od_analytic_account','=',project.id),('type','=','out_invoice'),('state','not in',('draft','cancel'))] 
#             if refunded_invoices:
#                 domain1.extend([('id','not in',refunded_invoices)])
            collected = self.get_collected_invoice_amt(project.id)
            inv_amount  = self.get_cust_invoice_untaxed_amount(project.id)
            
            supplier_invoice = invoice_pool.search([('od_analytic_account','=',project.id),('type','=','in_invoice'),('state','not in',('draft','cancel'))])
            supplier_refund= invoice_pool.search([('od_analytic_account','=',project.id),('type','=','in_refund'),('state','not in',('draft','cancel'))])
            supplier_refund_amount = self.get_supplier_paid(supplier_refund)
            paid = self.get_supplier_paid(supplier_invoice)
            paid = paid - supplier_refund_amount
            
            if project.od_pmo_collected:
                collected = project.od_collected
            if project.od_manual_invoice:
                inv_amount = project.od_manual_invoice_amnt
            if project.od_pmo_paid:
                paid = project.od_paid
                
            total_collected += collected
            total_paid += paid
            
            #manpower_cost = sum([tm.normal_amount for tm in timesheet_pool.search([('account_id','=',project.id),('date','<=',aud_date_end)])])
            manpower_cost = project.od_timesheet_amount2
            actual_outsourced = project.od_actual_outsource
            general_cost = self.get_general_cost(project)
            if project.od_pmo_gc:
                general_cost = project.od_gc 
            if project.od_pmo_mp:
                manpower_cost = project.od_tm
            total_paid += manpower_cost
            total_paid += general_cost
            total_paid += actual_outsourced
            
            open_projects.append((0,0,{'analytic_id':project.id,'project_value':project_value,
                                       'inv_amount':inv_amount,
                                       'collected':collected,'paid':paid,'manpower_cost':manpower_cost,'general_cost':general_cost, 'actual_outsource': actual_outsourced}))
              
        for project in closed_project_ids:
            sale = sale_pool.search([('project_id','=',project.id),('state','!=','cancel')],limit=1)
            amount_total = project.od_amended_sale_price
            discount = abs(sale.od_discount) or 0.0
            project_value = amount_total
#             refunded_invoices = self.get_refunded_invoices(project.id)
            domain2 = [('od_analytic_account','=',project.id),('type','=','out_invoice'),('state','not in',('draft','cancel'))] 
#             if refunded_invoices:
#                 domain2.extend([('id','not in',refunded_invoices)])
#             print "refunded invoicesss>>>>>>>>closedß",refunded_invoices,domain2
            supplier_invoice = invoice_pool.search([('od_analytic_account','=',project.id),('type','=','in_invoice'),('state','not in',('draft','cancel'))])
            supplier_refund= invoice_pool.search([('od_analytic_account','=',project.id),('type','=','in_refund'),('state','not in',('draft','cancel'))])
            supplier_inv_amount =self.get_supplier_amount(supplier_invoice)
            #manpower_cost = sum([tm.normal_amount for tm in timesheet_pool.search([('account_id','=',project.id),('date','<=',aud_date_end)])])
            manpower_cost = project.od_timesheet_amount2
            inv_amount  = self.get_cust_invoice_untaxed_amount(project.id)
            
            supplier_refund_amount =sum([inv.amount_total - inv.residual for inv in supplier_refund])
            supplier_refund_amount = self.get_supplier_paid(supplier_refund)
            supplier_inv_amount = supplier_inv_amount - supplier_refund_amount
            #collected = sum([inv.amount_total - inv.residual for inv in customer_invoice])
            paid = self.get_supplier_paid(supplier_invoice)
            #collected = collected - customer_refund_amount
            collected = self.get_collected_invoice_amt(project.id)
            paid = paid - supplier_refund_amount
            general_cost = self.get_general_cost(project)
            if project.od_pmo_collected:
                collected = project.od_collected
            if project.od_manual_invoice:
                inv_amount = project.od_manual_invoice_amnt
            if project.od_pmo_paid:
                paid = project.od_paid
            if project.od_pmo_gc:
                general_cost = project.od_gc 
            if project.od_pmo_mp:
                manpower_cost = project.od_tm
            a = int(collected)
            a1 = int(inv_amount)
            a2 = int(project_value)
            b = int(paid)
            b1 = int(supplier_inv_amount)
            diff = a2 - a
            if (a >= a1 or diff <= 2) and (b >= b1):
                continue
#             if (int(collected) >= int(inv_amount) or int(collected) >= int(project_value)) and int(paid) >= int(supplier_inv_amount):
#                 continue
#                 if sample_id:
#                     analytic_id = project.id 
#                     pmo_closed_project = self.env['pmo.closed.project.sample']
#                     closed_data = pmo_closed_project.search([('sample_id','=',sample_id.id),('analytic_id','=',analytic_id)])
#                     if not closed_data:
#                         continue
            total_paid += project_value
#             total_paid += manpower_cost
#             total_paid += general_cost
            total_collected += collected
            closed_projects.append((0,0,{'analytic_id':project.id,
                                         'inv_amount':inv_amount,
                                         'project_value':project_value,'collected':collected,'paid':paid,'manpower_cost':manpower_cost,'general_cost':general_cost})) 
        res =0.0
        if total_paid:
            res = total_collected/float(total_paid)
        comp_line =[(0,0,{'name':'Cash Flow Management','weight':100,'score':res*100.0,'final_score':res*100.0})]
        mgr_score = self.get_mgr_feedback()
        if mgr_score:
            comp_line.append((0,0,
                              {'name':'Direct Manager Feedback',
                               'weight':-20,
                               'score':mgr_score,
                               'final_score':mgr_score}
                              ))
        return open_projects,closed_projects,comp_line

#     #copy function
#     def get_pmo_dir_data(self,sample_id, aud_date_start, aud_date_end, audit_temp_id):
#         open_projects = []
#         closed_projects =[]
#         analytic_pool = self.env['account.analytic.account']
#         company_id = self.company_id and self.company_id.id
#         open_project_ids = analytic_pool.search([('company_id','=',company_id),('od_type_of_project','not in',('credit','comp_gen','poc','amc_view','o_m_view','parent_level0')),('state','not in',('close','cancelled'))])
#         closed_project_ids = analytic_pool.search([('company_id','=',company_id),('od_type_of_project','not in',('credit','comp_gen','poc','amc_view','o_m_view','parent_level0')),('state','=','close')])
#         sale_pool = self.env['sale.order']
#         invoice_pool = self.env['account.invoice']
#         total_collected =0.0
#         total_paid =0.0
#         timesheet_pool = self.env['hr.analytic.timesheet']
#         for project in open_project_ids:
#  
#             sale = sale_pool.search([('project_id','=',project.id),('state','!=','cancel')],limit=1)
#             amount_total = project.od_amended_sale_price
#             discount = abs(sale.od_discount) or 0.0
#             project_value = amount_total + (amount_total *.05)
#              
#             #collected amount for a project
#             reciept_ids = self.env['account.voucher'].search([('type','=','receipt'),('state','=','posted')]).ids
#             
#             voucher_distribution = self.env['od.voucher.analytic.distribution']
#             collected = 0.0
#             reciept_distribution_lines = voucher_distribution.search([('analytic_id','=',project.id),('voucher_id','in', reciept_ids)])
#             for line in reciept_distribution_lines:
#                 collected +=line.amount
#             #paid amount for a project
#             payment_ids = self.env['account.voucher'].search([('type','=','payment'),('state','=','posted')]).ids
#             paid = 0.0
#             payment_distribution_lines = voucher_distribution.search([('analytic_id','=',project.id),('voucher_id','in', payment_ids)])
#             for line in payment_distribution_lines:
#                 paid +=line.amount
#  
#             if project.od_pmo_collected:
#                 collected = project.od_collected
#             if project.od_pmo_paid:
#                 paid = project.od_paid
#             total_collected += collected
#             total_paid += paid
#             manpower_cost = sum([tm.normal_amount for tm in timesheet_pool.search([('account_id','=',project.id),('date','<=',aud_date_end)])])
#             general_cost = self.get_general_cost(project)
#             if project.od_pmo_gc:
#                 general_cost = project.od_gc
#             if project.od_pmo_mp:
#                 manpower_cost = project.od_tm
#             total_paid += manpower_cost
#             total_paid += general_cost
#             open_projects.append((0,0,{'analytic_id':project.id,'project_value':project_value,'collected':collected,'paid':paid,'manpower_cost':manpower_cost,'general_cost':general_cost}))
#              
#         for project in closed_project_ids:
#              
#  
#             sale = sale_pool.search([('project_id','=',project.id),('state','!=','cancel')],limit=1)
#             amount_total = project.od_amended_sale_price
#             discount = abs(sale.od_discount) or 0.0
#             project_value = amount_total + (amount_total *.05)
# #             refunded_invoices = self.get_refunded_invoices(project.id)
#             domain2 = [('od_analytic_account','=',project.id),('type','=','out_invoice'),('state','not in',('draft','cancel'))] 
# #             if refunded_invoices:
# #                 domain2.extend([('id','not in',refunded_invoices)])
# #             print "refunded invoicesss>>>>>>>>closedß",refunded_invoices,domain2
#  
#             #collected amount for a project
#             reciept_ids = self.env['account.voucher'].search([('type','=','receipt'),('state','=','posted')]).ids
#             voucher_distribution = self.env['od.voucher.analytic.distribution']
#             collected = 0.0
#             reciept_distribution_lines = voucher_distribution.search([('analytic_id','=',project.id),('voucher_id','in', reciept_ids)])
#             for line in reciept_distribution_lines:
#                 collected +=line.amount
#             manpower_cost = sum([tm.normal_amount for tm in timesheet_pool.search([('account_id','=',project.id),('date','<=',aud_date_end)])])
#  
#             #paid amount for a project
#             payment_ids = self.env['account.voucher'].search([('type','=','payment'),('state','=','posted')]).ids
#             paid = 0.0
#             payment_distribution_lines = voucher_distribution.search([('analytic_id','=',project.id),('voucher_id','in', payment_ids)])
#             for line in payment_distribution_lines:
#                 paid +=line.amount
#             supplier_inv_amount =self.get_supplier_amount_from_lines(project.id)
#             print project,supplier_inv_amount
#             general_cost = self.get_general_cost(project)
#             if project.od_pmo_collected:
#                 collected = project.od_collected
#             if project.od_pmo_paid:
#                 paid = project.od_paid
#             if project.od_pmo_gc:
#                 general_cost = project.od_gc 
#             if project.od_pmo_mp:
#                 manpower_cost = project.od_tm
#             if collected>=project_value and paid >=supplier_inv_amount:
#                 continue
# #                 if sample_id:
# #                     analytic_id = project.id 
# #                     pmo_closed_project = self.env['pmo.closed.project.sample']
# #                     closed_data = pmo_closed_project.search([('sample_id','=',sample_id.id),('analytic_id','=',analytic_id)])
# #                     if not closed_data:
# #                         continue
#             total_paid += project_value
# #             total_paid += manpower_cost
# #             total_paid += general_cost
#             total_collected += collected
#             closed_projects.append((0,0,{'analytic_id':project.id,'project_value':project_value,'collected':collected,'paid':paid,'manpower_cost':manpower_cost,'general_cost':general_cost})) 
#         res =0.0
#         if total_paid:
#             res = total_collected/float(total_paid)
#         comp_line =[(0,0,{'name':'Cash Flow Management','weight':100,'score':res*100.0,'final_score':res*100.0})]
#         mgr_score = self.get_mgr_feedback()
#         if mgr_score:
#             comp_line.append((0,0,
#                               {'name':'Direct Manager Feedback',
#                                'weight':-20,
#                                'score':mgr_score,
#                                'final_score':mgr_score}
#                               ))
#         return open_projects,closed_projects,comp_line
    
    

    
    
    def get_score_from_comp_data(self,vals):
        res =0.0
        for _,_,val in vals:
            final_score = val.get('final_score',0.0)
            res += final_score 
        return res
    
    
    
    def get_tc_data(self,sample_id, aud_date_start, aud_date_end, audit_temp_id):
        opp_sample_line,team_line,presale_comp_data = self.get_presale_mgr_vals_tc(sample_id, aud_date_start, aud_date_end, audit_temp_id)
        utl_data,fot_data,tech_comp_data = self.get_tech_cons_ps_vals(sample_id, aud_date_start, aud_date_end, audit_temp_id)
        presale_score = self.get_score_from_comp_data(presale_comp_data)
        tech_score = self.get_score_from_comp_data(tech_comp_data)
        wt_tech =0.7
        wt_presale =0.3
        comp_line =[(0,0,{'name':'Technical Activity','weight':wt_tech *100,'score':tech_score,'final_score':wt_tech * tech_score}),
                    (0,0,{'name':'Pre-sale Productivity','weight':wt_presale *100,'score':presale_score,'final_score':wt_presale * presale_score})
                    ]
        mgr_score = self.get_mgr_feedback()
        if mgr_score:
            comp_line.append((0,0,
                              {'name':'Direct Manager Feedback',
                               'weight':-20,
                               'score':mgr_score,
                               'final_score':mgr_score}
                              ))
        return opp_sample_line,team_line,presale_comp_data,utl_data,fot_data,tech_comp_data,comp_line
    
    def update_opp_kpi_consideration(self, bdm_net_sample_line):
        for line in bdm_net_sample_line:
            opp_id = line.cost_sheet_id.lead_id
            opp_id.write({'kpi_considered': False})
        return True
    
    def update_opp_kpi_sec_consideration(self, bdm_net_sample_line):
        for line in bdm_net_sample_line:
            opp_id = line.cost_sheet_id.lead_id
            opp_id.write({'kpi_considered_sec': False})
        return True

    
    def days_between_datetime(self,d1, d2):
        from datetime import datetime
        d1 = datetime.strptime(d1, DEFAULT_SERVER_DATETIME_FORMAT)
        d2 = datetime.strptime(d2, DEFAULT_SERVER_DATETIME_FORMAT)
        return abs((d2 - d1).days)+1
    
    def get_po_sample_data(self,sample_id,aud_date_start,aud_date_end,audit_temp_id):
        result =[]
        score_board =[]
        user_id  = self.user_id and self.user_id.id
        domain = [('date_approve','>=',aud_date_start),('date_approve','<=',aud_date_end),('validator','=',user_id),('state','in',('approved','done'))]
        company_id = self.company_id and self.company_id.id
        domain.extend([('company_id','=',company_id)])
        po_ids = self.env['purchase.order'].search(domain)
        for po in po_ids:
            po_id = po.id
            cost_saving = po.od_cost_saving
            po_log = self.env['purchase.order.log']
            second_date = po_log.search([('order_id','=',po_id),('state','=','second')]).date
            confirmed_date =po_log.search([('order_id','=',po_id),('state','=','confirm')]).date
            days = self.days_between_datetime(second_date, confirmed_date)
            score =100
            if days >3:
                score=0.0
            if cost_saving:
                score +=15.0
            result.append((0,0,{'po_id':po_id,'score':score}))
            score_board.append(score)
        avg_score = self.get_avg_score(score_board)
        comp_data = [(0,0,{'name':'PO Average Score','score':avg_score,'weight':100,'final_score':avg_score})]
        return result,comp_data
        
    def update_audit_sample(self,sample_id,aud_date_start,aud_date_end,audit_temp_id):
        type = audit_temp_id.type
        user_id  = self.user_id and self.user_id.id
        employee_id = self.id
        dt_start = aud_date_start
        result = []
        if type =='post_sales':
            result,comp_data,utilization = self.get_post_sales_vals(sample_id, aud_date_start, aud_date_end)
            sample_id.post_sale_sample_line.unlink()
            sample_id.comp_line.unlink()
            sample_id.write({'post_sale_sample_line':result,'comp_line':comp_data,'utilization':utilization})
        
        if type =='ttl':
            result,fot_data,comp_data = self.get_ttl_vals(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            sample_id.utl_sample_line.unlink()
            sample_id.ttl_fot_line.unlink()
            sample_id.comp_line.unlink()
            sample_id.write({'utl_sample_line':result,'ttl_fot_line':fot_data,'comp_line':comp_data})
        
        if type == 'pre_sales':
            opp_sample_line,comp_data = self.get_presale_vals(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            sample_id.opp_sample_line.unlink()
            sample_id.comp_line.unlink()
            sample_id.write({'opp_sample_line':opp_sample_line,'comp_line':comp_data})
        if type  == 'pre_sales_mgr':
            opp_sample_line,team_line,comp_data = self.get_presale_mgr_vals(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            sample_id.opp_sample_line.unlink()
            sample_id.comp_line.unlink()
            sample_id.team_line.unlink()
            sample_id.write({'opp_sample_line':opp_sample_line,'comp_line':comp_data,'team_line':team_line})
        if type =='tc':
            opp_sample_line,team_line,presale_comp_data,utl_data,fot_data,tech_comp_data,comp_line = self.get_tc_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            sample_id.utl_sample_line.unlink()
            sample_id.ttl_fot_line.unlink()
            sample_id.opp_sample_line.unlink()
            
            sample_id.tc_tech_comp_line.unlink()
            sample_id.tc_presale_comp_line.unlink()
            
            sample_id.team_line.unlink()
            sample_id.comp_line.unlink()
            
            sample_id.write({'utl_sample_line':utl_data,'ttl_fot_line':fot_data,
                             'opp_sample_line':opp_sample_line,'comp_line':comp_line,
                             'tc_tech_comp_line':tech_comp_data,
                             'tc_presale_comp_line':presale_comp_data,
                             'team_line':team_line})
        
        
        if type == 'tum':
            division_id = self.od_division_id and self.od_division_id.id 
            bdm_sample_line,bdm_comp_line,mp_sale_data,tc_comp_line,staff_data,staff_detail_line,comp_data,sale_enab_score,sale_enab_data,mp_sale_detail_data,branch_data = self.get_tum_data(sample_id, aud_date_start, aud_date_end, audit_temp_id,division_id)
            sample_id.tum_bdm_sample_line.unlink()
            sample_id.tum_bdm_comp_line.unlink()
            sample_id.tum_mp_sale_line.unlink()
            sample_id.tum_tc_comp_line.unlink()
            sample_id.tum_staff_data_line.unlink()
            sample_id.tum_staff_data_detail_line.unlink()
            sample_id.comp_line.unlink()
            sample_id.tum_sale_enab_line.unlink()
            sample_id.tum_mp_sale_detail_line.unlink()
            sample_id.tum_bdm_branch_line.unlink()
            sample_id.write({'tum_bdm_sample_line':bdm_sample_line,'tum_bdm_comp_line':bdm_comp_line,'tum_mp_sale_line':mp_sale_data,
                             'tum_tc_comp_line':tc_comp_line,'tum_staff_data_line':staff_data,
                             'tum_staff_data_detail_line':staff_detail_line,'comp_line':comp_data,'tum_sale_eanb_score':sale_enab_score,
                             'tum_sale_enab_line':sale_enab_data,
                             'tum_mp_sale_detail_line':mp_sale_detail_data,
                             'tum_bdm_branch_line':branch_data
                             })
        
        if type == 'sales_acc_mgr':
            today = dt.today()
            day = today.day
            achieved_line,achieved_total = self.get_sales_achieved_data(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            commit_total = sample_id.commit_total
            component_data,target = self.get_sales_acc_mgr_component(commit_total,achieved_total)
            sample_id.comp_line.unlink()
            sample_id.achieved_gp_line.unlink()
            sample_id.write({'achieved_gp_line':achieved_line,'comp_line':component_data,'target':target})
            self.write({'commit_total':commit_total})
        
        if type == 'service_sale_spl':
            today = dt.today()
            day = today.day
            achieved_line,achieved_total = self.get_sales_spl_achieved_data(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            commit_total = sample_id.commit_total
            component_data = self.get_sales_spl_component(commit_total,achieved_total)
            sample_id.comp_line.unlink()
            sample_id.achieved_gp_line.unlink()
            sample_id.write({'achieved_gp_line':achieved_line,'comp_line':component_data})
            self.write({'commit_total':commit_total})
        
        if type == 'sm':
            achieved_gp_line,team_line,comp_line,cf_data,cf_summary,cert_data,cert_summary,sale_enab_detail,sale_enab_summary = self.get_sm_data(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            sample_id.comp_line.unlink()
            sample_id.achieved_gp_line.unlink()
            sample_id.team_line.unlink()
            sample_id.sm_cf_line.unlink()
            sample_id.sm_cf_summary.unlink()
            sample_id.sm_cert_detail.unlink()
            sample_id.sm_cert_summary.unlink()
            sample_id.sm_enab_detail.unlink()
            sample_id.sm_enab_summary.unlink()
            sample_id.write({'achieved_gp_line':achieved_gp_line,'comp_line':comp_line,'team_line':team_line,
                             'sm_cf_line':cf_data,'sm_cf_summary':cf_summary,'sm_cert_detail':cert_data,
                             'sm_cert_summary':cert_summary,'sm_enab_detail':sale_enab_detail,'sm_enab_summary':sale_enab_summary})
        if type == 'pm':

            day_score_vals,cost_control_vals,invoice_schedule_vals,compliance_vals,pm_sch_line,comp_line = self.get_pm_data(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            sample_id.dayscore_line.unlink()
            sample_id.cost_control_line.unlink()
            sample_id.invoice_schedule_line.unlink()
            sample_id.compliance_line.unlink()
            sample_id.pm_sch_line.unlink()
            sample_id.comp_line.unlink()
            sample_id.write({'dayscore_line':day_score_vals,'cost_control_line':cost_control_vals,
                             'invoice_schedule_line':invoice_schedule_vals,
                             'pm_sch_line':pm_sch_line,
                             'compliance_line':compliance_vals,'comp_line':comp_line})
            
        
        if type == 'sde':
            day_score_vals,hd_line,compliance_vals,comp_line = self.get_sde_data(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            sample_id.sde_day_score_line.unlink()
            sample_id.hd_line.unlink()
            sample_id.compliance_line.unlink()
            sample_id.comp_line.unlink()
            sample_id.write({'sde_day_score_line':day_score_vals,'hd_line':hd_line,
                         'compliance_line':compliance_vals,'comp_line':comp_line})
            
        
        if type == 'sde_ksa':
            day_score_vals,hd_line,compliance_vals,comp_line = self.get_sde_data_ksa(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            sample_id.sde_day_score_line.unlink()
            sample_id.hd_line.unlink()
            sample_id.compliance_line.unlink()
            sample_id.comp_line.unlink()
            sample_id.write({'sde_day_score_line':day_score_vals,'hd_line':hd_line,
                         'compliance_line':compliance_vals,'comp_line':comp_line})
            
        if type == 'sdm':
            team_day_line,team_hd_line,comp_line = self.get_sdm_data(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            sample_id.comp_line.unlink()
            sample_id.team_hd_line.unlink()
            sample_id.team_day_line.unlink()
            sample_id.write({'team_day_line':team_day_line,'comp_line':comp_line,'team_hd_line':team_hd_line})
            
        
        if type == 'pdm':
            day_score_vals,cost_control_vals,invoice_schedule_vals,compliance_vals,pm_sch_line,team_line,my_comp_line,comp_line = self.get_pdm_data(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            
            sample_id.dayscore_line.unlink()
            sample_id.cost_control_line.unlink()
            sample_id.invoice_schedule_line.unlink()
            sample_id.compliance_line.unlink()
            sample_id.pm_sch_line.unlink()
            sample_id.my_comp_line.unlink()
            sample_id.comp_line.unlink()
            sample_id.team_line.unlink()
            sample_id.write({'dayscore_line':day_score_vals,'cost_control_line':cost_control_vals,
                             'invoice_schedule_line':invoice_schedule_vals,
                             'pm_sch_line':pm_sch_line,
                             'compliance_line':compliance_vals,'team_line':team_line,'my_comp_line':my_comp_line,'comp_line':comp_line})
        
        if type == 'bdm':
            bmd_costsheet_line,comp_line,target = self.get_bdm_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            sample_id.bmd_costsheet_line.unlink()
            sample_id.comp_line.unlink()
            sample_id.write({'bmd_costsheet_line':bmd_costsheet_line,'comp_line':comp_line,'target':target})
        if type == 'bdm_sec':
            self.update_opp_kpi_sec_consideration(sample_id.bdm_sec_sample_line)
            self.update_opp_kpi_sec_consideration(sample_id.bdm_sec_pip_sample_line)
            bdm_sec_sample_line,comp_line,target = self.get_bdm_sec_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            pipline_data = self.get_bdm_sec_pip_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            sample_id.bdm_sec_sample_line.unlink()
            sample_id.bdm_sec_pip_sample_line.unlink()
            sample_id.comp_line.unlink()
            sample_id.write({'bdm_sec_sample_line':bdm_sec_sample_line,'comp_line':comp_line,'target':target,'bdm_sec_pip_sample_line':pipline_data})

        if type == 'bdm_net':
            self.update_opp_kpi_consideration(sample_id.bdm_net_sample_line)
            self.update_opp_kpi_consideration(sample_id.bdm_net_sample_line_extra)
            self.update_opp_kpi_consideration(sample_id.bdm_net_pip_sample_line)
            bdm_net_sample_line,comp_line,target,res_extra = self.get_bdm_net_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
#             pipline_data = self.get_bdm_net_pip_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            
            sample_id.bdm_net_sample_line.unlink()
            sample_id.bdm_net_sample_line_extra.unlink()
            sample_id.bdm_net_pip_sample_line.unlink()
            sample_id.comp_line.unlink()
            sample_id.write({'bdm_net_sample_line':bdm_net_sample_line,'bdm_net_sample_line_extra':res_extra,'comp_line':comp_line,'target':target})
        
        
        
        if type == 'bdm_dc':
            bdm_dc_sample_line,comp_line,target = self.get_bdm_dc_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            pipline_data = self.get_bdm_dc_pip_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            sample_id.bdm_dc_sample_line.unlink()
            sample_id.bdm_dc_pip_sample_line.unlink()
            sample_id.comp_line.unlink()
            sample_id.write({'bdm_dc_sample_line':bdm_dc_sample_line,'comp_line':comp_line,'target':target,'bdm_dc_pip_sample_line':pipline_data})
        
        if type == 'bdm_ksa':
            bdm_ksa_sample,comp_line,target = self.get_bdm_ksa_data(sample_id,aud_date_start,aud_date_end,audit_temp_id)
            sample_id.bdm_ksa_sample_line.unlink()
            sample_id.comp_line.unlink()
            sample_id.write({
                'bdm_ksa_sample_line':bdm_ksa_sample,
                'comp_line':comp_line,
                'target':target,
                })
        if type == 'pmo':
            pmo_open_project_line,pmo_closed_project_line,comp_line = self.get_pmo_dir_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            sample_id.pmo_open_project_line.unlink()
            sample_id.pmo_closed_project_line.unlink()
#             sample_id.update_closed_project_data(pmo_closed_project_line)
            sample_id.comp_line.unlink()
            sample_id.write({'pmo_open_project_line':pmo_open_project_line,'pmo_closed_project_line':pmo_closed_project_line,'comp_line':comp_line,})
        
        if type == 'hoo':
            utl_sample_line,ttl_fot_line,pmo_open_project_line,pmo_closed_project_line,team_line,ttl_comp_line = self.get_hoo_data(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            sample_id.pmo_open_project_line.unlink()
            sample_id.pmo_closed_project_line.unlink()
#             sample_id.update_closed_project_data(pmo_closed_project_line)
            sample_id.comp_line.unlink()
            sample_id.team_line.unlink()
            sample_id.utl_sample_line.unlink()
            sample_id.ttl_fot_line.unlink()
            sample_id.write({'utl_sample_line':utl_sample_line,'ttl_fot_line':ttl_fot_line,
                         'pmo_open_project_line':pmo_open_project_line,
                         'pmo_closed_project_line':pmo_closed_project_line,
                         'team_line':team_line,
                         'comp_line':ttl_comp_line})
        
        if type == 'po_officer':
            po_sample,comp_line = self.get_po_sample_data(sample_id,aud_date_start,aud_date_end,audit_temp_id)
            
            sample_id.po_sample_line.unlink()
            sample_id.comp_line.unlink()
            sample_id.write({
                'po_sample_line':po_sample,
                'comp_line':comp_line
                })
        
    
    def create_audit_sample(self,aud_date_start,aud_date_end,audit_temp_id):
        type = audit_temp_id.type
        user_id  = self.user_id and self.user_id.id
        result = []
        sample_id = False
        employee_id = self.id
        dt_start = aud_date_start
        
        name = self.name + '-' +aud_date_start +' To -'+aud_date_end
        
        vals = {}
        vals.update({'name':name,'date_start':aud_date_start,'date_end':aud_date_end,
                'aud_temp_id':audit_temp_id.id,'type':type,'employee_id':employee_id})
        
        if type =='post_sales':
            result,comp_data,utilization = self.get_post_sales_vals(sample_id, aud_date_start, aud_date_end)
            vals.update({'post_sale_sample_line':result,'comp_line':comp_data,'utilization':utilization})
            sample_id =self.env['audit.sample'].create(vals)
        
        
        if type =='ttl':
            result,fot_data,comp_data = self.get_ttl_vals(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            vals.update({'utl_sample_line':result,'ttl_fot_line':fot_data,'comp_line':comp_data}) 
            sample_id =self.env['audit.sample'].create(vals)
        
        if type == 'hoo':
            utl_sample_line,ttl_fot_line,pmo_open_project_line,pmo_closed_project_line,team_line,ttl_comp_line = self.get_hoo_data(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            vals.update({'utl_sample_line':utl_sample_line,'ttl_fot_line':ttl_fot_line,
                         'pmo_open_project_line':pmo_open_project_line,'pmo_closed_project_line':pmo_closed_project_line,
                         'team_line':team_line,
                         'comp_line':ttl_comp_line}) 
            sample_id =self.env['audit.sample'].create(vals)
            
        if type == 'pre_sales':
            opp_sample_line,comp_data = self.get_presale_vals(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            vals.update({'opp_sample_line':opp_sample_line,'comp_line':comp_data}) 
            sample_id =self.env['audit.sample'].create(vals)
            
        if type  == 'pre_sales_mgr':
            opp_sample_line,team_line,comp_data = self.get_presale_mgr_vals(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            vals.update({'opp_sample_line':opp_sample_line,'comp_line':comp_data,'team_line':team_line}) 
            sample_id =self.env['audit.sample'].create(vals)
            #create utlization line
        
        if type == 'tc':
            opp_sample_line,team_line,presale_comp_data,utl_data,fot_data,tech_comp_data,comp_line = self.get_tc_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            vals.update({'utl_sample_line':utl_data,'ttl_fot_line':fot_data,
                             'opp_sample_line':opp_sample_line,'comp_line':comp_line,
                             'tc_tech_comp_line':tech_comp_data,
                             'tc_presale_comp_line':presale_comp_data,
                             'team_line':team_line})
            sample_id =self.env['audit.sample'].create(vals)
        if type == 'tum':
            division_id = self.od_division_id and self.od_division_id.id 
            bdm_sample_line,bdm_comp_line,mp_sale_data,tc_comp_line,staff_data,staff_detail_line,comp_data,sale_enab_score,sale_enab_data,mp_sale_detail_data,branch_data = self.get_tum_data(sample_id, aud_date_start, aud_date_end, audit_temp_id,division_id)
            vals.update({'tum_bdm_sample_line':bdm_sample_line,'tum_bdm_comp_line':bdm_comp_line,'tum_mp_sale_line':mp_sale_data,
                         'tum_tc_comp_line':tc_comp_line,'tum_staff_data_line':staff_data,'tum_staff_data_detail_line':staff_detail_line,
                         'comp_line':comp_data,'tum_sale_eanb_score':sale_enab_score,
                          'tum_sale_enab_line':sale_enab_data,
                           'tum_mp_sale_detail_line':mp_sale_detail_data,
                            'tum_bdm_branch_line':branch_data
                         
                         })
            sample_id =self.env['audit.sample'].create(vals)
        if type == 'service_sale_spl':
            today = dt.today()
            day = today.day
            commit_line,commit_total = self.get_sales_spl_commit_data(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            achieved_line,achieved_total = self.get_sales_spl_achieved_data(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            component_data= self.get_sales_spl_component(commit_total,achieved_total)
            vals.update({'commit_gp_line':commit_line,'achieved_gp_line':achieved_line,'comp_line':component_data})
            sample_id =self.env['audit.sample'].create(vals)
            self.write({'commit_total':commit_total})
        
        if type == 'sales_acc_mgr':
            today = dt.today()
            day = today.day
            commit_line,commit_total = self.get_sales_commit_data(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            achieved_line,achieved_total = self.get_sales_achieved_data(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            component_data,target = self.get_sales_acc_mgr_component(commit_total,achieved_total)
            vals.update({'commit_gp_line':commit_line,'achieved_gp_line':achieved_line,'comp_line':component_data,'target':target})
            sample_id =self.env['audit.sample'].create(vals)
            self.write({'commit_total':commit_total})
        
        if type == 'sm':
            achieved_gp_line,team_line,comp_line,cf_data,cf_summary,cert_data,cert_summary,sale_enab_detail,sale_enab_summary = self.get_sm_data(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            vals.update({'achieved_gp_line':achieved_gp_line,'comp_line':comp_line,'team_line':team_line,
                         'sm_cf_line':cf_data,'sm_cf_summary':cf_summary,'sm_cert_detail':cert_data,
                         'sm_cert_summary':cert_summary,'sm_enab_detail':sale_enab_detail,'sm_enab_summary':sale_enab_summary})
            sample_id =self.env['audit.sample'].create(vals)
        
        
        
        if type == 'pm':
            
            day_score_vals,cost_control_vals,invoice_schedule_vals,compliance_vals,pm_sch_line,comp_line = self.get_pm_data(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            vals.update({'dayscore_line':day_score_vals,'cost_control_line':cost_control_vals,'invoice_schedule_line':invoice_schedule_vals,
                         'compliance_line':compliance_vals,'pm_sch_line':pm_sch_line,'comp_line':comp_line})
            sample_id =self.env['audit.sample'].create(vals)
        
        if type == 'sde':
            day_score_vals,hd_line,compliance_vals,comp_line = self.get_sde_data(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            vals.update({'sde_day_score_line':day_score_vals,'hd_line':hd_line,
                         'compliance_line':compliance_vals,'comp_line':comp_line})
            sample_id =self.env['audit.sample'].create(vals)
        
        
        if type == 'sde_ksa':
            day_score_vals,hd_line,compliance_vals,comp_line = self.get_sde_data_ksa(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            vals.update({'sde_day_score_line':day_score_vals,'hd_line':hd_line,
                         'compliance_line':compliance_vals,'comp_line':comp_line})
            sample_id =self.env['audit.sample'].create(vals)
            
        if type == 'sdm':
            team_day_line,team_hd_line,comp_line = self.get_sdm_data(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            vals.update({'team_day_line':team_day_line,'comp_line':comp_line,'team_hd_line':team_hd_line})
            sample_id =self.env['audit.sample'].create(vals)
        
        
        if type == 'pmo':
            pmo_open_project_line,pmo_closed_project_line,comp_line = self.get_pmo_dir_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            vals.update({'pmo_open_project_line':pmo_open_project_line,'pmo_closed_project_line':pmo_closed_project_line,'comp_line':comp_line})
            sample_id =self.env['audit.sample'].create(vals)
            
        if type == 'pdm':
            day_score_vals,cost_control_vals,invoice_schedule_vals,compliance_vals,pm_sch_line,team_line,my_comp_line,comp_line = self.get_pdm_data(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            vals.update({'dayscore_line':day_score_vals,'cost_control_line':cost_control_vals,'invoice_schedule_line':invoice_schedule_vals,
                         'compliance_line':compliance_vals,'pm_sch_line':pm_sch_line,'team_line':team_line,'my_comp_line':my_comp_line,'comp_line':comp_line})
            sample_id =self.env['audit.sample'].create(vals)
            
        if type == 'bdm':
            bmd_costsheet_line,comp_line,target = self.get_bdm_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            vals.update({'bmd_costsheet_line':bmd_costsheet_line,'comp_line':comp_line,'target':target})
            sample_id =self.env['audit.sample'].create(vals)
        
        if type == 'bdm_sec':
            bdm_sec_sample_line,comp_line,target = self.get_bdm_sec_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            pipline_data = self.get_bdm_sec_pip_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            vals.update({'bdm_sec_sample_line':bdm_sec_sample_line,'comp_line':comp_line,'target':target,'bdm_sec_pip_sample_line':pipline_data})
            sample_id =self.env['audit.sample'].create(vals)
        
        if type == 'bdm_net':
            bdm_net_sample_line,comp_line,target,res_extra = self.get_bdm_net_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
#             pipline_data = self.get_bdm_net_pip_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            vals.update({'bdm_net_sample_line':bdm_net_sample_line,'comp_line':comp_line,'target':target})
            sample_id =self.env['audit.sample'].create(vals)
        
        if type == 'bdm_dc':
            bdm_dc_sample_line,comp_line,target = self.get_bdm_dc_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            pipline_data = self.get_bdm_dc_pip_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            vals.update({'bdm_dc_sample_line':bdm_dc_sample_line,'comp_line':comp_line,'target':target,'bdm_dc_pip_sample_line':pipline_data})
            sample_id =self.env['audit.sample'].create(vals)
            
        
        if type == 'bdm_ksa':
            bdm_ksa_sample,comp_line,target = self.get_bdm_ksa_data(sample_id,aud_date_start,aud_date_end,audit_temp_id)
            vals.update({'bdm_ksa_sample_line':bdm_ksa_sample,
                'comp_line':comp_line,'target':target})
            sample_id =self.env['audit.sample'].create(vals)
        if type == 'po_officer':
            po_sample,comp_line = self.get_po_sample_data(sample_id,aud_date_start,aud_date_end,audit_temp_id)
            vals.update({'po_sample_line':po_sample,
                'comp_line':comp_line})
            sample_id =self.env['audit.sample'].create(vals)
            
        
        return sample_id
    
    
    
    
    
    
    def get_certificate_status(self,execution_num=False):
        res={}
        
        ex_num = self.get_execution_number()
        if execution_num:
            ex_num = execution_num
        ex_num = str(ex_num)
        cert='cert'+ ex_num
        cert_st ='cert_status'+ex_num
        if eval('self.'+cert):
            res['required'] = True 
            if eval('self.'+cert_st) == 'achieved':
                res['achieved'] =True
        return res
    
    
    
    def get_sess_enab_status(self,execution_num=False):
        res={}
        ex_num = self.get_execution_number()
        if execution_num:
            ex_num = execution_num
        ex_num = str(ex_num)
        cert='sess'+ ex_num
        cert_st ='sess_status'+ex_num
        if eval('self.'+cert):
            res['required'] = True 
            if eval('self.'+cert_st) == 'achieved':
                res['achieved'] =True
        return res
    
    
    
    def get_second_sess_enab_status(self,execution_num=False):
        res={}
        ex_num = self.get_execution_number()
        if execution_num:
            ex_num = execution_num
        ex_num = str(ex_num)
        cert='second_sess'+ ex_num
        cert_st ='second_sess_status'+ex_num
        if eval('self.'+cert):
            res['required'] = True 
            if eval('self.'+cert_st) == 'achieved':
                res['achieved'] =True
        return res
    
    
    def get_third_sess_enab_status(self,execution_num=False):
        res={}
        ex_num = self.get_execution_number()
        if execution_num:
            ex_num = execution_num
        ex_num = str(ex_num)
        cert='third_sess'+ ex_num
        cert_st ='third_sess_status'+ex_num
        if eval('self.'+cert):
            res['required'] = True 
            if eval('self.'+cert_st) == 'achieved':
                res['achieved'] =True
        return res
    
    def get_mgr_feedback(self,execution_num=False):
        result =0.0
        ex_num = self.get_execution_number()
        if execution_num:
            ex_num = execution_num
        ex_num = str(ex_num)
        feedback='mgr_feedback'+ ex_num
        score ='mgr_score'+ex_num
        if eval('self.'+feedback):
            result = eval('self.'+score) 
        return result
            
        
    def get_score(self,avg_score,type,ex_num):
            score =avg_score
            if type =='post_sales':
                cert='cert'+ ex_num
                if eval('self.'+cert):
                    score = avg_score * .80
                    cert_st ='cert_status'+ex_num
                    if eval('self.'+cert_st) == 'achieved':
                        score +=20
            if score >100:
                score = 100.0         
            return score
    
    @api.one
    def trial_kpi(self):
        
        audit_temp_id = self.audit_temp_id
        aud_date_start = False
        aud_date_end = False
        active = self.active
        if audit_temp_id and active:
            type = audit_temp_id.type 
            ex_num = self.get_execution_number()
            ex_num = str(ex_num)
            aud_date_start = eval('self'+'.'+'aud_date_start'+str(ex_num))
            aud_date_end  = eval('self'+'.'+'aud_date_end'+str(ex_num))
            aud_samp = 'audit_sample'+str(ex_num)
            aud_samp_check = eval('self.'+aud_samp)
            scr = 'score'+ex_num
            utl ='utl'+ex_num
            if aud_samp_check:
                sample_id  = eval('self.'+aud_samp)
                self.update_audit_sample(sample_id,aud_date_start,aud_date_end,audit_temp_id)
#                 score =  self.get_score(sample_id.avg_score, type, ex_num)
                score = sample_id.avg_score
                utilization = sample_id.utilization
                self.write({scr:score,utl:utilization})
            else:
                if aud_date_start and aud_date_end:
                    sample_id =self.create_audit_sample(aud_date_start,aud_date_end,audit_temp_id)
                    if sample_id:
    #                     score =  self.get_score(sample_id.avg_score, type, ex_num)
                        score = sample_id.avg_score
                        utilization = sample_id.utilization
                        self.write({aud_samp:sample_id.id,scr:score,utl:utilization})
     
#     
#     def audit_set_date(self):
#         year='2018'
#         day_one =01
#         day_end =26
#         month_start1 =1
#         month_start2 =1
#         for i in range(1,13):
#             date_start =year+'-'+str(month_start1)+'-'  + str(day_one)
#             date_stop = year+'-'+str(month_start2)+'-'  + str(day_end)
#             day_one =27
#             month_start2+=1
#             month_start1= month_start2-1
#             sdate ='aud_date_start'+str(i)
#             edate ='aud_date_end'+str(i)
#             self.write({sdate:date_start,edate:date_stop})
    
    def audit_set_date(self):
        
        today = dt.today()
        year = str(today.year)
        month_list =[('2026-01-01','2026-01-31'),('2026-02-01','2026-02-28'),('2026-03-01','2026-03-31'),('2026-04-01','2026-04-30'),('2026-05-01','2026-05-31'),
                     ('2026-06-01','2026-06-30'), ('2026-07-01','2026-07-31'),('2026-08-01','2026-08-31'),('2026-09-01','2026-09-30'),('2026-10-01','2026-10-31'),
                     ('2026-11-01','2026-11-30'), ('2025-12-01','2025-12-31')
                     ]
        for i in range(1,13):
           
            sdate ='aud_date_start'+str(i)
            edate ='aud_date_end'+str(i)
            date_tup = month_list[i-1]
            date_start = date_tup[0]
            date_stop = date_tup[1]
            self.write({sdate:date_start,edate:date_stop})
    def audit_set_execution(self,number=False):
        today = dt.today()
        month_number = today.month
        day = today.day 
#         if day >26:
#             month_number +=1
        if number:
            month_number = number
        ext ='execute'+str(month_number)
        self.write({ext:True})
        for i in range(1,13):
            if i != month_number:
                ext = 'execute'+str(i)
                self.write({ext:False})
        
        
        
        
        
