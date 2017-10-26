$( document ).ready(function(){
    // Navbar Stuff
    $('.button-collapse').sideNav();
    //Select Menu
    $('select').material_select();
})

function remove_fixed() {
    $('#nav-fixed').removeClass('navbar-fixed')
}