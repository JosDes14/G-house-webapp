function set_notification_count(n) {
  $('#notification-badge').text(n);
  if(n > 0){
    $('#notification-badge').css('visibility', 'visible');
  } else {
    $('#notification-badge').css('visibility', 'hidden');
  }
};


$(document).ready(function() {
  setInterval(function() {
    $.ajax({
      url : "/new_notifications"
    }).done(function(notifications) {
      if(notifications) {
        set_notification_count(notifications.length)
      } else {
        set_notification_count(0)
      };
    });
  }, 10000);
});


function seen_notifications(notifications) {
  var notification_ids = [];
  for(var i=0; i<notifications.length; i++){
    notification_ids.push(notifications[i].id)
  };
  $.ajax({
    url : "/seen_notifications",
    type : 'POST',
    data : {
      ids : JSON.stringify(notification_ids)
    }
  });
};


function update_notification_list(header_url) {
  $.ajax({
    url : "/recent_notifications"
  }).done(function(notifications) {
    //var header_url = {{ url_for('your_notifications', user_id=current_user.id) }};
    var header = "<li role='presentation' class='notification-header'><a role='menuitem' class='header-link' href="+ header_url +">All notifications</a></li>";
    var nothing_new = "<li role='presentation' class='notification'>No recent notifications...</li>";
    var idUnseen;
    $('#notification-menu').empty()
    if(notifications.length > 0){
      var length = notifications.length;
      for(var i=0; i<length; i++){
        var url;
        if(notifications[i].link){
          url = notifications[i].link;
        } else {
          url = '#';
        }
        if (!(notifications[i].seen)){
          idUnseen = "id='unseen'";
        } else {
          idUnseen = "";
        }
        var list_item = "<li role='presentation' class='notification' "+ idUnseen +"><a role='menuitem' class='notification-link' href='"+ url +"'>"+ notifications[i].content +"</a></li>";
        var divider = "<li role='presentation' class='divider'></li>";
        $('#notification-menu').append(list_item);
        $('#notification-menu').append(divider);
        seen_notifications(notifications);
        set_notification_count(0);
      };
    } else {
      $('#notification-menu').append(nothing_new);
    }
    $('#notification-menu').append(header)
  });
};
