
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