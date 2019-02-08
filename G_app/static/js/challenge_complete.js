$(document).ready(function() {


  $(".completeBtn").click(function() {

    $(".completeModal").modal("show");
    $(".completeClaim").attr("id", this.id);

  });


  $(".closeModal").click(function() {

    $(".completeModal").modal("hide");
    $(".verifyModal").modal("hide");

  });


  $(".completeClaim, .refuseClaim, .verifyChallenge").click(function() {

    var isVerification;
    var challengeCompleted;
    var hideChallenge;

    if (this.className.includes("completeClaim")) {
      isVerification = false;
      challengeCompleted = false;
      hideChallenge = false;
    } else if (this.className.includes("refuseClaim")) {
      isVerification = true;
      challengeCompleted = false;
      hideChallenge = true;
    } else {
      isVerification = true;
      challengeCompleted = true;
      hideChallenge = true;
    }

    var challengeId = this.id;


    $(".completeModal").modal("hide");
    $(".verifyModal").modal("hide");

    $.ajax({
      url : "/challenge_completed",
      type : "POST",
      data : {
        challenge_id : challengeId,
        is_verification : isVerification,
        completed : challengeCompleted
      }
    }).done(function(message) {
      $("#completeMsg"+challengeId).show('slow');
      $(".completeBtn#"+challengeId).hide();
      if (hideChallenge) {
        $(".challenge"+challengeId).hide();
      }
      //alert(message.content)
    });
  });


});

function verifyChallenge(id, name) {

  var modalContent = name + " claims he has completed this challenge. Please verify this claim.";
  $(".verifyModal").modal("show");
  $(".verifyChallenge").attr("id", id);
  $(".refuseClaim").attr("id", id);
  $(".customModalBody").text(modalContent);

};
