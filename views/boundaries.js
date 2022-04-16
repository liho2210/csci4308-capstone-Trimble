$(function() {
  var $boundaries = $('#boundaries');
  $.ajax({
          type: "GET",
          url: 'https://cy08574un0.execute-api.us-east-1.amazonaws.com/dev/boundary',
          data: {},
          success: function(boundaries) {
            $.each(boundaries, function(i, boundary){
              $boundaries.append(`<a href="zones.html" onclick="localStorage.setItem('boundary', '${boundary.id}'); localStorage.setItem('bound_poly', '${boundary.polygon}')";>${boundary.name}</a>`);
            });
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
