$(function() {
  var $zones = $('#zones');
  $.ajax({
          type: "GET",
          url: 'https://cy08574un0.execute-api.us-east-1.amazonaws.com/dev/boundaries/'+localStorage.getItem("boundary")+'/zones',
          data: {},
          success: function(zones) {
            $.each(zones, function(i, zone){
              $zones.append(`<a href="resources.html" onclick="localStorage.setItem('zone', '${zone.zone_id}')";>${zone.zone_id}</a>`);
            });
          },

          // Error handling 
          error: function (error) {
              console.log(`Error ${error}`);
          }
  });
  console.log(localStorage.getItem("bound_poly"));
})

function create_zone(){
$.ajax({
  type: "POST",
  url: "https://cy08574un0.execute-api.us-east-1.amazonaws.com/dev/boundaries/"+localStorage.getItem("boundary")+"/zones",
  // data: `{
  //   "zone_id": "${zone_id}",
  //   "polygon": "${polygon}",
  //   "description": "${description}"
  // }`,
  data: `{
    "zone_id": "5",
    "polygon": [
      [40.0102, -105.2714],[40.0068, -105.2714],[40.0072, -105.2629]
    ],
    "description": "These coordinates roughly outline Farrand Field"
  }`,
  success: function(zones) {
    console.log('success')
  },
  error: function (error) {
      console.log(`Error ${error}`);
  },
  dataType: "json"
});
}
