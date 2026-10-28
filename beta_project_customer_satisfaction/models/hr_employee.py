from openerp import models, fields, api, _
from openerp.exceptions import Warning
import re
from datetime import date as dt
from datetime import timedelta, datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class hr_employee(models.Model):
    _inherit = "hr.employee"

    def get_pm_component(self, day_weight_scr, cc_weight_scr, inv_weight_scr, comp_weight_scr, sc_weight_scr,feedback_weight_scr, day_flag,
                         cost_flag, inv_flag, comp_flag, sc_flag, feedback_flag):
        comp_data = []
        if self.company_id.id == 1:

            day_wt = .1
            cc_wt = .2
            inv_wt = .3
            comp_wt = .1
            sc_wt = .3
            exclude_wt = 0.0
            if not day_flag:
                exclude_wt += day_wt
                day_wt = 0.0
            if not cost_flag:
                exclude_wt += cc_wt
                cc_wt = 0.0
            if not inv_flag:
                exclude_wt += inv_wt
                inv_wt = 0.0
            if not comp_flag:
                exclude_wt += comp_wt
                comp_wt = 0.0
            if not sc_flag:
                exclude_wt += sc_wt
                sc_wt = 0.0
            if exclude_wt == 1.0:
                return comp_data
            if exclude_wt:
                day_wt = day_wt + (day_wt * exclude_wt) / float(1.0 - exclude_wt)
                cc_wt = cc_wt + (cc_wt * exclude_wt) / float(1.0 - exclude_wt)
                inv_wt = inv_wt + (inv_wt * exclude_wt) / float(1.0 - exclude_wt)
                comp_wt = comp_wt + (comp_wt * exclude_wt) / float(1.0 - exclude_wt)
                sc_wt = sc_wt + (sc_wt * exclude_wt) / float(1.0 - exclude_wt)
            if day_wt:
                score = (day_weight_scr / 10.0) * 100.0
                final_score = day_wt * score
                comp_data.append((0, 0,
                                  {'name': '5 Day Processing Score', 'weight': day_wt * 100.0, 'final_score': final_score,
                                   'score': score}))

            if cc_wt:
                score = (cc_weight_scr / 20.0) * 100.0
                final_score = cc_wt * score
                comp_data.append(
                    (0, 0, {'name': 'Cost Control', 'weight': cc_wt * 100.0, 'final_score': final_score, 'score': score}))

            if inv_wt:
                score = (inv_weight_scr / 30.0) * 100.0
                final_score = inv_wt * score
                comp_data.append((0, 0, {'name': 'Invoice Schedule', 'weight': inv_wt * 100, 'final_score': final_score,
                                         'score': score}))

            if comp_wt:
                score = (comp_weight_scr / 10.0) * 100.0
                final_score = comp_wt * score
                comp_data.append((0, 0, {'name': 'Compliance Provided By PMO', 'weight': comp_wt * 100.0,
                                         'final_score': final_score, 'score': score}))

            if sc_wt:
                score = (sc_weight_scr / 30.0) * 100.0
                final_score = sc_wt * score
                comp_data.append((0, 0, {'name': 'Schedule Control', 'weight': sc_wt * 100.0, 'final_score': final_score,
                                         'score': score}))

            mgr_score = self.get_mgr_feedback()
            if mgr_score:
                comp_data.append((0, 0,
                                  {'name': 'Direct Manager Feedback',
                                   'weight': -20,
                                   'score': mgr_score,
                                   'final_score': mgr_score}
                                  ))

        if self.company_id.id == 6:
            # (5, 0, 0) clears existing component lines so they are never duplicated
            comp_data = [(5, 0, 0)]
            # (name, achieved score, max score, weight, flag)
            components = [
                ('5 Day Processing', day_weight_scr, 10.0, 0.1, day_flag),
                ('Schedule Control', sc_weight_scr, 25.0, 0.25, sc_flag),
                ('Invoice Schedule', inv_weight_scr, 25.0, 0.25, inv_flag),
                ('Customer Satisfaction', feedback_weight_scr, 10.0, 0.1, feedback_flag),
                ('Cost Control', cc_weight_scr, 20.0, 0.2, cost_flag),
                ('PMO Compliance', comp_weight_scr, 10.0, 0.1, comp_flag),


            ]

            for name, raw_score, max_score, weight, flag in components:
                # Component not applicable (flag False) -> give max score
                if not flag:
                    raw_score = max_score

                score = (raw_score / max_score) * 100.0
                comp_data.append((0, 0, {
                    'name': name,
                    'weight': weight * 100.0,
                    'final_score': weight * score,
                    'score': score,
                }))

            mgr_score = self.get_mgr_feedback()
            if mgr_score:
                comp_data.append((0, 0, {
                    'name': 'Direct Manager Feedback',
                    'weight': -20,
                    'score': mgr_score,
                    'final_score': mgr_score,
                }))

        return comp_data

    def get_pm_data(self, sample_id, user_id, aud_date_start, aud_date_end, audit_temp_id):

        analytic_pool = self.env['account.analytic.account']
        analytic_ids = analytic_pool.search(
            [('od_owner_id', '=', user_id), ('od_type_of_project', 'in', ('sup', 'imp', 'sup_imp', 'cust_trn')),
             ('state', 'not in', ('close', 'cancelled'))])
        project_closed_on_audit_old_type = analytic_pool.search(
            [('od_owner_id', '=', user_id), ('od_type_of_project', 'in', ('sup', 'imp', 'sup_imp', 'cust_trn')),
             ('state', '=', 'close'), ('od_analytic_level', '=', 'level_old'), ('od_project_end', '>=', aud_date_start),
             ('od_project_end', '<=', aud_date_end)])
        project_closed_on_audit = analytic_pool.search(
            [('od_owner_id', '=', user_id), ('od_type_of_project', 'in', ('sup', 'imp', 'sup_imp', 'cust_trn')),
             ('state', '=', 'close'), ('od_analytic_level', '!=', 'level_old'),
             ('od_date_end_original', '>=', aud_date_start), ('od_date_end_original', '<=', aud_date_end)])
        project_closed = analytic_pool.search(
            [('od_owner_id', '=', user_id), ('od_type_of_project', 'in', ('sup', 'imp', 'sup_imp', 'cust_trn')),
             ('state', '=', 'close'), ('od_analytic_level', '!=', 'level_old'),
             ('od_closing_date', '>=', aud_date_start), ('od_closing_date', '<=', aud_date_end)])

        sample_project_ids = analytic_ids + project_closed_on_audit + project_closed_on_audit_old_type

        diff_project = project_closed - project_closed_on_audit

        day_score_vals = []
        #         total_sale_value = sum([a.od_project_sale for a in sample_project_ids])
        #         max_day_sore =aud_date_endaud_date_endaud_date_end 20 * len(sample_project_ids)

        cost_control_vals = []
        #         total_gp_value = sum([a.od_amended_profit for a in sample_project_ids])
        #         max_cc_sore = 30 * len(sample_project_ids)

        invoice_schedule_vals = []
        compliance_vals = []
        schedule_control_vals = []
        schedule_control_vals_main = []
        feedback_vals = []
        day_weight = []
        cc_weight = []
        inv_weight = []
        comp_weight = []
        feedback_weight = []
        sc_weight = []
        tot_sale_day = 0.0
        tot_gp = 0.0
        sch_gp = 0.0
        tot_sal_inv = 0.0
        tot_sal_comp = 0.0
        tot_sal_feedback = 0.0
        day_score_main = []
        cost_control_val_main = []
        invoice_schedule_main = []
        compliance_vals_main = []
        feedback_vals_main = []
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
                    cost_control_vals.append(
                        {'analytic_id': proj.id, 'gp_value': gp_value, 'score': cost_control_score, 'form_wt': 20.0,
                         'actual_gp': actual_gp, 'original_gp': original_gp})
                    #Added by Aslam to update Cust feedback score for KSA
                    cust_feedback_score = proj.cust_feedback_score
                    if self.company_id.id == 6:
                        feedback_vals.append(
                            {'analytic_id': proj.id, 'gp_value': gp_value, 'score': cust_feedback_score, 'form_wt': 10.0,
                             'actual_gp': actual_gp, 'original_gp': original_gp})



        for proj in sample_project_ids:
            processed_date = proj.od_cost_sheet_id and proj.od_cost_sheet_id.processed_date and proj.od_cost_sheet_id.processed_date[:10]
            if processed_date and aud_date_start <= processed_date <= aud_date_end:
                sale_val = proj.od_amended_sale_price or 1.0
                tot_sale_day += sale_val
                dayscore = proj.day_process_score
                day_score_vals.append({'analytic_id': proj.id, 'sale_value': sale_val, 'score': dayscore,
                                       'cost_sheet_id': proj.od_cost_sheet_id.id, 'form_wt': 10.0})
            # cost control score
            #             if proj.state == 'close':
            #                 closed_date = proj.od_closing_date
            #                 if closed_date and aud_date_start <= closed_date <= aud_date_end:
            #                     gp_value = proj.od_amended_profit
            #                     actual_gp = proj.od_actual_profit
            #                     original_gp = proj.od_original_sale_profit
            #                     tot_gp += gp_value
            #                     cost_control_score = proj.cost_control_score
            #                     cost_control_vals.append({'analytic_id':proj.id,'gp_value':gp_value,'score':cost_control_score,'form_wt':20.0,'actual_gp':actual_gp,'original_gp':original_gp})
            # invoice Schedule Score
            #             inv_sch_dates = [a.date for a in proj.od_project_invoice_schedule_line]
            #             check = self.check_inv_sch_dates(inv_sch_dates,aud_date_start,aud_date_end)
            #             check2,inv_score,plan_amount = self.get_inv_sch_score(proj,aud_date_start,aud_date_end)
            #             if check2:
            #                 invoice_sc_score = inv_score
            #                 tot_sal_inv  += plan_amount
            #                 invoice_schedule_vals.append({'analytic_id':proj.id,'sale_value':plan_amount,'score':invoice_sc_score,'form_wt':30.0})

            # Added by Aslam to include A0 INV1 Analytic Accounts
            if proj.fin_approved_date and proj.fin_approved_date[:10] > '2020-09-01':
                form_weight_inv_sch = 30.0
                if self.company_id.id == 6:
                    form_weight_inv_sch = 25.0
                today = str(dt.today())
                parent_analytic = proj.parent_id or False
                if parent_analytic and parent_analytic.id not in a0_ids:
                    for inv_sch in parent_analytic.prj_inv_sch_line:
                        if inv_sch.name == 'INV1' and inv_sch.date > '01-Nov-20' and not inv_sch.invoice_id:
                            if today >= inv_sch.date:
                                a0_ids.append(proj.parent_id.id)
                                score = 0.0
                                plan_amount = inv_sch.amount
                                tot_sal_inv += plan_amount
                                invoice_schedule_vals.append(
                                    {'analytic_id': proj.parent_id.id, 'sale_value': plan_amount, 'score': score,
                                     'form_wt': form_weight_inv_sch})

            for inv_line in proj.od_project_invoice_schedule_line:
                today = str(dt.today())
                planned_date = inv_line.date
                if today >= planned_date:
                    invoice = inv_line.invoice_id
                    invoice_state = invoice.state
                    form_weight_inv_sch = 30.0
                    if self.company_id.id == 6:
                        form_weight_inv_sch = 25.0

                    if invoice and invoice_state in ('open', 'paid', 'accept'):
                        cust_date = invoice.cust_date
                        if cust_date:
                            if aud_date_start <= cust_date <= aud_date_end:
                                if cust_date <= planned_date:
                                    inv_sch_score = 30.0
                                    if self.company_id.id == 6:
                                        inv_sch_score = 25.0
                                    plan_amount = inv_line.amount
                                    tot_sal_inv += plan_amount
                                    invoice_schedule_vals.append(
                                        {'analytic_id': proj.id, 'sale_value': plan_amount, 'score': inv_sch_score,
                                         'form_wt': form_weight_inv_sch})
                                else:
                                    score = 0.0
                                    plan_amount = inv_line.amount
                                    tot_sal_inv += plan_amount
                                    invoice_schedule_vals.append(
                                        {'analytic_id': proj.id, 'sale_value': plan_amount, 'score': score,
                                         'form_wt': form_weight_inv_sch})
                        else:
                            score = 0.0
                            plan_amount = inv_line.amount
                            tot_sal_inv += plan_amount
                            invoice_schedule_vals.append(
                                {'analytic_id': proj.id, 'sale_value': plan_amount, 'score': score, 'form_wt': form_weight_inv_sch})

                    else:
                        score = 0.0
                        plan_amount = inv_line.amount
                        tot_sal_inv += plan_amount
                        invoice_schedule_vals.append(
                            {'analytic_id': proj.id, 'sale_value': plan_amount, 'score': score, 'form_wt': form_weight_inv_sch})

            if proj.start_project_comp and self.company_id.id == 1:
                compliance_score = proj.compliance_score
                # sale_val = proj.od_project_sale
                sale_val = proj.od_amended_sale_price or 1.0
                tot_sal_comp += sale_val
                compliance_vals.append(
                    {'analytic_id': proj.id, 'sale_value': sale_val, 'score': compliance_score, 'form_wt': 10.0})

            #Finalise with elayyan when to include
            if self.company_id.id == 6 and proj.state in ('sign_off', 'close'):
                compliance_score = proj.compliance_score
                # sale_val = proj.od_project_sale
                sale_val = proj.od_amended_sale_price or 1.0
                tot_sal_feedback += sale_val
                compliance_vals.append(
                    {'analytic_id': proj.id, 'sale_value': sale_val, 'score': compliance_score, 'form_wt': 10.0})



            # schedule control score
            current_day = str(dt.today())
            #             project_planned_end = proj.od_project_end or proj.date
            project_planned_end = proj.od_date_end_original
            closed_date = proj.od_closing_date
            if current_day >= project_planned_end:
                if proj.state == 'close':
                    if aud_date_start <= closed_date <= aud_date_end:
                        sc_scr = 30.0
                        sc_scr_weight = 30.0
                        if self.company_id.id == 6:
                            sc_scr = 25.0
                            sc_scr_weight = 25.0
                        gp_value = proj.od_amended_profit
                        sch_gp += gp_value
                        schedule_control_vals.append(
                            {'analytic_id': proj.id, 'gp_value': gp_value, 'score': sc_scr, 'form_wt': sc_scr_weight})

                else:
                    sc_scr = 0.0
                    sc_scr_weight = 30.0
                    if self.company_id.id == 6:
                        sc_scr_weight = 25.0
                    gp_value = proj.od_amended_profit
                    sch_gp += gp_value
                    schedule_control_vals.append(
                        {'analytic_id': proj.id, 'gp_value': gp_value, 'score': sc_scr, 'form_wt': sc_scr_weight})

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
            sal_val_percent = 0.0
            sale_value = data.get('sale_value')

            if tot_sale_day:
                sal_val_percent = sale_value / float(tot_sale_day)
            dayscore = data.get('score')
            weight_day = max_day_sore * sal_val_percent * (dayscore / 10.0)
            data['sale_value_percent'] = sal_val_percent * 100.0
            data['weight'] = weight_day
            day_weight.append(weight_day)
            day_score_main.append((0, 0, data))
        max_cc_sore = 20 * len(cost_control_vals)
        for data in cost_control_vals:
            gp_val_percent = 0.0
            gp_value = data.get('gp_value')
            if tot_gp:
                gp_val_percent = gp_value / float(tot_gp)
            score = data.get('score')
            weight_cc = max_cc_sore * gp_val_percent * (score / 20.0)
            data['weight'] = weight_cc
            data['gp_value_percent'] = gp_val_percent * 100.0
            cc_weight.append(weight_cc)
            cost_control_val_main.append((0, 0, data))

        max_sc_score_weight = 30
        if self.company_id.id == 6:
            max_sc_score_weight = 25.0
        max_sc_sore = max_sc_score_weight * len(schedule_control_vals)
        for data in schedule_control_vals:
            gp_val_percent = 0.0
            gp_value = data.get('gp_value')
            if sch_gp:
                gp_val_percent = gp_value / float(sch_gp)
            score = data.get('score')
            weight_sc = max_sc_sore * gp_val_percent * (score / max_sc_score_weight)
            data['weight'] = weight_sc
            data['gp_value_percent'] = gp_val_percent * 100.0
            sc_weight.append(weight_sc)
            schedule_control_vals_main.append((0, 0, data))

        max_inv_score_weight = 30
        if self.company_id.id == 6:
            max_inv_score_weight = 25.0
        max_inv_scr = max_inv_score_weight * len(invoice_schedule_vals)
        for data in invoice_schedule_vals:
            sal_val_percent = 0.0
            sale_value = data.get('sale_value')
            if tot_sal_inv:
                sal_val_percent = sale_value / float(tot_sal_inv)
            score = data.get('score')
            weight_inv = max_inv_scr * sal_val_percent * (score / max_inv_score_weight)
            data['sale_value_percent'] = sal_val_percent * 100.0
            data['weight'] = weight_inv
            inv_weight.append(weight_inv)
            invoice_schedule_main.append((0, 0, data))

        max_comp_scr = 10 * len(compliance_vals)
        for data in compliance_vals:
            sal_val_percent = 0.0
            sale_value = data.get('sale_value')
            if tot_sal_comp:
                sal_val_percent = sale_value / float(tot_sal_comp)
            score = data.get('score')
            weight_comp = max_comp_scr * sal_val_percent * (score / 10.0)
            data['sale_value_percent'] = sal_val_percent * 100.0
            data['weight'] = weight_comp
            comp_weight.append(weight_comp)
            compliance_vals_main.append((0, 0, data))

        if self.company_id.id == 6:
            max_feedback_score = 10 * len(feedback_vals)
            for data in feedback_vals:
                sal_val_percent = 0.0
                sale_value = data.get('sale_value')
                if tot_sal_feedback:
                    sal_val_percent = sale_value / float(tot_sal_feedback)
                score = data.get('score')
                weight_comp = max_feedback_score * sal_val_percent * (score / 10.0)
                data['sale_value_percent'] = sal_val_percent * 100.0
                data['weight'] = weight_comp
                feedback_weight.append(weight_comp)
                feedback_vals_main.append((0, 0, data))


        day_weight_scr = self.get_avg_score(day_weight)
        cc_weight_scr = self.get_avg_score(cc_weight)
        inv_weight_scr = self.get_avg_score(inv_weight)
        comp_weight_scr = self.get_avg_score(comp_weight)
        sc_weight_scr = self.get_avg_score(sc_weight)
        feedback_weight_scr = self.get_avg_score(feedback_weight)
        day_flag = cost_flag = inv_flag = comp_flag = sc_flag = feedback_flag = False
        if day_score_main:
            day_flag = True
        if cost_control_val_main:
            cost_flag = True
        if invoice_schedule_main:
            inv_flag = True
        if compliance_vals_main:
            comp_flag = True
        if schedule_control_vals_main:
            sc_flag = True
        if feedback_vals_main:
            feedback_flag = True
        comp_line = self.get_pm_component(day_weight_scr, cc_weight_scr, inv_weight_scr, comp_weight_scr, sc_weight_scr,feedback_weight_scr,
                                          day_flag, cost_flag, inv_flag, comp_flag, sc_flag, feedback_flag)

        return day_score_main, cost_control_val_main, invoice_schedule_main, compliance_vals_main, schedule_control_vals_main, feedback_vals_main, comp_line

    def create_audit_sample(self, aud_date_start, aud_date_end, audit_temp_id):
        if audit_temp_id.type != 'pm':
            # every other type runs the original code untouched
            return super(hr_employee, self).create_audit_sample(aud_date_start, aud_date_end, audit_temp_id)

        # ---- pm: rebuilt from the original method ----
        user_id = self.user_id and self.user_id.id
        sample_id = False
        name = self.name + '-' + aud_date_start + ' To -' + aud_date_end

        vals = {
            'name': name,
            'date_start': aud_date_start,
            'date_end': aud_date_end,
            'aud_temp_id': audit_temp_id.id,
            'type': audit_temp_id.type,
            'employee_id': self.id,
        }

        day_score_vals, cost_control_vals, invoice_schedule_vals,compliance_vals, pm_sch_line, cust_feedback_line,comp_line = self.get_pm_data(sample_id, user_id, aud_date_start, aud_date_end, audit_temp_id)

        vals.update({
            'dayscore_line': day_score_vals,
            'cost_control_line': cost_control_vals,
            'invoice_schedule_line': invoice_schedule_vals,
            'compliance_line': compliance_vals,
            'pm_sch_line': pm_sch_line,
            'comp_line': comp_line,
            'cust_feedback_line': cust_feedback_line,
        })
        return self.env['audit.sample'].create(vals)

    def update_audit_sample(self, sample_id, aud_date_start, aud_date_end, audit_temp_id):
        if audit_temp_id.type != 'pm':
            # all other types run the original code untouched
            return super(hr_employee, self).update_audit_sample(
                sample_id, aud_date_start, aud_date_end, audit_temp_id)

        # ---- pm: rebuilt from the original method ----
        user_id = self.user_id and self.user_id.id

        (day_score_vals, cost_control_vals, invoice_schedule_vals,
         compliance_vals, pm_sch_line, cust_feedback_line,
         comp_line) = self.get_pm_data(sample_id, user_id, aud_date_start,
                                       aud_date_end, audit_temp_id)

        sample_id.dayscore_line.unlink()
        sample_id.cost_control_line.unlink()
        sample_id.invoice_schedule_line.unlink()
        sample_id.compliance_line.unlink()
        sample_id.pm_sch_line.unlink()
        sample_id.comp_line.unlink()
        sample_id.cust_feedback_line.unlink()

        sample_id.write({
            'dayscore_line': day_score_vals,
            'cost_control_line': cost_control_vals,
            'invoice_schedule_line': invoice_schedule_vals,
            'pm_sch_line': pm_sch_line,
            'compliance_line': compliance_vals,
            'cust_feedback_line': cust_feedback_line,
            'comp_line': comp_line,
        })


    def get_pdm_data(self,sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id):
        employee_id = self.id
        team_ids = self.search([('parent_id','=',employee_id)])
        user_ids = [emp.user_id.id for emp in team_ids if (emp.audit_temp_id and emp.audit_temp_id.type=='pm') ]
        result = []
        team_vals =[]
        score_board =[]

        day_score_vals = cost_control_vals = invoice_schedule_vals = compliance_vals = schedule_control_vals = my_comp_data = []
        for uid in user_ids:
            day_score_main,cost_control_val_main,invoice_schedule_main,compliance_vals_main,schedule_control_vals_main,cust_feedback_line_main,team_comp_data = self.get_pm_data(sample_id,uid, aud_date_start, aud_date_end, audit_temp_id)
            if uid == user_id:
                day_score_vals, cost_control_vals,invoice_schedule_vals,compliance_vals, schedule_control_vals,my_comp_data = day_score_main,cost_control_val_main,invoice_schedule_main,compliance_vals_main,schedule_control_vals_main,team_comp_data

            #score = self.get_score_from_comp_data(team_comp_data)
            score = self.get_score_from_comp_data([c for c in team_comp_data if c[0] == 0])
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
