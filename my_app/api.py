import frappe
import json
import random
import string
from passlib.context import CryptContext
from frappe.utils.data import today

@frappe.whitelist(allow_guest=True)
def register_require(**data):
	user_dict = data['data']
	user_data = json.loads(user_dict)
	for k, v in user_data.items():
		pass
	user_data = json.loads(user_dict)
	first_name 		= user_data.get("first_name")
	last_name 		= user_data.get("last_name")
	company_name 	= user_data.get("company_name")
	business_type 	= user_data.get("business_type")
	business_size 	= user_data.get("business_size")
	password 		= user_data.get("password")
	email 			= user_data.get("email")
	if company_name == None:
		company_name = first_name  + " " + last_name

	create_company(company_name, business_type, business_size )
	create_bank_account(company_name)
	create_new_user(first_name, last_name, email)
	create_user_permission(email, company_name)
	create_posprofile(company_name)
	create_pos_opening_entry(email, company_name)


	passlibctx = CryptContext(
		schemes=[
			"pbkdf2_sha256",
			"argon2",
			"frappe_legacy",
		],
		deprecated=[
			"frappe_legacy",
		],
	)
	passcode = passlibctx.hash(password)
	dataes = {
		"doctype": "User",
		"name": email,
		"fieldname": "password",
		'password': passcode,
		"encrypted": 0
	}

	frappe.db.sql(
		"""INSERT INTO __Auth VALUES (%(doctype)s, %(name)s,%(fieldname)s, %(password)s, %(encrypted)s)""",
		as_dict=True,
		values=dataes
	)
	return {
		"message":"success"
	}

	####create new company
def create_company(companyname , businesstype, businesssize):
	new_company = frappe.new_doc('Company')
	new_company.company_name = companyname
	shortname = "".join(c[0] for c in companyname.split()).upper()
	new_company.abbr                			= shortname.strip()
	new_company.default_currency    			= "USD"
	new_company.country            				= "Cambodia"
	new_company.business_type       			= businesstype
	new_company.business_side       			= businesssize
	new_company.insert(ignore_permissions=True)
	new_company.db_set("default_bank_account",f"ABA - {new_company.abbr}")
	create_company.myname = new_company

	###create new bank account
def create_bank_account(companyname):
	new_bank 									= frappe.new_doc("Account")
	new_bank.account_name 						= "ABA"
	new_bank.company 							= companyname
	new_bank.parent_account 					= f"Bank Accounts - {create_company.myname.abbr}"
	new_bank.account_type						= "Bank"
	new_bank.insert(ignore_permissions=True)

	#####create new user
def create_new_user(firstname, lastname, email):
	new_user = frappe.new_doc('User')
	new_user.first_name             			= firstname
	new_user.last_name              			= lastname
	new_user.email                  			= email
	new_user.role_profile_name      			= "POS User"
	new_user.module_profile         			= "Pos Saller"
	new_user.send_welcome_email     			= False
	new_user.reset_password_key     			= ""
	new_user.insert(ignore_permissions=True)
	# update new user after create new user
	new_user.db_set("user_type", "System User")

	##### create new permission
def create_user_permission(email, companyname):
	new_permisson = frappe.new_doc('User Permission')
	new_permisson.user              			= email
	new_permisson.allow            				= "Company"
	new_permisson.for_value         			= companyname
	new_permisson.is_default        			= True
	new_permisson.insert(ignore_permissions=True)

	
	##### create posprofile for user after sign up new account
def create_posprofile(companyname):
	random_pos_profile = ''.join(random.sample(string.ascii_lowercase, 8))
	new_posprofile = frappe.new_doc('POS Profile')
	new_posprofile.name             			= random_pos_profile
	new_posprofile.company          			= companyname
	new_posprofile.warehouse        			= f"Stores - {create_company.myname.abbr}"
	new_posprofile.append('payments', {
		'mode_of_payment': 'Cash',
		"default": 1,
		"allow_in_return": 1,
	})
	new_posprofile.currency = "USD"
	new_posprofile.write_off_account         	= f"Write off - {create_company.myname.abbr}"
	new_posprofile.write_off_cost_center     	= f"Main - {create_company.myname.abbr}"
	new_posprofile.write_off_limit           	= 1
	new_posprofile.hide_unavailable_items    	= 1
	new_posprofile.append('item_groups',{
		'item_group':'All Item Groups'
	})
	new_posprofile.append('customer_groups',{
		'customer_group':'All Customer Groups'
	})
	new_posprofile.insert(ignore_permissions=True, ignore_mandatory=True)
	create_posprofile.posname = new_posprofile


	#### create new POS opening Entry
def create_pos_opening_entry(email, companyname):
	new_pos_opening_entry = frappe.new_doc('POS Opening Entry')
	new_pos_opening_entry.period_start_date  	= today()
	new_pos_opening_entry.posting_date       	= today()
	new_pos_opening_entry.company            	= companyname
	new_pos_opening_entry.pos_profile        	= create_posprofile.posname.name
	new_pos_opening_entry.user               	= email
	new_pos_opening_entry.append('balance_details', {
		'mode_of_payment': 'Cash',
	})
	new_pos_opening_entry.insert(ignore_permissions=True)
	new_pos_opening_entry.submit()

@frappe.whitelist(allow_guest=True)
def get_user(datauser):
	data_user = frappe.db.get_value("User",{"name":datauser},"user_type")
	if data_user:
		return data_user