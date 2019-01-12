function update_groceries(id, prevInHouse){
  $.ajax({
    url: "/update_groceries",
    type: 'POST',
    data: {
      id : id,
      prev_in_house : prevInHouse
    },
    success: function(data){
      //alert(data.message);
      //alert(data.message);
    },
    error: function(error){
      alert(error);
    }
  });
}
