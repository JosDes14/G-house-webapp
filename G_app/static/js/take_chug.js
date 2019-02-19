function acceptChug(chugId) {

  makeRequest(chugId, true)

}

function refuseChug(chugId) {

  makeRequest(chugId, false)

}


function closeModal() {

  $(".refuseModal").modal("hide");

}


function showModal(chugId, userBalance, chugPrice) {

  var button;

  if (userBalance >= chugPrice) {
    $(".customHeader").text("Are you sure?");
    $(".customBody").text("If you refuse you will spend " + chugPrice.toFixed(2) + "₲.");
    button = $("<button class='btn btn-outline-danger' onclick='refuseChug(" + chugId + ")'>Refuse</button>");
  } else {
    $(".customHeader").text("Uh oh...");
    $(".customBody").text("You don't have enough ₲, you're going to have to accept... If you don't respond within 24hrs the chug will automatically be accepted.");
    button = $("<button class='btn btn-outline-success' onclick='acceptChug(" + chugId + ")'>Accept</button>");
  }

  $(".customFooter").append(button);

  $(".refuseModal").modal("show");

}


function makeRequest(chugId, accept) {

  $.ajax({
    url : "/respond_chug",
    type : "POST",
    data : {
      is_new : false,
      chug_id : chugId,
      accept : accept
    }
  }).done(function(message){
    $(".accept-refuse-menu").hide();
    if (accept) {
      $(".status").text("You have accepted this chug, it is now active until you take it");
    } else {
      $(".status").text("You have refused this chug, it is no longer active");
      closeModal();
    }
  });

}
