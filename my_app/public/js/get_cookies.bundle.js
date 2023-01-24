let cookies = frappe.get_cookies()
// console.log(cookies)
if(cookies.module_profile === "Pos Saller"){
    window.location.href = "/app/point-of-sale"
    document.cookie = "module_profile = None;"
}