# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils.data import flt


def execute(filters=None):
	columns = get_columns()
	data = get_datas(filters)
	chart = get_chart_data(data,filters)
	report_summary = get_report_summary(data,filters)
	# print("\n\n\n\n\n\n\n\n\n\n\n", report_summary)
	return columns, data, None, chart, report_summary
def get_columns():
	data = [
		{"label": _("ID"),"fieldname": "name","fieldtype": "Data","width": 200,},
		{"label": _("Customer Name"),"fieldname": "customer_name","fieldtype": "Link","options": "Customer","width": 120,},
		{
			"label": _("Posting Date"),
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 120,
		},
				{
			"label": _("Pos Profile"),
			"fieldname": "pos_profile",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label": _("Company"),
			"fieldname": "company",
			"fieldtype": "Link",
			"options": "Company",
			"width": 120,
		},
		{
			"label": _("Item Name"),
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 120,
		},
		{"label": _("Quantity"), "fieldname": "qty", "fieldtype": "Data", "width": 90,},
		{"label": _("Rate"), "fieldname": "rate", "fieldtype": "Data", "width": 100,},
		{"label": _("Amount"), "fieldname": "base_amount", "fieldtype": "Data", "width": 100,},
		{
			"label": _("Grand Total"),
			"fieldname": "grand_total",
			"fieldtype": "Data",
			"width": 100,
		},
	]	
	return data
def get_datas(filters):
	conditions = get_conditions(filters)
	data = []
	data_item = frappe.db.sql(f"""SELECT name,customer_name, posting_date,pos_profile ,company, grand_total FROM `tabSales Invoice` WHERE {conditions}""".format(
			conditions=conditions
        ),as_dict=1)
	for d in data_item:
		row = {
			"name":d.name,
			"customer_name":d.customer_name,
			"company":d.company,
			"pos_profile":d.pos_profile,
			"posting_date":d.posting_date,
			"grand_total":f"$ {d.grand_total}"
		}
		data.append(row)
		child = get_items(d.name)
		for i in child:
			r = {
				"indent":1,
				"item_name":i.item_name,
				"qty":i.qty,
				"rate":i.rate,
				"base_amount":i.base_amount
			}
			data.append(r)
	total_row =  total_amount(filters)
	for t in total_row:
		total_row = {
			"name":"<p style='color:green; font-weight:bold;' >Total Amount</p>",
			"grand_total":f"$ {t.total}"
		}
		data.append(total_row)
	
	return data
def get_items(id):
	items = frappe.db.sql(f"""SELECT item_name, qty, base_amount, rate FROM `tabSales Invoice Item` WHERE parent = '{id}';""",as_dict=1)
	return items

def get_conditions(filters):
	conditions = "1=1"
	if filters.get("company"):
		conditions += f" and company= '{filters.get('company')}'"
	# if (filters.get('posting_date')):
	# 	conditions += f" and posting_date = '{filters.get('posting_date')}'"
	if (filters.get('customer_name')):
		conditions += f" and customer_name = '{filters.get('customer_name')}'"
	if (filters.get("year")):
		years = int(filters.get("year"))
		conditions += f" and YEAR(posting_date) = {years}" 
		if (filters.get("month")):
			months = convert_month(filters.get("month"))
			conditions += f" and MONTH(posting_date) = {months}" 
	return conditions	
	#for function is for convert month
def convert_month(filters):
	month = {
		'January':1,
		'February':2,
		'March':3,
		'April':4,
		'May':5,
		'June':6,
		'July':7,
		'August':8,
		'September':9, 
		'October':10,
		'November':11,
		'December':12
        }
	return month.get(filters)

#this function is for get total 
def total_amount(filters):
	conditions = get_conditions(filters)
	# company =  filters.get("company")
	return frappe.db.sql(f"""
	SELECT SUM(total) as total FROM `tabSales Invoice`
	WHERE {conditions}""".format(
			conditions=conditions
        ),as_dict=1)
def count_name(filters):
	conditions = get_conditions(filters)
	# company =  filters.get("company")
	return frappe.db.sql(f"""
	SELECT COUNT(name) as name FROM `tabSales Invoice`
	WHERE {conditions}""".format(
			conditions=conditions
        ),as_dict=1)
# next task is create chart for count invoice and count total

def get_chart_data(data, filters):
	if not data:
		return None
	conditions = get_conditions(filters)
	get_label = frappe.db.sql(f"""SELECT name, posting_date,total FROM `tabSales Invoice` WHERE {conditions}""".format(
			conditions=conditions
        ),as_dict=1)
		
	label = []
	for c in get_label:
		b = {
			"name": c.name
		}
		label.append(b)
	names = [f['name'] for f in label] # this one for convert list of dictionalry to list 


	total = []
	for g in get_label:
		j = {
			"total" : g.total
		}
		total.append(j)
	values = [f['total'] for f in total]
	chart = {
		'data':{
			'labels':names,
			'datasets':[
				{'name':'Number','values':values},
			]
		},
		'type':'bar',
		'colors':['#F16A61'],
	}
	return chart
def get_report_summary(data,filters):
	if not data:
		return None
	g_total = total_amount(filters)
	total_amounts = [f['total'] for f in g_total]
	c_name = count_name(filters)
	total_name = [f['name'] for f in c_name]
	return [
		{
			'value':total_name,
			'indicator': 'Blue',
			'label': 'Total Invoice',
			'datatype': 'float',
		},
		{
			'value':total_amounts,
			'indicator': 'Green',
			'label': 'Total Amount',
			'datatype': 'float',
		}
	]