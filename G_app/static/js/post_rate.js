$(document).ready(function(){

  $(".rate-form").on("submit", function(event){
    event.preventDefault();
    var formValue = $("input[name=rating]:checked").val();
    var postId = this.id;
    //alert(postId)
    //alert(formValue)
    $.ajax({
      url: "/post_rating",
      type: 'POST',
      data: {
        post_id : postId,
        rating : formValue
      },
      success: function(data){
        //alert(data.message);
        $("div#post"+postId).show();
        $("small#msg"+postId).hide();
        $("p#rating").text("Your vote has registered! Current rating: "+data.rating+"/5");
        $(".rate-form#"+postId).hide();
        $("p#rate"+postId).hide();
      },
      error: function(error){
        alert(error);
      }
    });

  });

});
