function openModal(betId, userId) {

  $(".acceptModal").modal("show");
  $(".acceptBet").attr("onclick", "acceptBet("+betId+", "+userId+")");
  /*$(".acceptBet").click(function() {
    acceptBet(betId, userId);
  });*/

}

function closeModal() {

  $(".acceptModal").modal("hide");

}

function acceptBet(betId, userId) {

  $.ajax({
    url : "/available_bets",
    type : "POST",
    data : {
      user_id : userId,
      bet_id : betId
    }
  }).done(function(message) {
    //alert(message.user);
    //alert(message.bet);
    closeModal();
    $(".bet-section#"+betId).hide();
  });

}
