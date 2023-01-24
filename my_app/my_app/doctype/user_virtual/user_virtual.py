# Copyright (c) 2023, Admin and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from my_app.virtual_doctype import VirtualDoctype


class UserVirtual(VirtualDoctype):
	parent_doctype = "User"
	field_type = "Pos Saller"
	field_by = "module_profile"
	remove_field =  "User Virtual"