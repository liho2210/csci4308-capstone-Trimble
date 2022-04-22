// array to store zone polygons
var zone_polys = [];

// initalize function
$(function() {
  // html list to store href links and onclick functionality
  var $zones = $('#zones');
  $.ajax({
          type: "GET",
          url: 'https://cy08574un0.execute-api.us-east-1.amazonaws.com/dev/boundaries/'+localStorage.getItem("boundary")+'/zones',
          data: {},
          success: function(zones) {
            $.each(zones, function(i, zone){
              // add all polygons to array
              zone_polys.push(zone.polygon);
              // add dynamic links to html list
              $zones.append(`<a href="resources.html" onclick="localStorage.setItem('zone', '${zone.zone_id}'); localStorage.setItem('zone_poly', '${zone.polygon}')";>${zone.zone_id}</a>`);
            });
            // store polygon array to local storage
            localStorage.setItem('zone_polys', JSON.stringify(zone_polys));
          },
          // Error handling 
          error: function (error) {
              console.log(`Error ${error}`);
              localStorage.setItem('zone_polys', JSON.stringify(zone_polys));
          },
  });
  console.log(localStorage.getItem("boundary"));
  // console.log(localStorage.getItem("zone"));
  // console.log(JSON.parse(localStorage.getItem("rec_polys")));
  
  console.log(zone_polys);
  // location.reload();
  // window.onload = function () {
  //   if (! localStorage.justOnce) {
  //       localStorage.setItem("justOnce", "true");
        
  //   }
  // }
  // setTimeout(() => window.location.reload(), 2);
  
  // setTimeout(location.reload.bind(location), 600);
})

function create_zone(zone_id, zone_polygon, zone_desc){
$.ajax({
  type: "POST",
  url: "https://cy08574un0.execute-api.us-east-1.amazonaws.com/dev/boundaries/"+localStorage.getItem("boundary")+"/zones",
  data: `{
    "zone_id": "${zone_id}",
    "polygon": ${zone_polygon},
    "description": "${zone_desc}"
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

