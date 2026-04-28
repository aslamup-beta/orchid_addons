openerp.document_viewer_code = function(instance, local) {

    var core = instance.web;
    var Sidebar = core.Sidebar;
    var Widget = core.Widget;
    var _t = core._t;

    Sidebar.include({
        start : function(){
            var self = this;
            self._super.apply(self, arguments);
            self.$el.on('click','.o_sidebar_viewer_code_item', function(evt) {
                evt.preventDefault();
                evt.stopPropagation();
                var $target = $(evt.currentTarget);
                var id = parseInt($target.attr('data-id'), 10);
                self.do_action({
                    name: _t('Attachment Viewer'),
                    type: 'ir.actions.client',
                    tag: "document.viewer.code",
                    params: {
                        id: id
                    },
                    target: 'new'
                });
            });
        }
    });

    core.DocumentViewerCode = Widget.extend({
        template: "ViewerCode",
        init: function(parent, action, options) {
            var self = this;
            var url = "/web/binary/saveas?model=ir.attachment&field=datas&filename_field=name&id=" + action.params.id;
            self.url = url;
            self._super.apply(self, arguments);
        },
        start: function() {
            var self = this;
            $.get(self.url, function(code){
                hljs.highlightBlock(self.$el.find("code").text(code).get(0));
            }, "text");
            return self._super();
        },
        renderElement: function() {
            var self = this;
            self._super();
            self.getParent().$buttons.hide();
        }
    });

    core.client_actions.add('document.viewer.code', 'instance.web.DocumentViewerCode');

};