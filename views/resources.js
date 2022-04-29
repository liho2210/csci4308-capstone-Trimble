// array to store resource points
var rec_polys = [];

// initalize function
$(function() {
  // html list to store onclick/modal actions
  rec_polys = [];
  var $resources = $('#resources');
  $.ajax({
          type: "GET",
          url: 'https://cy08574un0.execute-api.us-east-1.amazonaws.com/dev/boundaries/'+localStorage.getItem("boundary")+'/zones/'+localStorage.getItem("zone")+'/resources',          
          data: {},
          success: function(resources) {
            $.each(resources, function(i, resource){
              // add all resources to array
              rec_polys.push(resource.coordinates);
              // if none added, clear rec_polys ************
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
  console.log(localStorage.getItem("boundary"));
  console.log(localStorage.getItem("zone"));
  console.log(JSON.parse(localStorage.getItem("rec_polys")));
})

function create_resource(rec_name,rec_type,rec_stat,
  rec_cnt, rec_desc, rec_lat,rec_lon){
  $.ajax({
    type: "POST",
    url: 'https://cy08574un0.execute-api.us-east-1.amazonaws.com/dev/boundaries/'+localStorage.getItem("boundary")+'/zones/'+localStorage.getItem("zone")+'/resources',
    data: `{
      "resource_name": "${rec_name}",
      "resource_type": "${rec_type}",
      "resource_status": "${rec_stat}",
      "amount": "${rec_cnt}",
      "description": "${rec_desc}",
      "coordinates": [
        [${rec_lat},
        ${rec_lon}] 
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

  function get_events(){
    var $events = $('#events');
      $.ajax({
              type: "GET",
              url: 'https://cy08574un0.execute-api.us-east-1.amazonaws.com/dev/boundaries/'+localStorage.getItem("boundary")+'/'+localStorage.getItem("zone")+'events',
              data: {},
              success: function(events) {
                $.each(events, function(i, event){
                  // add all polygons to array
                  // boundary_events.push(event);
                  // add dynamic links to html list
                  $events.append(event.name);
                });
                console.log($events)
                // store polygon array to local storage
                // localStorage.setItem('bound_events', JSON.stringify(boundary_events));
              },
              // Error handling 
              error: function (error) {
                  console.log(`Error ${error}`);
                  // localStorage.setItem('zone_polys', JSON.stringify(zone_polys));
              },
      });
    }
  

