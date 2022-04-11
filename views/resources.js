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

function create_resource(){
  $.ajax({
    type: "POST",
    url: "https://cy08574un0.execute-api.us-east-1.amazonaws.com/dev/boundaries/229408da-73f3-403d-a5fb-f90314e9f182/zones/2/resources",
    data: `{
      "name": "Folsom Field Project",
      "description": "This polygon roughly encapsulates folsom field",
      "polygon": "[[-105.268026, 40.008357], [-105.267992, 40.010473], [-105.265692, 40.010451], [-105.265626, 40.008405]]",
      "metadata": {
        "status": "in progress"
      }
    }`,
    success: function(resources) {
      console.log('success')
    },
    error: function (error) {
        console.log(`Error ${error}`);
    },
    dataType: "json"
  });
}
