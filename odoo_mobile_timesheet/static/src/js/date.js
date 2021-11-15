odoo.define('odoo_mobile_timesheet', function (require) {
'use strict';
require('web.dom_ready');
var website = require('website.website');
$("div.input-group i.fa-calendar").on('click', function(e) {
        $(e.currentTarget).closest("div.date").datetimepicker({
            icons : {
                time: 'fa fa-clock-o',
                date: 'fa fa-calendar',
                up: 'fa fa-chevron-up',
                down: 'fa fa-chevron-down'
            },
        });
    });
});
