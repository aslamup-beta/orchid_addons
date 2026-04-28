openerp.orchid_beta_project = function (instance) {
    instance.web.list.columns.add('field.my_widget', 'instance.orchid_beta_project.my_widget');
    instance.orchid_beta_project.my_widget = instance.web.list.Column.extend({
        _format: function (row_data, options) {
            res = this._super.apply(this, arguments);
            var amount = parseFloat(res).toFixed(2);
            if (amount > 0.0){
                return "<font color='#800080'>"+(amount)+"</font>";
            }
            return parseFloat(res).toFixed(2)
        }
    });
    
  
    instance.web.list.columns.add('field.green_widget', 'instance.orchid_beta_project.green_widget');
    instance.orchid_beta_project.green_widget = instance.web.list.Column.extend({
        _format: function (row_data, options) {
            res = this._super.apply(this, arguments);
            var amount = parseFloat(res);
            if (amount > 0.0){
                return "<font color='#008000'>"+(amount)+"</font>";
            }
            return parseFloat(res).toFixed(2)
        }
    });
    
    
    
};