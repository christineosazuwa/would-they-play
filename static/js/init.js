  function startPage() {
    setTimeout ( function () {
		setTimeout ( function () {
			$(".desc").removeClass("Out").addClass("In fadeInDown");
		},100 );
		$(".search").removeClass("Out").addClass("In fadeInUp");
		},200 );
    setTimeout ( function () {
			$(".text404").removeClass("Out").addClass("In bounceIn");
		},200 );
	} /*  End animation section home  */
  
  /*Onload function*/
  $(window).load(function(){
    $("body").removeClass("preload");	      
    $(".text404-cut").lettering('words');
    startPage();
  });	
  
  
