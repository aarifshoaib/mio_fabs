function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
    }
var csrftoken = getCookie('csrftoken');


function get_message_pop_function(status, msg){
    if (status == 'success'){
        return `<div class="alert alert-success alert-dismissible fade show" role="alert">
                                                                <strong>${msg}</strong>
                                                                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                                                                    <span aria-hidden="true">×</span>
                                                                </button>
                                                            </div>`
    }else{
        return `<div class="alert alert-danger alert-dismissible fade show" role="alert">
                                                                <strong>${msg}</strong>
                                                                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                                                                    <span aria-hidden="true">×</span>
                                                                </button>
                                                            </div>`
    }
}

$('#login-form-authenticate-form-id').submit(function(e){
    e.preventDefault();
    var loginbtn = document.getElementById('login-btn');
    var otpdiv = document.getElementById('otp-input-div');
    var otpinput = document.getElementById('otp-input-id');
    var message_popup = document.getElementById('login-message-popup-id');
    loginbtn.setAttribute('disabled', '');
    loginbtn.value = 'Please Wait..'
    var formData = new FormData(this);
    
    $.ajax({
        type: 'POST',
        url: '/login-authentication-check-secret-key-api',
        data: formData,
        processData: false,
        contentType: false,
        beforeSend: function(xhr, settings) {
                xhr.setRequestHeader('X-CSRFToken', csrftoken);
            },
        success: function(res){
                    loginbtn.removeAttribute('disabled', '');
                    loginbtn.value = 'Login';
                    if (res.status == 'success'){
                        if (res.login){
                            if (res.otp_input == false){
                                otpinput.value = '';
                                otpinput.removeAttribute('required', '');
                                otpdiv.style.display = 'none';
                            }
                            message_popup.innerHTML = get_message_pop_function(res.status, res.msg)
                            location.href = '/dashboard';
                        }else {
                            if (res.otp_input){
                                otpdiv.style.display = '';
                                otpinput.setAttribute('required', '');
                                message_popup.innerHTML = get_message_pop_function(res.status, res.msg)
                            }
                        }
                    }else{
                            if (res.otp_input){
                                otpinput.value = '';
                                otpdiv.style.display = '';
                                if (otpinput.hasAttribute('required') == false){
                                    otpinput.setAttribute('required', '');
                                }
                                message_popup.innerHTML = get_message_pop_function(res.status, res.msg)
                            }else{
                                otpinput.value = '';
                                otpinput.removeAttribute('required', '');
                                otpdiv.style.display = 'none';   
                                message_popup.innerHTML = get_message_pop_function(res.status, res.msg)
                            }
                        }
                },
            error: function(error) {
                loginbtn.removeAttribute('disabled', '');
                loginbtn.value = 'Login';
                location.href = '/admin';
        }
    });
});