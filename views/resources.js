$(function() {
  var $resources = $('#resources');
  $.ajax({
          type: "GET",
          url: 'https://cy08574un0.execute-api.us-east-1.amazonaws.com/dev/boundaries/'+localStorage.getItem("boundary")+'/zones/'+localStorage.getItem("zone")+'/resources',          
          data: {},
          success: function(resources) {
            $.each(resources, function(i, resource){
              $resources.append('<a data-toggle="modal" data-target="#myModal">'+resource.resource_name+'</a>');
            });
          },

          // Error handling 
          error: function (error) {
              console.log(`Error ${error}`);
          }
  });
})

function create_resource(name, type, status, amount, description, coordinates){
$.ajax({
  type: "POST",
  url: "https://cy08574un0.execute-api.us-east-1.amazonaws.com/dev/boundaries/Middle+CU+Project/zones/2/resources",
  data: `{
    "resource_name": "${name}",
    "resource_type": "${type}",
    "resource_status": "${status}",
    "amount": "${amount}",
    "description": "${description}",
    "coordinates": "${coordinates}"
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
