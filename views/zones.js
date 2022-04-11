$(function() {
    var $zones = $('#zones');
    $.ajax({
            type: "GET",
            url: 'https://cy08574un0.execute-api.us-east-1.amazonaws.com/dev/boundaries/229408da-73f3-403d-a5fb-f90314e9f182/zones',
            data: {},
            success: function(zones) {
              $.each(zones, function(i, zone){
                $zones.append('<li>'+zone.name+'</li>');
              });
            },

            // Error handling 
            error: function (error) {
                console.log(`Error ${error}`);
            }
    });
})
