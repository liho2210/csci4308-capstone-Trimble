$(function() {
    var $boundaries = $('#boundaries');
    $.ajax({
            type: "GET",
            url: 'https://cy08574un0.execute-api.us-east-1.amazonaws.com/dev/boundary',
            data: {},
            success: function(boundaries) {
              $.each(boundaries, function(i, boundary){
                // $boundaries.append('<li>'+boundary.id+'</li>');
                $boundaries.append('<a href="https://cy08574un0.execute-api.us-east-1.amazonaws.com/dev/boundary/"onclick="location.href=this.href+boundary.id;return false;">'+boundary.name+'</a>');
                // $boundaries.append('<a href="index.html">'+boundary.name+'</a>');
              });
            },

            // Error handling 
            error: function (error) {
                console.log(`Error ${error}`);
            }
    });
      
})

function create_boundary(){
  $.ajax({
    type: "POST",
    url: "https://cy08574un0.execute-api.us-east-1.amazonaws.com/dev/boundary",
    data: `{
      "name": "Folsom Field Project",
      "description": "This polygon roughly encapsulates folsom field",
      "polygon": "[[-105.268026, 40.008357], [-105.267992, 40.010473], [-105.265692, 40.010451], [-105.265626, 40.008405]]",
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
