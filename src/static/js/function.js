$( document ).ready(function(){
    // Navbar Stuff
    $('.button-collapse').sideNav();
    // Navbar Dropdown
    $('.dropdown-button').dropdown({
        hover: true, // Activate on hover
        belowOrigin: true
    });
    //Select Menu
    $('select').material_select();
})

function remove_fixed() {
    $('#nav-fixed').removeClass('navbar-fixed')
}

function check_delete_subject() {
    if (confirm('Delete a subject will result in the deletion of all cards which belong to the subject!') == true){
        $('#confirm_delete').val(true)
    }else {
        $('#confirm_delete').val(false)
    }
}