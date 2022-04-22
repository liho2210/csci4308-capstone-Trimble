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
  console.log(localStorage.getItem("boundary"));
  console.log(localStorage.getItem("zone"));
  console.log(JSON.parse(localStorage.getItem("bound_polys")));
})

function create_boundary(bound_name, bound_desc, bound_polygon){
$.ajax({
  type: "POST",
  url: "https://cy08574un0.execute-api.us-east-1.amazonaws.com/dev/boundary",
  data: `{
    "name": "${bound_name}",
    "description": "${bound_desc}",
    "polygon": "${bound_polygon}",
    "metadata": {
      "status": "in progress"
    }
  }`,
  success: function(boundaries) {
    console.log('success')
    window.location.reload();
  },
  error: function (error) {
      console.log(`Error ${error}`);
  },
  dataType: "json"
});
}
