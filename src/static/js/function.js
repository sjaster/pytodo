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