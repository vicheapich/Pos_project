// Copyright (c) 2023, Admin and contributors
// For license information, please see license.txt

frappe.ui.form.on('User Virtual', {
	after_save: function (frm) {
		frm.reload_doc();
		frm.refresh();
	},
});
