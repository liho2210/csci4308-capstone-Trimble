// array to store zone polygons
var zone_polys = [];
// var boundary_events = [];

// initalize function
$(function() {
  // html list to store href links and onclick functionality
  var $zones = $('#zones');
  var $zone_del = $('#zone_del');
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
              $zone_del.append(`<a href="zones.html" onclick="delete_zone('${zone.zone_id}')";>${zone.zone_id}</a> <br/>`)
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
  success: function() {
    console.log('success')
  },
  error: function (error) {
      console.log(`Error ${error}`);
  },
  dataType: "json"
});
}

function get_events(){
  var $events = $('#events');
    $.ajax({
            type: "GET",
            url: 'https://cy08574un0.execute-api.us-east-1.amazonaws.com/dev/boundaries/'+localStorage.getItem("boundary")+'/events',
            data: {},
            success: function(events) {
              $.each(events, function(i, event){
                $events.append('<b>'+event.resource_name+" (Zone "+
                event.zone_id+"): "+
                event.prev_resource_status+" ---> "+
                event.curr_resource_status+'</b>'+'<br/>');
              });
              console.log($events)
             },
            // Error handling 
            error: function (error) {
                console.log(`Error ${error}`);
            },
    });
  }

function delete_zone(zone_id){
  $.ajax({
    type: "DELETE",
    url: 'https://cy08574un0.execute-api.us-east-1.amazonaws.com/dev/boundaries/'+localStorage.getItem("boundary")+'/zones/'+zone_id,
    success: function() {
      console.log('success')
    },
    error: function (error) {
        console.log(`Error ${error}`);
    },
  });
}
