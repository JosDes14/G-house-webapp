function openModal() {

  $(".chugModal").modal("show");

}


function closeModal() {

    $(".chugModal").modal("hide");

}


function giveChug(recipientId, giverId) {

  $.ajax({
    url : "/give_chug",
    type : "POST",
    data : {
      recipient_id : recipientId,
      giver_id : giverId
    }
  }).done(function(message) {
    closeModal();
  });

}
