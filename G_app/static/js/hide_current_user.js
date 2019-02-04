$(document).ready(function() {
  $.ajax({
    url : "/current_user_id"
  }).done(function(id) {
    var target_id = id.id - 1;
    $("ul#target li").eq(target_id).hide();
  });
});
