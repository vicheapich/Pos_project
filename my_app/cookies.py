import frappe
from frappe.auth import clear_cookies
def check_role(login_manager):
    data_user = frappe.db.get_value("User",{"name":frappe.session.user},"module_profile")
    frappe.local.cookie_manager.set_cookie("module_profile", data_user)

# def clean_cookies(login_manager):
# 	if hasattr(frappe.local, "session"):
# 		frappe.session.sid = ""
# 	frappe.local.cookie_manager.delete_cookie(
# 		["full_name", "user_id", "sid", "user_image", "system_user"]
# 	)
def clean_cookies(login_manager):
    clear_cookies()