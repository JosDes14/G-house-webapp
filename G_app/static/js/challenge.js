function changeButton() {
  $('#submit').val('Modify');
};


function refuse(id) {
  var link = "/edit/challenge/id/" + id
  $.ajax({
    url : link,
    type : 'POST',
    data : {
      delete_key : "D3l3t3"
    }
  });
};
