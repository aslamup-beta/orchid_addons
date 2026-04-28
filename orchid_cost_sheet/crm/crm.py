from openerp.osv import fields,osv 
from datetime import datetime


class od_buisiness_type(osv.osv):
    _name = 'od.buisiness.type'
    _columns = {
                'name':fields.char('Business Type'),
                }

class od_opp_sector(osv.osv):
    _name = 'od.opp.sector'
    _columns = {
                'name':fields.char('Sector Name')
                }
class od_inquiry_type(osv.osv):
    _name = 'od.inquiry.type'
    _columns = {
                'name':fields.char('Inquiry Type')
                }
class od_installation_type(osv.osv):
    _name = 'od.installation.type'
    _columns = {
                'name':fields.char('Installation Type'),
                }
class od_networking(osv.osv):
    _name = "od.networking"
    _columns = {
                'name':fields.char('Networking')
                }
class od_security(osv.osv):
    _name = "od.security"
    _columns = {
                'name':fields.char("Security"),
                }
class od_systems(osv.osv):
    _name = "od.systems"
    _columns = {
                'name':fields.char('Systems')
                }
class od_collaporation(osv.osv):
    _name = "od.collaporation"
    _columns = {
                'name':fields.char('Systems')
                }
class od_my_involvement(osv.osv):
    _name = "od.my.involvement"
    _columns = {
                'name':fields.char('My Involvement')
                }
    
class od_period(osv.osv):
    _name = "od.period"
    _columns = {
                'name':fields.char('Period'),
                }
class od_price(osv.osv):
    _name = "od.price"
    _columns = {
                'name':fields.integer('Price')
                }
class od_poc(osv.osv):
    _name = "od.poc"
    _columns = {
                'name':fields.integer('POC')
                }

class od_tech_capability(osv.osv):
    _name = "od.tech.capability"
    _columns = {
                'name':fields.integer('Tech Capability'),
                }
class od_exist_customer(osv.osv):
    _name = 'od.exist.customer'
    _columns = {
                'name':fields.char('Name')
                }
class od_protected_vendor(osv.osv):
    _name = 'od.protected.vendor'
    _columns = {
                'name':fields.char('Name')
                }
    
class od_partner_class(osv.osv):
    _name = 'od.partner.class'
    _columns = {
                'name':fields.char('Class Name'),
                }

class od_group_line(osv.osv):
    _name ='od.group.line'
    _columns = {
                'crm_id':fields.many2one('crm.lead'),
                'group_id':fields.many2one('od.product.group','Group'),
                'sub_group_id':fields.many2many('od.product.sub.group','group_sub_pdt_rel','group_line','sub_group','Sub Group'),
                }
class od_status(osv.osv):
    _name = 'od.status'
    _columns = {
                'name':fields.char('Name')
                }
