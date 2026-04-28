openerp.orchid_remove_quick_create = function (instance) {

    var QWeb = instance.web.qweb,
        _t  = instance.web._t,
        _lt = instance.web._lt;

        instance.web.form.AbstractField.include({
                init: function(field_manager, node) {
                    var self = this;
                    this._super(field_manager, node);
                    this.options.no_create_edit = this.session.allow_quick_create ? false:true;
                    this.options.no_quick_create = this.session.allow_quick_create ? false:true;
                    //this.options.no_open = this.session.allow_quick_create ? false:true;

                },

        });
};

