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

function openCVentry (entry_name) {
  var targetdiv = document.getElementById(entry_name).lastElementChild;
  var button_1 = document.getElementById(entry_name).querySelector("div:first-of-type button:nth-child(1)");
  var button_2 = document.getElementById(entry_name).querySelector("div:first-of-type button:last-of-type");

  if (targetdiv.style.display === 'block') {
    targetdiv.style.display = 'none';
    button_1.style.borderBottomLeftRadius = "0.25rem";
    button_2.style.borderBottomRightRadius = "0.25rem";
    button_2.innerHTML = "<i class='fa-solid fa-plus' style ='font-size: 16px; '></i>";
  } else {
    targetdiv.style.display = 'block';
    button_1.style.borderBottomLeftRadius = "0";
    button_2.style.borderBottomRightRadius = "0";
    button_2.innerHTML = "<i class='fa-solid fa-minus' style ='font-size: 16px; '></i>";
  }
}


