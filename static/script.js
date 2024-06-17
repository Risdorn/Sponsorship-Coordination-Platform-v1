function Form_toggle(id) {
    var form = document.getElementById(id);
    if (form.style.display === "none") {
        form.style.display = "block";
    } else {
        form.style.display = "none";
    }
}

function showForm(id) {
    var form = document.getElementById(id);
    form.style.display = "block";
}

function hideForm(id) {
    var form = document.getElementById(id);
    form.style.display = "none";
}

function id_toggle(form_id, type, id){
    var form = document.getElementById(form_id);
    if (type == "campaign"){
        form.campaign_id.value = id;
    } else if (type == "influencer"){
        form.influencer_id.value = id;
    }
}

function id_toggle2(form_id, id){
    var form = document.getElementById(form_id);
    form.campaign_id.value = id;
}

function id_toggle3(form_id, id, type){
    var form = document.getElementById(form_id);
    form.id.value = id;
    form.form_id.value = type;
}

function Fill_Campaign(goals, visibility, start_date, end_date, budget){
    var form = document.getElementById("edit_campaign");
    // form.name.value = name;
    form.goals.value = goals;
    if (visibility == "public"){
        form.visibility[0].checked = true;
        form.visibility[1].checked = false;
    } else {
        form.visibility[0].checked = false;
        form.visibility[1].checked = true;
    }
    form.start_date.value = start_date;
    form.end_date.value = end_date;
    form.budget.value = budget;
}