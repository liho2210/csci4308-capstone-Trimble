// array to store boundary polygons
var bound_polys = [];

// initalize function
$(function() {
  // html list to store href links and onclick functionality
  var $boundaries = $('#boundaries');
  $.ajax({
          type: "GET",
          url: 'https://cy08574un0.execute-api.us-east-1.amazonaws.com/dev/boundary',
          data: {},
          success: function(boundaries) {
            $.each(boundaries, function(i, boundary){
              // add all polygons to array
              bound_polys.push(boundary.polygon);
              // add dynamic links to html list
              $boundaries.append(`<a href="zones.html" onclick="localStorage.setItem('boundary', '${boundary.id}'); localStorage.setItem('bound_poly', '${boundary.polygon}')";>${boundary.name}</a>`);
            });
            // store polygon array to local storage
            localStorage.setItem("bound_polys", JSON.stringify(bound_polys));
          },
          // Error handling 
          error: function (error) {
              console.log(`Error ${error}`);
          }
  });
})

function create_boundary(name, description, polygon){
$.ajax({
  type: "POST",
  url: "https://cy08574un0.execute-api.us-east-1.amazonaws.com/dev/boundary",
  data: `{
    "name": "${name}",
    "description": "${description}",
    "polygon": "${polygon}",
    "metadata": {
      "status": "in progress"
    }
  }`,
  success: function(boundaries) {
    console.log('success')
  },
  error: function (error) {
      console.log(`Error ${error}`);
  },
  dataType: "json"
});
}
