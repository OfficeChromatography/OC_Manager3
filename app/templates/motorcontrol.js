// AJAX POST
$(document).ready(function(){
  var $myForm = $("#Gcode_form")
  $myForm.submit(function(event){
    event.preventDefault()
    var $formData = $(this).serialize()
    var $endpoint = window.location.href
    $.ajax({
      method: 'POST',
      url:    $endpoint,
      data:   $formData,
      success: handleFormSuccess,
      error: handleFormError,
    })
  })

  function handleFormSuccess(data, textStatus, jqXHR){
      document.getElementById("sentit").value = data.monitor
      scrollit()
      // console.log(data);
      console.log(textStatus)
      // console.log(jqXHR)
      $myForm[0].reset(); // reset form data
  }

  function handleFormError(jqXHR, textStatus, errorThrown){
      // console.log(jqXHR)
      console.log(textStatus)
      // console.log(errorThrown)
  }
})

// Erase button

function erase(){
  event.preventDefault()
  document.getElementById("id_chattext").value = ''
}

// MONITOR CONTROLLER
function scrollit(){
    document.getElementById("sentit").scrollTop = document.getElementById("sentit").scrollHeight
}

// Slider
function sliderChange(val,id){
  document.getElementById(id).value = val;
}

// Buttons move
$(document).ready(function(){
  var $myForm = $(".move-form")
  $myForm.submit(function(event){
    button_pressed = document.activeElement.id
    event.preventDefault()
    var $formData = $(this).serialize() + "&button="+button_pressed
    var $endpoint = window.location.href
    var $speedrange = document.getElementById("speedrange").value
    $.ajax({
      method: 'POST',
      url:    $endpoint,
      data:   $formData,
      success: handleFormSuccess,
      error: handleFormError,
    })
  })

  function handleFormSuccess(data, textStatus, jqXHR){
      document.getElementById("sentit").value = data.monitor
      console.log("bien");
      // console.log(data);
      // console.log(textStatus)
      // console.log(jqXHR)
  }

  function handleFormError(jqXHR, textStatus, errorThrown){
    console.log("error");
      // console.log(jqXHR)
      // console.log(textStatus)
      // console.log(errorThrown)
  }
})

//Intialization
window.onload=scrollit()