class crm_lead(osv.osv):
    _inherit = 'crm.lead'
    def create(self, cr, uid, vals, context=None):
        vals.update({'od_creator':uid})
        return super(crm_lead, self).create(cr, uid, vals, context=context)
    def od_open_attachement(self,cr,uid,ids,context=None):
        res = {}
        model_name=self._name
        object_id = ids[0]
        domain = [('model_name','=',model_name),('object_id','=',object_id)]
        ctx = {'default_model_name':model_name,'default_object_id':object_id}
        return {
            'domain': domain,
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'od.attachement',
            'type': 'ir.actions.act_window',
            'context':ctx
        }
    def _od_attachement_count(self, cr, uid, ids, field_name, arg, context=None):
        res ={}
        for obj in self.browse(cr, uid, ids, context):
            attachement_ids = self.pool.get('od.attachement').search(cr, uid, [('model_name', '=', self._name),('object_id','=',ids[0])])
            if attachement_ids:
                res[obj.id] = len(attachement_ids)
        return res
    def onchange_poc_req_date(self,cr,uid,ids,date,context=None):
        res = {}
        if date:
            res['value'] = {'planned_poc_start_date':date}
        return res
    _columns = {
                
               'od_territory_id':fields.related('partner_id', 'od_territory_id', type='many2one', relation='od.partner.territory', string='Sale Territory', readonly=True,store=True),
                'od_attachement_count':fields.function(_od_attachement_count,type="integer",string="Total"),
               'od_contact_person':fields.many2one('res.partner','Contact Person'),
               'poc_initiation_date':fields.date('Initiation Date'),
               'od_customer_name':fields.char('Customer Name'),
               'poc_name':fields.char('POC Name'),
               'poc_bi_objective':fields.char('POC Business Objective'),
               'planned_poc_start_date':fields.date('Planned POC Start Date'),
               'planned_poc_finish_date':fields.date('Planned POC Finish Date'),
               'actual_poc_start_date':fields.date('Actual POC Start Date'),
               'actual_poc_finished_date':fields.date('Actual POC Finished Date'),
               'pre_requisite_status':fields.selection([('pending_customer','Pending Customer'),
                                                        ('pending_beta_it','Pending Beta IT'),
                                                        ('pending_vendor','Pending Vendor'),
                                                        ('completed','Completed')
                                                        ],'Pre-Requisite Status'),
                'poc_status':fields.selection([('not_started','Not Started'),
                                               ('on_hold','On Hold'),
                                               ('in_progress','In Progress'),
                                               ('cancelled','Cancelled'),
                                               ('finished','Finished')
                                               ],'POC Status'),
                'od_buisiness_type_id':fields.many2one('od.partner.industry','Industry'),
                'od_buisiness_type_ids':fields.many2many('od.buisiness.type','buisiness_type_crm_rel','crm_id','buisiness_id','Type Of Buisiness'),
                'od_opp_sector_id':fields.many2one('od.opp.sector','Sector'),
                'od_inquiry_type_id':fields.many2one('od.inquiry.type','Type Of Inquiry'),
                'od_submission_date':fields.date('Submission Date'),
#                 'od_protected_by_vendor':fields.selection([('yes','Yes'),('no','No'),('partially','Partially')],'Protected By Vendor?'),
#                 'od_existing_customer':fields.selection([('new','New Customer'),('exist_loyal','Existing Loyal Customer'),
#                                                          ('exist_unsatisfied','Existing Un-Satisfied Customer'),
#                                                          ('exist_neutral','Existing Neutral Customer')],'Existing Customer?'),
                
                'od_protected_by_vendor':fields.many2one('od.protected.vendor','Protected By Vendor?'),
                'od_existing_customer':fields.many2one('od.exist.customer','Existing Customer?'),
                'od_customer_need':fields.char('Customer Need Reason'),
                'od_installation_type_id':fields.many2one('od.installation.type','Installation Type'),
               'is_deal_budgeted':fields.selection([('yes','Yes'),('no','No'),('no_idea','No Idea')],'Is Deal Budgeted'),
               'managers_engagement':fields.char('Management Engagement'),
               'is_bid_bond_required':fields.selection([('yes','Yes'),('no','No'),('no_idea','No Idea')],'Bid Bond Required?'),
                'od_group_line':fields.one2many('od.group.line','crm_id','Groups'),
                'od_group_id':fields.many2one('od.product.group','Group'),
                'od_sub_group_id':fields.many2one('od.product.sub.group','Sub Group'),
               'od_our_products':fields.many2many('od.product.brand','crm_product_brand_rel','crm_id','brand_id','Our Products'),
               'od_competing_products':fields.many2many('od.product.brand','crm_comp_product_brand_rel','crm_id','brand_id','Competing Products'),
               'od_our_competer':fields.many2many('res.partner','partner_od_crm','crm_id','partner_id','Our Competitors',domain=[('is_company','=',True)]),
               'od_my_involvement':fields.many2one('od.my.involvement','My Involvement'),
               'od_beta_imp_service':fields.boolean('Beta Implementation?'),
               'od_outsourced':fields.boolean('Outsourced Imp.Service?'),
               'od_auditing_service':fields.boolean('Auditing Service'),
               'od_amc':fields.boolean('Amc'),
               'od_period_id':fields.char('AMC Period'),
               'od_operation':fields.boolean('OM/ Resident Engineers'),
               'od_operation_period':fields.char('Operation Period'),
               'od_no_of_engineer':fields.integer('No Of Engineer'),
               'project_implemented_loc':fields.char('Project Location'),
               'od_price_id':fields.many2one('od.price','Price'),
               'od_poc_id':fields.many2one('od.poc','POC'),
               'od_tech_capability_id':fields.many2one('od.tech.capability','Tech Capability'),
               'management_presentation':fields.boolean('Management Presentation?'),
               'man_pre_date':fields.date('Management Presentation Date'),
               'technical_presentation':fields.boolean('Technical Presentation?'),
               'tech_pre_date':fields.date('Technical Presentation Date'),
               'proof_of_concept':fields.boolean('Proof Of Concept?'),
               'proof_date':fields.date('Proof of Concept Date'),
               'help_customer_rfp':fields.boolean('Help Customer in Writing Specifications RFP?'),
               'rfp_date':fields.date('Customer RFP Date'),
               'tech_proposal':fields.boolean('Detailed Technical Proposal'),
               'hld_proposal':fields.boolean('Detailed HLD Proposal'),
               'financial_proposal':fields.boolean('Financial Proposal'),
               'site_survey':fields.boolean('Site Survey'),
               'req_tech_workshop':fields.boolean('Requirements Technical Workshop'),
               'proposal_date':fields.date('Proposal Date'),
               'od_req_on_7':fields.date('Financial Proposal Required Date', track_visibility='onchange'),
               'od_req_on_8':fields.date('Site Survey Required Date'),
               'od_req_on_9':fields.date('Technical workshop Required Date'),
               'hld_date':fields.date('HLD Date'),
               'comments':fields.text('Comments'),
               'od_status_id_1':fields.many2one('od.status','Management Presentation Status'),
               'od_status_id_2':fields.many2one('od.status','Technical Presentation Status'),
               'od_status_id_3':fields.many2one('od.status','Proof Of Concept Status'),
               'od_status_id_4':fields.many2one('od.status','Help customer Status'),
               'od_status_id_5':fields.many2one('od.status','Detailed Technical Status'),
               'od_status_id_6':fields.many2one('od.status','Hld Proposal Status'),
               'od_status_id_7':fields.many2one('od.status','Financial Proposal Status'),
               'od_status_id_8':fields.many2one('od.status','Site Survey Status'),
               'od_status_id_9':fields.many2one('od.status','Technical workshop Status'),
               'finished_on_1':fields.date('Management Presentation Finished On'),
               'finished_on_2':fields.date('Technical Presentation Finished On'),
               'finished_on_3':fields.date('Proof Of Concept Finished On'),
               'finished_on_4':fields.date('Help customer Finished On'),
               'finished_on_5':fields.date('Detailed Technical Finished On'),
               'finished_on_6':fields.date('Hld Proposal Finished On'),
               'finished_on_7':fields.date('Financial Proposal Finished On'),
               'finished_on_8':fields.date('Site Survey Finished On'),
               'finished_on_9':fields.date('Technical workshop Finished On'),
               'od_creator':fields.many2one('res.users','Creator',readonly=True),
               
               'cust_req1':fields.text(string="Customer Requirement"),
               'cust_req2':fields.text(string="Customer Requirement"),
               'comp1':fields.selection([('comply','Comply'),('not_comply','Do Not Comply'),('part_comply','Partially Comply')],string="Compliance"),
               'comp2':fields.selection([('comply','Comply'),('not_comply','Do Not Comply'),('part_comply','Partially Comply')],string="Compliance"),
               'sam_note1':fields.text(string="SAM Note"),
               'sam_note2':fields.text(string="SAM Note"),
               'od_partner_class_rel':fields.many2one('od.partner.class','Partner Class'),
               'budget_proposal':fields.boolean('Budgetary proposal'),
               'od_budg_req_on':fields.date('Budgetary proposal Required Date'),
               'od_budg_status_id':fields.many2one('od.status','Budgetary proposal Status'),
               'od_budg_finished_on':fields.date('Budgetary proposal Finished On')
          }
    _defaults = {
        'financial_proposal':True,
#                   'man_pre_date': fields.date.context_today,
#                   'tech_pre_date': fields.date.context_today,
#                   'proof_date': fields.date.context_today,
#                   'rfp_date': fields.date.context_today,
#                   'proposal_date': fields.date.context_today,
                 
                 }
    
    def on_change_partner_id(self, cr, uid, ids, partner_id, context=None):
        values = super(crm_lead,self).on_change_partner_id(cr, uid, ids, partner_id, context=context)
        if partner_id:
