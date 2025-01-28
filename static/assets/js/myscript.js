
function martialCheck(inp){
    if (inp == 1) {
        document.getElementById('marital-inputs').style.display = 'flex';
    } else {
        document.getElementById('marital-inputs').style.display = 'none';
    }
}

function relativesCheck(inp){
    if (inp == 1) {
        document.getElementById('relatives-inputs').style.display = 'flex';
    } else {
        document.getElementById('relatives-inputs').style.display = 'none';
    }
}

function selectionStatus(inp){
    if (inp == 1) {
        document.getElementById('selection-inputs').style.display = 'flex';
    } else {
        document.getElementById('selection-inputs').style.display = 'none';
    }
}

function physicalCheck(inp){
    if (inp == 1) {
        document.getElementById('physical-inputs').style.display = 'flex';
    } else {
        document.getElementById('physical-inputs').style.display = 'none';
    }
}

function viewPassword(){
    var pass1 = document.getElementById('pass1')
    var pass2 = document.getElementById('pass2')

    if (pass1.type == 'text'){
        pass1.type = 'password';
        pass2.type = 'password';
    } else{
        pass1.type = 'text';
        pass2.type = 'text';
    }
}

function singpassfunc(inp){
    if (inp == 'singpass'){
        var singp = document.getElementById('singpass-id')
        singp.style.display = 'flex';
        var singp_pass = document.getElementById('singpass-password')
        singp_pass.style.display = 'flex';

    } else{
        document.getElementById('singpass-id').style.display = 'none';
        document.getElementById('singpass-password').style.display = 'none';
    }
}