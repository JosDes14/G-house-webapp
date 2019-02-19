$(document).ready(function() {

  $(".winClaim, .lostBet, .refuseClaim, .verifyWin").click(function() {

    var isVerification;
    var betWon;
    var hideBet;
    var betId = this.id

    if (this.className.includes("winClaim")) {
      isVerification = false;
      betWon = true;
      hideBet = false;
      $(".winBtn#"+betId).hide();
      $("#claimMsg"+betId).show('slow');
    } else if (this.className.includes("lostBet") || this.className.includes("refuseClaim")) {
      isVerification = true;
      betWon = false;
      hideBet = true;
    } else {
      isVerification = true;
      betWon = true;
      hideBet = true;
    }

    $(".claimModal").modal("hide");
    $(".verifyModal").modal("hide");

    $.ajax({
      url : "/bet_completed",
      type : "POST",
      data : {
        bet_id : betId,
        is_verification : isVerification,
        bet_won : betWon
      }
    }).done(function(message) {
      if (hideBet) {
        $(".bet"+betId).hide();
      }
    });

  });

});

function showWinModal(description, id) {

  $(".claimModal").modal("show");

  var modalContent = "Is the following description true?\n  \"" + description + "\"\nIf yes, then you have won the bet (and viceversa).";
  $(".winModalBody").text(modalContent);

  $(".winClaim").attr("id", id);
  $(".lostBet").attr("id", id);

}

function showVerifyModal(id, name) {

  $(".verifyModal").modal("show");

  var modalContent = name + " claims to have won the bet. Please verify.";
  $(".verifyModalBody").text(modalContent);

  $(".refuseClaim").attr("id", id);
  $(".verifyWin").attr("id", id);

}

function closeModal(modal) {

  if (modal == "claim") {
    $(".claimModal").modal("hide");
  } else if (modal == "verify") {
    $(".verifyModal").modal("hide");
  }

}
