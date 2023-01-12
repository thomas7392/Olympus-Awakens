/* Set the width of the side navigation to 250px and the left margin of the page content to 250px */
function openNav() {
  var width = (window.innerWidth > 0) ? window.innerWidth : screen.width;

  if (document.getElementById("mySidebar").style.width == "200px"){
    closeNav();
  }
  else{
    if (width > 700){
      document.getElementById("mySidebar").style.width = "200px";
      document.getElementById("myHeader").style.marginLeft = "200px";
      document.getElementById("myHeader").style.width = "calc(100vw - 200px)";
      document.getElementById("move_content_for_nav").style.marginLeft = "200px"
      document.getElementById("move_content_for_nav").style.width = "calc(100vw - 200px)";
    }
    else {document.getElementById("mySidebar").style.width = "200px";
          document.getElementById("myHeader").style.marginLeft = "200px";
          document.getElementById("move_content_for_nav").style.marginLeft = "200px";}
  }
}

/* Set the width of the side navigation to 0 and the left margin of the page content to 0 */
function closeNav() {
  var width = (window.innerWidth > 0) ? window.innerWidth : screen.width;
  document.getElementById("mySidebar").style.width = "0px";
  document.getElementById("myHeader").style.marginLeft = "0px";
  document.getElementById("move_content_for_nav").style.marginLeft = "0px"
  document.getElementById("move_content_for_nav").style.width = "100%";
  document.getElementById("myHeader").style.width = "100%";
}