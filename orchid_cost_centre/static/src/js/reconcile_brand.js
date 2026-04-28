openerp.orchid_cost_centre = function(instance){

    var module = instance.account;

    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    instance.web.account.bankStatementReconciliation = instance.web.account.bankStatementReconciliation.extend({
        init: function(parent, context) {
            this._super(parent,context);
            this.create_form_fields = {
                account_id: {
                    id: "account_id",
                    index: 0,
                    corresponding_property: "account_id", // a account.move field name
                    label: _t("Account"),
                    required: true,
                    tabindex: 10,
                    constructor: instance.web.form.FieldMany2One,
                    field_properties: {
                        relation: "account.account",
                        string: _t("Account"),
                        type: "many2one",
                        domain: [['type','not in',['view', 'closed', 'consolidation']]],
                    },
                },
                label: {
                    id: "label",
                    index: 1,
                    corresponding_property: "label",
                    label: _t("Label"),
                    required: true,
                    tabindex: 11,
                    constructor: instance.web.form.FieldChar,
                    field_properties: {
                        string: _t("Label"),
                        type: "char",
                    },
                },
                tax_id: {
                    id: "tax_id",
                    index: 6,
                    corresponding_property: "tax_id",
                    label: _t("Tax"),
                    required: false,
                    tabindex: 16,
                    constructor: instance.web.form.FieldMany2One,
                    field_properties: {
                        relation: "account.tax",
                        string: _t("Tax"),
                        type: "many2one",
                        domain: [['type_tax_use','in',['purchase', 'all']], ['parent_id', '=', false]],
                    },
                },
                amount: {
                    id: "amount",
                    index: 3,
                    corresponding_property: "amount",
                    label: _t("Amount"),
                    required: true,
                    tabindex: 13,
                    constructor: instance.web.form.FieldFloat,
                    field_properties: {
                        string: _t("Amount"),
                        type: "float",
                    },
                },
                analytic_account_id: {
                    id: "analytic_account_id",
                    index: 5,
                    corresponding_property: "analytic_account_id",
                    label: _t("Analytic Acc."),
                    required: false,
                    tabindex: 15,
                    group:"analytic.group_analytic_accounting",
                    constructor: instance.web.form.FieldMany2One,
                    field_properties: {
                        relation: "account.analytic.account",
                        string: _t("Analytic Acc."),
                        type: "many2one",
                        domain: [['type', '!=', 'view'], ['state', 'not in', ['close','cancelled']]],
                    },
                },
                od_product_brand_id: {
                    id: "od_product_brand_id",
                    index: 4,
                    corresponding_property: "od_product_brand_id",
                    label: _t("Brand"),
                    required: false,
                    tabindex: 14,
                    group:"orchid_cost_centre.group_orchid_product_brand",
                    constructor: instance.web.form.FieldMany2One,
                    field_properties: {
                        relation: "od.product.brand",
                        string: _t("Brand"),
                        type: "many2one",
                        domain: [],
                    },
                },
                od_cost_centre_id: {
                    id: "od_cost_centre_id",
                    index: 2,
                    corresponding_property: "od_cost_centre_id",
                    label: _t("Cost Centre"),
                    required: false,
                    tabindex: 12,
                    group:"orchid_cost_centre.group_orchid_cost_centre_centre",
                    constructor: instance.web.form.FieldMany2One,
                    field_properties: {
                        relation: "od.cost.centre",
                        string: _t("Cost Centre"),
                        type: "many2one",
                        domain: [],
                    },
                },

            };


        },

        start: function() {
            this._super();
            var self = this;
            // Retreive statement infos and reconciliation data from the model
            var lines_filter = [['journal_entry_id', '=', false], ['account_id', '=', false]];
            var deferred_promises = [];
            
            // Working on specified statement(s)
            if (self.statement_ids && self.statement_ids.length > 0) {
                lines_filter.push(['statement_id', 'in', self.statement_ids]);

                // If only one statement, display its name as title and allow to modify it
                if (self.single_statement) {
                    deferred_promises.push(self.model_bank_statement
                        .query(["name"])
                        .filter([['id', '=', self.statement_ids[0]]])
                        .first()
                        .then(function(title){
                            self.title = title.name;
                        })
                    );
                }
                // Anyway, find out how many statement lines are reconciled (for the progressbar)
                deferred_promises.push(self.model_bank_statement
                    .call("number_of_lines_reconciled", [self.statement_ids])
                    .then(function(num) {
                        self.already_reconciled_lines = num;
                    })
                );
            }
            
            // Get operation templates
            deferred_promises.push(new instance.web.Model("account.statement.operation.template")
                .query(['id','name','account_id','label','amount_type','amount','tax_id','analytic_account_id','od_product_brand_id','od_cost_centre_id'])
                .all().then(function (data) {
                    _(data).each(function(preset){
                        self.presets[preset.id] = preset;
                    });
                })
            );

            // Get the function to format currencies
            deferred_promises.push(new instance.web.Model("res.currency")
                .call("get_format_currencies_js_function")
                .then(function(data) {
                    self.formatCurrency = new Function("amount, currency_id", data);
                })
            );
    
            // Get statement lines
            deferred_promises.push(self.model_bank_statement_line
                .query(['id'])
                .filter(lines_filter)
                .order_by('statement_id, id')
                .all().then(function (data) {
                    self.st_lines = _(data).map(function(o){ return o.id });
                })
            );
    
            // When queries are done, render template and reconciliation lines
            return $.when.apply($, deferred_promises).then(function(){
    
                // If there is no statement line to reconcile, stop here
                if (self.st_lines.length === 0) {
                    self.$el.prepend(QWeb.render("bank_statement_nothing_to_reconcile"));
                    return;
                }
    
                // Create a dict account id -> account code for display facilities
                new instance.web.Model("account.account")
                    .query(['id', 'code'])
                    .all().then(function(data) {
                        _.each(data, function(o) { self.map_account_id_code[o.id] = o.code });
                    });

                // Create a dict currency id -> rounding factor
                new instance.web.Model("res.currency")
                    .query(['id', 'rounding'])
                    .all().then(function(data) {
                        _.each(data, function(o) { self.map_currency_id_rounding[o.id] = o.rounding });
                    });

                // Create a dict tax id -> amount
                new instance.web.Model("account.tax")
                    .query(['id', 'amount'])
                    .all().then(function(data) {
                        _.each(data, function(o) { self.map_tax_id_amount[o.id] = o.amount });
                    });
            
                new instance.web.Model("ir.model.data")
                    .call("xmlid_to_res_id", ["account.menu_bank_reconcile_bank_statements"])
                    .then(function(data) {
                        self.reconciliation_menu_id = data;
                        self.doReloadMenuReconciliation();
                    });

                // Bind keyboard events TODO : méthode standard ?
                $("body").on("keypress", function (e) {
                    self.keyboardShortcutsHandler(e);
                });
    
                // Render and display
                self.$el.prepend(QWeb.render("bank_statement_reconciliation", {
                    title: self.title,
                    single_statement: self.single_statement,
                    total_lines: self.already_reconciled_lines+self.st_lines.length
                }));
                self.updateProgressbar();
                var reconciliations_to_show = self.st_lines.slice(0, self.num_reconciliations_fetched_in_batch);
                self.last_displayed_reconciliation_index = reconciliations_to_show.length;
                self.$(".reconciliation_lines_container").css("opacity", 0);
    
                // Display the reconciliations
                return self.model_bank_statement_line
                    .call("get_data_for_reconciliations", [reconciliations_to_show])
                    .then(function (data) {
                        var child_promises = [];
                        while ((datum = data.shift()) !== undefined)
                            child_promises.push(self.displayReconciliation(datum.st_line.id, 'inactive', false, true, datum.st_line, datum.reconciliation_proposition));
                        $.when.apply($, child_promises).then(function(){
                            self.$(".reconciliation_lines_container").animate({opacity: 1}, self.aestetic_animation_speed);
                            self.getChildren()[0].set("mode", "match");
                            self.updateShowMoreButton();
                        });
                    });
            });
        },






    });

instance.web.account.bankStatementReconciliationLine = instance.web.account.bankStatementReconciliationLine.extend({

        // idem
        prepareCreatedMoveLineForPersisting: function(line) {
            var dict = {};
            if (dict['account_id'] === undefined)
                dict['account_id'] = line.account_id;
            dict['name'] = line.label;
            var amount = line.tax_id ? line.amount_with_tax: line.amount;
            if (amount > 0) dict['credit'] = amount;
            if (amount < 0) dict['debit'] = -1 * amount;
            if (line.tax_id) dict['account_tax_id'] = line.tax_id;
            if (line.is_tax_line) dict['is_tax_line'] = line.is_tax_line;
            if (line.analytic_account_id) dict['analytic_account_id'] = line.analytic_account_id;
            if (line.od_product_brand_id) dict['od_product_brand_id'] = line.od_product_brand_id;
            if (line.od_cost_centre_id) dict['od_cost_centre_id'] = line.od_cost_centre_id;
            return dict;
        },

});


};
