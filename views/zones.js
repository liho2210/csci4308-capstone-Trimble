$(function() {
    var $zones = $('#zones');
    $.ajax({
            type: "GET",
            url: 'https://cy08574un0.execute-api.us-east-1.amazonaws.com/dev/boundaries/54f6d866-5fec-4180-8ba8-853818d53a6a/zones',
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
