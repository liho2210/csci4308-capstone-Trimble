$(function() {
    var $resources = $('#resources');
    $.ajax({
            type: "GET",
            url: 'https://cy08574un0.execute-api.us-east-1.amazonaws.com/dev/boundaries/229408da-73f3-403d-a5fb-f90314e9f182/zones/2/resources',
            data: {},
            success: function(resources) {
              $.each(resources, function(i, resource){
                $resources.append('<li>'+resource.description+'</li>');
              });
            },

            // Error handling 
            error: function (error) {
                console.log(`Error ${error}`);
            }
    });
})
