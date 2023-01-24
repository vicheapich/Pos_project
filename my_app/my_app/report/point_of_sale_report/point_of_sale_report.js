// Copyright (c) 2023, Admin and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Point of Sale Report"] = {
	"filters": [
		{
            "fieldname": 'customer_name',
            "label": __('Customer Name'),
            "fieldtype": 'Link',
            "options": "Customer",
        },
		{
            "fieldname": 'company',
            "label": __('Company'),
            "fieldtype": 'Link',
            "default": frappe.defaults.get_user_default("company"),
            "options": 'Company',
        },
        // {
        //     "fieldname": 'posting_date',
        //     "label": __("Posting Date"),
		// 	"fieldtype": 'Date'
        // },
        {
            "fieldname": 'year',
            "label": __("Year"),
			"fieldtype": 'Select',
            "default": '',
            "options": [
               '', '2017','2018', '2019', '2020','2021','2022', '2023', '2024', '2025', '2026', '2027', '2028','2029','2030'
            ],
        },
        {
            "fieldname": 'month',
            "label": __("Month"),
			"fieldtype": 'Select',
            "depends_on":'eval:doc.year != null',
            "options": [
                'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
                'September', 'October', 'November', 'December'
            ],
        },
	]
};
