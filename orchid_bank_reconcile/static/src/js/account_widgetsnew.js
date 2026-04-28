//openerp.orchid_bank_reconcile = function (instance) {
function orchid_quick_widget(instance){
    var QWeb = instance.web.qweb;
	var _t = instance.web._t;
    instance.web.account.ReconciliationListView.include({
            load_list: function(){
                var self = this;
                var tmp = this._super.apply(this, arguments);
                if (this.partners) {
                     od_partners=self.partners;
                     for(var i = 0, len = od_partners.length; i < len; i++){
                        var content = self.$('.partner_search-select').html();
                        str=od_partners[i][1]
                        option = str.length > 33 ? str.substring(33,-1)+'...' : str;                       
                        var new_option = '<option value="' + i + '">' + option +'</option>\n';
                        self.$('.partner_search-select').html(content + new_option);
                     }
                    this.$('.partner_search-select').change(function(){
                        var name = this.value;
                        self.current_partner = Number(name);
                        self.search_by_partner();
                    });

                }

            },

    });

}
