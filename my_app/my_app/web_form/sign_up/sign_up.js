frappe.ready(function() {
	$( 'input[data-fieldname="confirm_password"]').change(function() {	
		const password = frappe.web_form.get_value(["password"]);
		const confirm_password = frappe.web_form.get_value(["confirm_password"]);
		if(password != confirm_password){
			$( 'input[data-fieldname="confirm_password"]').css("border", "0.5px solid red");
		}
		else{
			$( 'input[data-fieldname="confirm_password"]').css("border", "");
		}
	});
	$(".submit-btn").on("click", function(){
		let data = frappe.web_form.get_values();
		frappe.call({
			method: "my_app.api.register_require",
			args: {
				"data":data
			}, 
			btn: $('primary-action'),
			freeze : true,
			callback: function(r) {
				console.log(r)
				// if(r.message == "Success"){
				// 	window.location.href = "app/payment/retail";
				// }
			}
		})
	})
	frappe.web_form.validate = ()=>{
		const password = frappe.web_form.get_value(["password"]);
		const confirm_password = frappe.web_form.get_value(["confirm_password"]);
		if(password != confirm_password){
			frappe.show_alert({
				message:__("Password not matching"),
				indicator:'red'
			}, 5);
			frappe.web_form.set_value('confirm_password','')
			return false;
		}
		let pass = /^(?=.{3,})(((?=.*[A-Z])(?=.*[a-z]))|((?=.*[A-Z])(?=.*[0-9]))|((?=.*[a-z])(?=.*[0-9]))).*$/
		if (!pass.test(confirm_password) && confirm_password) {
			frappe.show_alert({
				message:__("Your password must contain 3 character and at least 1 upper case, numeric, and special character"),
				indicator:'red'
			}, 10);
			frappe.web_form.set_value('password','')
			frappe.web_form.set_value('confirm_password','')
			return false;
		}
		return true;
	}
})