$(document).ready(function(){
    $('.sidenav').sidenav({ edge: "right"});
    $('.slider').slider();
    $('.dropdown-trigger').dropdown({ edge: "right" });
    $(".copyright").text(new Date().getFullYear())
    $('.tooltipped').tooltip();
    $('select').formSelect();
  });

 