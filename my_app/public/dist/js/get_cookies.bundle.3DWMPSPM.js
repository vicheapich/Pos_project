(() => {
  // ../my_app/my_app/public/js/get_cookies.bundle.js
  var cookies = frappe.get_cookies();
  if (cookies.module_profile === "Pos Saller") {
    window.location.href = "/app/point-of-sale";
    document.cookie = "module_profile = None;";
  }
})();
//# sourceMappingURL=get_cookies.bundle.3DWMPSPM.js.map
