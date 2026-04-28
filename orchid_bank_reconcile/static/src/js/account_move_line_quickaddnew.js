//openerp.orchid_bank_reconcile = function (instance) {
function orchid_quick_move(instance){
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    var round_pr = instance.web.round_precision

    instance.web.orchid_bank_reconcile = openerp.account.quickadd || {};

    instance.web.views.add('tree_orchid_bank_reconcile_move_line_quickadd', 'instance.web.orchid_bank_reconcile.QuickAddListView');

    instance.web.orchid_bank_reconcile.QuickAddListView = instance.web.ListView.extend({
        init: function() {
            this._super.apply(this, arguments);
            this.journals = [];
            this.periods = [];
            
            this.current_journal = null;
            this.current_period = null;

            this.default_period = null;
            this.default_journal = null;
            
            this.od_accounts = [];
            this.od_current_account = null;
            this.od_default_account = null;            

            this.current_journal_type = null;
            this.current_journal_currency = null;
            this.current_journal_analytic = null;

            this.od_book_balance = 0.0;
            this.od_bank_balance = 0.0;

            this.od_fc_book_balance = 0.0;        
            this.od_fc_bank_balance = 0.0;

        },
        start:function(){
            var tmp = this._super.apply(this, arguments);
            var self = this;
            var defs = [];
            this.$el.parent().prepend(QWeb.render("OdAccountMoveLineQuickAdd", {widget: this}));


    

            this.$el.parent().find('.od_reco_button').click(function() {
                    console.log("#################");
                  self.do_search(self.last_domain, self.last_context, self.last_group_by);
                });

            this.$el.parent().find('.oe_orchid_bank_reconcile_select_journal').change(function() {
                    self.current_journal = this.value === '' ? null : parseInt(this.value);
                    self.do_search(self.last_domain, self.last_context, self.last_group_by);
                });
            this.$el.parent().find('.oe_orchid_bank_reconcile_select_period').change(function() {
                    self.current_period = this.value === '' ? null : parseInt(this.value);
                    self.do_search(self.last_domain, self.last_context, self.last_group_by);
                });

            this.$el.parent().find('.oe_orchid_bank_reconcile_select_account').change(function() {
                    self.od_current_account = this.value === '' ? null : parseInt(this.value);
                    self.do_search(self.last_domain, self.last_context, self.last_group_by);
                });

            this.on('edit:after', this, function () {
                self.$el.parent().find('.oe_orchid_bank_reconcile_select_journal').attr('disabled', 'disabled');
                self.$el.parent().find('.oe_orchid_bank_reconcile_select_period').attr('disabled', 'disabled');
                self.$el.parent().find('.oe_orchid_bank_reconcile_select_account').attr('disabled', 'disabled');
            });
            this.on('save:after cancel:after', this, function () {
                self.$el.parent().find('.oe_orchid_bank_reconcile_select_journal').removeAttr('disabled');
                self.$el.parent().find('.oe_orchid_bank_reconcile_select_period').removeAttr('disabled');
                self.$el.parent().find('.oe_orchid_bank_reconcile_select_account').removeAttr('disabled');
            });
            var mod = new instance.web.Model("account.move.line", self.dataset.context, self.dataset.domain);
            defs.push(mod.call("default_get", [['journal_id','period_id','account_id'],self.dataset.context]).then(function(result) {
               // self.current_period = result['period_id'];
                self.current_journal = result['journal_id'];
                self.od_current_account = result['account_id'];
                
            }));
            defs.push(mod.call("od_list_journals", []).then(function(result) {
                self.journals = result;
            }));
            defs.push(mod.call("od_list_periods", []).then(function(result) {
                self.periods = result;
            }));
            defs.push(mod.call("od_list_accounts", []).then(function(result) {
                self.od_accounts = result;
            }));

            defs.push(mod.call("od_book_bank_balance", []).then(function(result) {
                self.od_book_balance = result.book_balance;
                self.od_bank_balance = result.bank_balance;
                self.od_fc_book_balance = result.od_fc_book_balance;
                self.od_fc_bank_balance = result.od_fc_bank_balance;

            }));



            return $.when(tmp, defs);
        },
        do_search: function(domain, context, group_by) {
            var self = this;
            this.last_domain = domain;
            this.last_context = context;
            this.last_group_by = group_by;
            this.old_search = _.bind(this._super, this);
            var o;

            vals={
                'period_id':self.current_period,
                'account_id':self.od_current_account,
                'journal_id': self.current_journal,
            }
            var get_bank_book = new instance.web.Model("account.move.line").get_func("od_book_bank_balance");
            get_bank_book(vals).then(function(result) {

                self.od_book_balance = result.book_balance;
                self.od_bank_balance = result.bank_balance;
            
                self.od_fc_book_balance = result.fc_book_balance;
                self.od_fc_bank_balance = result.fc_bank_balance;

                book_dr_cr = result.book_balance > 0 ? "Dr" : "Cr"
                bank_dr_cr = result.bank_balance > 0 ? "Dr" : "Cr"
//                self.$el.parent().find('.od_book_balance h4').text(_.str.sprintf("%s: %s %s","Book Balance",round_pr(result.book_balance),book_dr_cr)); 
//                self.$el.parent().find('.od_bank_balance h4').text(_.str.sprintf("%s: %s %s","Bank Balance",round_pr(result.bank_balance),bank_dr_cr)); 

//                self.$el.parent().find('.od_fc_book_balance h4').text(_.str.sprintf("(%s: %s)","FC",round_pr(result.fc_book_balance))); 
//                self.$el.parent().find('.od_fc_bank_balance h4').text(_.str.sprintf("(%s: %s)","FC",round_pr(result.fc_bank_balance))); 


                self.$el.parent().find('.od_book_balance h4').text(_.str.sprintf("%s: %s %s","Book Balance",result.book_balance.toFixed(2),book_dr_cr)); 
                self.$el.parent().find('.od_bank_balance h4').text(_.str.sprintf("%s: %s %s","Bank Balance",result.bank_balance.toFixed(2),bank_dr_cr)); 

                self.$el.parent().find('.od_fc_book_balance h4').text(_.str.sprintf("(%s: %s)","FC",result.fc_book_balance.toFixed(2))); 
                self.$el.parent().find('.od_fc_bank_balance h4').text(_.str.sprintf("(%s: %s)","FC",result.fc_bank_balance.toFixed(2))); 

            });

            self.$el.parent().find('.oe_orchid_bank_reconcile_select_journal').children().remove().end();
            self.$el.parent().find('.oe_orchid_bank_reconcile_select_journal').append(new Option('', ''));
            for (var i = 0;i < self.journals.length;i++){
                o = new Option(self.journals[i][1], self.journals[i][0]);
                if (self.journals[i][0] === self.current_journal){
                    self.current_journal_type = self.journals[i][2];
                    self.current_journal_currency = self.journals[i][3];
                    self.current_journal_analytic = self.journals[i][4];
                    $(o).attr('selected',true);
                }
                self.$el.parent().find('.oe_orchid_bank_reconcile_select_journal').append(o);
            }
            self.$el.parent().find('.oe_orchid_bank_reconcile_select_period').children().remove().end();
            self.$el.parent().find('.oe_orchid_bank_reconcile_select_period').append(new Option('', ''));
            for (var i = 0;i < self.periods.length;i++){
                o = new Option(self.periods[i][1], self.periods[i][0]);
                self.$el.parent().find('.oe_orchid_bank_reconcile_select_period').append(o);
            }    
            self.$el.parent().find('.oe_orchid_bank_reconcile_select_period').val(self.current_period).attr('selected',true);


            self.$el.parent().find('.oe_orchid_bank_reconcile_select_account').children().remove().end();
            self.$el.parent().find('.oe_orchid_bank_reconcile_select_account').append(new Option('', ''));

            for (var i = 0;i < self.od_accounts.length;i++){
//                console.log("#@@@##",self.od_accounts[i]);

//                        str=self.od_accounts[i][0]
//                        od_acc_option = str.length > 12 ? str.substring(12,-1)+'...' : str; 

//console.log("@@",od_acc_option);
//                o = new Option(self.od_accounts[i][1], od_acc_option);
                o = new Option(self.od_accounts[i][1], self.od_accounts[i][0]);
                self.$el.parent().find('.oe_orchid_bank_reconcile_select_account').append(o);
            } 
            self.$el.parent().find('.oe_orchid_bank_reconcile_select_account').val(self.od_current_account).attr('selected',true);
            book_dr_cr = self.od_book_balance > 0 ? "Dr" : "Cr"
            bank_dr_cr = self.od_bank_balance > 0 ? "Dr" : "Cr"
            self.$el.parent().find('.od_book_balance h4').text(_.str.sprintf("%s: %s %s","Book Balance",Math.abs(self.od_book_balance),book_dr_cr)); 
            self.$el.parent().find('.od_bank_balance h4').text(_.str.sprintf("%s: %s %s","Bank Balance",Math.abs(self.od_bank_balance),bank_dr_cr)); 

            return self.search_by_journal_period();
        },
        search_by_journal_period: function() {
            var self = this;
            var domain = [];
            if (self.current_journal !== null) domain.push(["journal_id", "=", self.current_journal]);
            if (self.current_period !== null) domain.push(["period_id", "=", self.current_period]);
            if (self.od_current_account !== null) domain.push(["account_id", "=", self.od_current_account]);
            self.last_context["journal_id"] = self.current_journal === null ? false : self.current_journal;
            if (self.current_period === null) delete self.last_context["period_id"];
            else self.last_context["period_id"] =  self.current_period;
            self.last_context["journal_type"] = self.current_journal_type;
            self.last_context["account_id"] = self.od_current_account;
            self.last_context["currency"] = self.current_journal_currency;
            self.last_context["analytic_journal_id"] = self.current_journal_analytic;
            var compound_domain = new instance.web.CompoundDomain(self.last_domain, domain);
            self.dataset.domain = compound_domain.eval();
            return self.old_search(compound_domain, self.last_context, self.last_group_by);
        },
    });
}
