function updateInfo() {

  var amount = $(".amount").val();
  var odds = $(".odds").val()

  if (amount != '' && odds != '' && !(isNaN(amount)) && !(isNaN(odds))) {

    var lose = parseFloat((amount*odds) - amount).toFixed(2);
    var win = parseFloat(amount).toFixed(2);
    var info = "If the statement in the description is true you will lose " +
      lose + " ₲. If it is false you will win " + win + " ₲.";

    $(".info-box").fadeIn();
    $(".info-text").text(info);

  } else {

    $(".info-box").fadeOut();

  }

}
