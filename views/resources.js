$(function() {
    var $resources = $('#resources');
    $.ajax({
            type: "GET",
            url: 'https://cy08574un0.execute-api.us-east-1.amazonaws.com/dev/boundaries/Middle+CU+Project/zones/2/resources',
            data: {},
            success: function(resources) {
              $.each(resources, function(i, resource){
                $resources.append('<a data-toggle="modal" style="display: inline" data-target="#myModal">'+resource.resource_name+'</a>');
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
    url: "https://cy08574un0.execute-api.us-east-1.amazonaws.com/dev/boundaries/Middle+CU+Project/zones/2/resources",
    data: `{
      "resource_name": "Brick",
      "resource_type": "Material",
      "resource_status": "Arrived",
      "amount": "50",
      "description": "Used for building walls",
      "coordinates": [
        -105.267,
        40.006
      ]
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
