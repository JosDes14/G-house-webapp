$(document).ready(function(){

  $(".rate-form").on("submit", function(event){
    event.preventDefault();
    var postId = this.id;
    var inputName = "rating"+postId;
    var formValue = $("input[name="+inputName+"]:checked").val();
    //alert(postId)
    $.ajax({
      url: "/post_rating",
      type: 'POST',
      data: {
        post_id : postId,
        rating : formValue
      },
      success: function(data){
        //alert(data.message);
        $("div#alert"+postId).show();
        $("small#msg"+postId).hide();
        $("p#rating"+postId).text("Your vote has registered! Current rating: "+data.rating+"/5");
        $(".rate-form#"+postId).hide();
        $("p#rate"+postId).hide();
      },
      error: function(error){
        alert(error);
      }
    });

  });

});
