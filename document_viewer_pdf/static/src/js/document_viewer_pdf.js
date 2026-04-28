openerp.document_viewer_pdf = function(instance, local) {

    var core = instance.web;
    var Sidebar = core.Sidebar;
    var Widget = core.Widget;
    var _t = core._t;

    Sidebar.include({
        start : function(){
            var self = this;
            self._super.apply(self, arguments);
            self.$el.on('click','.o_sidebar_viewer_pdf_item', function(evt) {
                evt.preventDefault();
                evt.stopPropagation();
                var $target = $(evt.currentTarget);
                var id = parseInt($target.attr('data-id'), 10);
                self.do_action({
                    name: _t('Attachment Viewer'),
                    type: 'ir.actions.client',
                    tag: "document.viewer.pdf",
                    params: {
                        id: id
                    },
                    target: 'new'
                });
            });
        }
    });

    core.DocumentViewerPdf = Widget.extend({
        template: "ViewerPdf",
        init: function(parent, action, options) {
            var self = this;
            var url = "/document_viewer_pdf/static/lib/pdfjs/web/viewer.html";
            url += "?" + $.param({"file": "/web/binary/saveas?model=ir.attachment&field=datas&filename_field=name&id=" + action.params.id});
            url += "#page=1&zoom=page-width";
            self.url = url;
            self._super.apply(self, arguments);
        },
        start: function() {
            var self = this;
            self.$iframe = self.$el.find("iframe");
            self.waitForPDF();
            return self._super();
        },
        waitForPDF: function() {
            var self = this;
            var $contents = $();
            try{
                $contents = self.$iframe.contents();
            }catch(e){}
            if($contents.find('#errorMessage').is(":visible")) {
                return;
            }
            if($contents.find('.page').length > 0 && $contents.find('.textLayer').length > 0) {
                self.doPDFPostLoad();
            } else {
                setTimeout(function() { self.waitForPDF(); }, 50);
            }
        },
        renderElement: function() {
            var self = this;
            self._super();
            self.getParent().$buttons.hide();
        },
        doPDFPostLoad: function() {
            var self = this;
            var $contents = self.$iframe.contents();
            $contents.find('#openFile, #viewBookmark, #documentProperties').hide();
            $contents.find('#documentProperties').prev().hide();
        }
    });

    core.client_actions.add('document.viewer.pdf', 'instance.web.DocumentViewerPdf');

};