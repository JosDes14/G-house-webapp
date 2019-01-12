$(document).ready(function(){

  $(".delbtn").click(function(){

    var postId = this.id;
    $("#deleteModal").modal("show");
    $(".deletePost").attr('id', postId);

  });

  $("#closeModal").click(function(){

    $("#deleteModal").modal("hide");

  });

  $(".deletePost").click(function(){

    var postId = this.id
    $("#deleteModal").modal("hide");
    $.ajax({
      url : "/delete_post",
      type : "POST",
      data : {
        post_id : postId
      },
      success : function(data){
        //alert(data.message)
      }
    });
    $("#post"+postId).hide();

  });
});
