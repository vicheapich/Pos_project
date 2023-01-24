# Copyright (c) 2022, Mr. Vean Viney and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import getseries
from frappe.utils.data import DATE_FORMAT, cint, cstr, getdate
import datetime
from frappe.utils import flt
from frappe import _, msgprint


class VirtualDoctype(Document):
    """
        Usage:
            - You must set value to variable parent_doctype.
        Example:
            1. Python File:
                from platform_frappe.model.virtual_doctype import VirtualDoctype

                class CustomerRelative(VirtualDoctype):
                    parent_doctype = "CBP Customer"

            2. Javascript File:
                frappe.ui.form.on('Customer Relative', {
                    after_save: function (frm) {
                        frm.reload_doc();
                        frm.refresh()
                    }
                });
    """

    parent_doctype = ""
    field_type = ""
    field_by = ""
    remove_field = ""


    def __init__(self, *args, **kwargs):

        
        self._table_fieldnames = self.get_table_fieldnames()
        self.args = args
        self.kwargs = kwargs
        super().__init__(*args, **kwargs)

    def get_new_parent_doc(self):
        return frappe.new_doc(self.parent_doctype)

    def get_table_fieldnames(self):
        """
            Don't call to protected member directly.
            Ex: self.get_new_parent_doc()._table_fieldnames
        """
        data = set()

        for d in self.get_new_parent_doc().meta.get_table_fields():
            data.update({d.fieldname})

        return data

    def get_table_field_objects(self):
        """
            Don't call to protected member directly.
            Ex: self.get_new_parent_doc().meta._table_fields
        """
        data = []

        for d in self.meta.get_table_fields():
            setattr(d, "parent", self.parent_doctype)
            data.append(d)

        return data

    def get_virtual_table_fieldnames(self):
        """
            Don't call to protected member directly.
            Ex: self.get_new_parent_doc().meta._table_fields
        """
        data = set()

        for d in self.meta.get_table_fields():
            data.update({d.fieldname})

        return data

    def get_table_field_dict(self):
        data = {}

        for field in self.get_table_field_objects():
            data.update({field.fieldname: {"doctype": field.options, "parent": field.parent, "label": field.label}})

        return data

    def exec_virtual_method(self, fn_name, *args, **kwargs):
        pre_doct = self.doctype
        self.doctype = self.parent_doctype
        getattr(super(), fn_name)(*args, **kwargs)
        self.doctype = pre_doct

    def prepare_data_from_db(self):
        data = frappe.db.get_value(self.parent_doctype, self.name, ["name"], as_dict=1)

        if not data:
            # When reload new form operation, it must ignore another query or another calling function.
            setattr(self, "__islocal", True)
            return None

        data = frappe.get_doc(self.parent_doctype, self.name).as_dict()
        table_fieldnames = self.get_table_fieldnames()
        form_table_fieldnames = self.get_virtual_table_fieldnames()
        diff_table_fieldnames = table_fieldnames - form_table_fieldnames

        for field_name in diff_table_fieldnames:
            if hasattr(data, field_name):
                del data[field_name]

        self.update(data)

    def prepare_data_for_db_insert(self, *args, **kwargs):
        data = self.get_valid_dict(convert_dates_to_str=True)
        parent_doctype = self.get_new_parent_doc()

        for field, value in data.items():
            if hasattr(parent_doctype, field):
                setattr(parent_doctype, field, value)

        for children_field in self.get_virtual_table_fieldnames():
            children_data = getattr(self, children_field)

            for data_item in children_data:
                setattr(data_item, "parenttype", self.parent_doctype)

                parent_doctype.append(children_field, data_item.as_dict())

        parent_doctype.insert(ignore_permissions=True)

        setattr(self, "name", parent_doctype.name)
        
    def prepare_data_for_update(self, *args, **kwargs):
        data = self.get_valid_dict(convert_dates_to_str=True)
        parent_doctype = self.get_new_parent_doc()
        children_field_dict = self.get_table_field_dict()

        for field, value in data.items():
            if hasattr(parent_doctype, field):
                setattr(parent_doctype, field, value)

        for children_field in self.get_virtual_table_fieldnames():
            children_data = getattr(self, children_field)
            keep_ids = []

            for data_item in children_data:
                setattr(data_item, "parenttype", self.parent_doctype)
                keep_ids.append(data_item.name)

            child_doctype = children_field_dict.get(children_field, {}).get("doctype")
            children = frappe.get_list(child_doctype,
                                       fields=["name"],
                                       filters={"parent": self.name,
                                                "parentfield": children_field,
                                                "parenttype": self.parent_doctype,
                                                "name": ("NOT IN", keep_ids)})

            for del_item in children:
                frappe.delete_doc(child_doctype, del_item.get("name"))

        self.exec_virtual_method("db_update")

    def db_insert(self, *args, **kwargs):
        """
            Don't use self.reload() here, the children will not save.
        """
        self.prepare_data_for_db_insert()

    def load_from_db(self):
        """
            Don't use self.reload() here, the children will not save.
        """
        self.prepare_data_from_db()

    def db_update(self, *args, **kwargs):
        """
            Don't use self.reload() here, the children will not save.
        """
        self.prepare_data_for_update()

    def delete(self, ignore_permissions=False):
        self.doctype = self.parent_doctype
        super().delete(ignore_permissions)

    @classmethod
    def filters_list(cls, *args, **kwargs):
        if cls.field_by == "":
            return ""
        else:
            return {f'{cls.field_by}': cls.field_type}

    @classmethod
    def get_list(cls, args):
        if len(args.filters) == 0:
            data = frappe.db.get_list(cls.parent_doctype, fields="*", filters=cls.filters_list(), order_by='creation desc')
        else:
            for i in args.filters:
                i.remove(cls.remove_field)
            args.filters.append([cls.field_by, "=", cls.field_type])
            data = frappe.db.get_list(cls.parent_doctype, fields="*", filters=args.filters, order_by='creation desc')
        
        return data

    @classmethod
    def get_count(cls, args):
        pass

    @classmethod
    def get_stats(cls, args):
        pass

    #Make Difference Entry in Journal Entry ---- (Accounting Entries Table)
    @frappe.whitelist()
    def get_balance(self):
        if not self.get("accounts"):
            msgprint(_("'Entries' cannot be empty"), raise_exception=True)
        else:
            self.total_debit, self.total_credit = 0, 0
            diff = flt(self.difference, self.precision("difference"))

            # If any row without amount, set the diff on that row
            if diff:
                blank_row = None
                for d in self.get("accounts"):
                    if not d.credit_in_account_currency and not d.debit_in_account_currency and diff != 0:
                        blank_row = d

                if not blank_row:
                    blank_row = self.append("accounts", {})

                blank_row.exchange_rate = 1
                if diff > 0:
                    blank_row.credit_in_account_currency = diff
                    blank_row.credit = diff
                elif diff < 0:
                    blank_row.debit_in_account_currency = abs(diff)
                    blank_row.debit = abs(diff)

            self.validate_total_debit_and_credit()

    def validate_total_debit_and_credit(self):
        self.set_total_debit_credit()
        if self.difference:
            frappe.throw(
                _("Total Debit must be equal to Total Credit. The difference is {0}").format(self.difference)
            )

    def set_total_debit_credit(self):
        self.total_debit, self.total_credit, self.difference = 0, 0, 0
        for d in self.get("accounts"):
            if d.debit and d.credit:
                frappe.throw(_("You cannot credit and debit same account at the same time"))

            self.total_debit = flt(self.total_debit) + flt(d.debit, d.precision("debit"))
            self.total_credit = flt(self.total_credit) + flt(d.credit, d.precision("credit"))

        self.difference = flt(self.total_debit, self.precision("total_debit")) - flt(
            self.total_credit, self.precision("total_credit")
        )
