frappe.ready(function(){
    let datauser = frappe.session.user
    // console.log(datauser);
    frappe.call({
        method: "my_app.api.get_user",
        type:"GET",
        args: {
            "datauser": datauser,
        }, callback: function(r) {
        //    console.log(r.message)   
           let cl = document.getElementsByClassName("nav-link")[3];
           if (r.message === "System User"){
            cl.style.display = "none"
           }else{
            cl.style.display = "block"
           }
        }
    })
});