#             sheet_pool= self.pool.get('od.cost.sheet')
#             sheet_ids = sheet_pool.search(cr,uid,[('lead_id','=',ids[0])])
#             print "sheets>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",sheet_ids,partner_id,type(partner_id)
#             for sheet in sheet_pool.browse(cr,uid,sheet_ids):
#                 sheet.write({'od_customer_id':partner_id})
            
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
            values['value'].update( {
                 'user_id':partner.user_id and partner.user_id.id,
                 #'od_lead_user_id':partner.user_id and partner.user_id.id,
                'od_customer_name': partner.parent_id.name if partner.parent_id else partner.name,
                'od_buisiness_type_id':partner.parent_id.od_industry_id.id if partner.parent_id else partner.od_industry_id.id
            })
            
        return values
    def on_change_user(self, cr, uid, ids, user_id, context=None):
        res = super(crm_lead, self).on_change_user( cr, uid, ids, user_id)
        if user_id and ids:
            sheet_pool= self.pool.get('od.cost.sheet')
            sheet_ids = sheet_pool.search(cr,uid,[('lead_id','=',ids[0])])
            for sheet in sheet_pool.browse(cr,uid,sheet_ids):
                sheet.write({'sales_acc_manager':user_id})
        return res
    
    def od_mark_mp_finished(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context):
            obj.write({'finished_on_1': datetime.today()})
        return True
    def od_mark_tp_finished(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context):
            obj.write({'finished_on_2': datetime.today()})
        return True
    def od_mark_hcws_finished(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context):
            obj.write({'finished_on_4': datetime.today()})
        return True
    def od_mark_dtp_finished(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context):
            obj.write({'finished_on_5': datetime.today()})
        return True
    def od_mark_hld_finished(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context):
            obj.write({'finished_on_6': datetime.today()})
        return True
    def od_mark_ss_finished(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context):
            obj.write({'finished_on_8': datetime.today()})
        return True
    def od_mark_rtw_finished(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context):
            obj.write({'finished_on_9': datetime.today()})
        return True
    def od_mark_poc_finished(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context):
            obj.write({'finished_on_3': datetime.today()})
        return True
    
        

     
    