// array to store resource points
var rec_polys = [];

// initalize function
$(function() {
  // html list to store onclick/modal actions
  var $resources = $('#resources');
  $.ajax({
          type: "GET",
          url: 'https://cy08574un0.execute-api.us-east-1.amazonaws.com/dev/boundaries/'+localStorage.getItem("boundary")+'/zones/'+localStorage.getItem("zone")+'/resources',          
          data: {},
          success: function(resources) {
            $.each(resources, function(i, resource){
              // add all resources to array
              rec_polys.push(resource.coordinates);
              // add dynamic functions to html list
              $resources.append('<a data-toggle="modal" data-target="#myModal">'+resource.resource_name+'</a>');
            });
            // store resource points array to local storage
            localStorage.setItem("rec_polys", JSON.stringify(rec_polys));
          },
          // Error handling 
          error: function (error) {
              console.log(`Error ${error}`);
          }
  });
})

// function create_resource(name, type, status, amount, description, coordinates){
// $.ajax({
//   type: "POST",
//   url: "https://cy08574un0.execute-api.us-east-1.amazonaws.com/dev/boundaries/Middle+CU+Project/zones/2/resources",
//   data: `{
//     "resource_name": "${name}",
//     "resource_type": "${type}",
//     "resource_status": "${status}",
//     "amount": "${amount}",
//     "description": "${description}",
//     "coordinates": "${coordinates}"
//   }`,
//   success: function(resources) {
//     console.log('success')
//   },
//   error: function (error) {
//       console.log(`Error ${error}`);
//   },
//   dataType: "json"
// });
// }
function create_resource(){
  $.ajax({
    type: "POST",
    url: "https://cy08574un0.execute-api.us-east-1.amazonaws.com/dev/boundaries/6fd85abc-2eb9-4ce1-9bf8-09ffa706f306/zones/5/resources",
    data: `{
      "resource_name": "Cement",
      "resource_type": "Material",
      "resource_status": "Arrived",
      "amount": "50",
      "description": "Used for building walls",
      "coordinates": [
        [40.0087,
        -105.2708] 
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

