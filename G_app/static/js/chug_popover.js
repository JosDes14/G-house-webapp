function showDecreaseModal(row, col, amount) {

  $(".decreaseModal").modal("show");

  if (amount > 0) {
    var button = $("<button type='button' class='btn btn-success' onclick='decreaseChug("+row+", "+col+")'>Remove chug</button>");
    $(".customHeader").text("Are you sure?");
    $(".customBody").text("Are you sure that the chug was completed?");
    $(".customFooter").append(button);
  } else {
    $(".customHeader").text("Uh oh...");
    $(".customBody").text("You have 0 chugs to give... You can't decrease that amount.");
  }

}


function closeDecreaseModal() {

  $(".decreaseModal").modal("hide");

}


function decreaseChug(row, col) {

  var idGiver = col + 1;
  var idTaker = row + 1;

  $.ajax({
    url : "/decrease_chug",
    type : "POST",
    data : {
      id_giver : idGiver,
      id_taker : idTaker
    }
  }).done(function(message) {
    alert(message.content);
  });

}
