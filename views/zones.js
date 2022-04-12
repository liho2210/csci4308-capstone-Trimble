$(function() {
    var $zones = $('#zones');
    $.ajax({
            type: "GET",
            url: 'https://cy08574un0.execute-api.us-east-1.amazonaws.com/dev/boundaries/Middle+CU+Project/zones',
            data: {},
            success: function(zones) {
              $.each(zones, function(i, zone){
                $zones.append('<li>'+zone.zone_id+'</li>');
              });
            },

            // Error handling 
            error: function (error) {
                console.log(`Error ${error}`);
            }
    });
})

function create_zone(){
  $.ajax({
    type: "POST",
    url: "https://cy08574un0.execute-api.us-east-1.amazonaws.com/dev/boundaries/Middle+CU+Project/zones",
    data: `{
      "zone_id": "5",
      "polygon": [
        [
          -105.268,
          40.006
        ],
        [
          -105.268,
          40.005
        ],
        [
          -105.266,
          40.005
        ],
        [
          -105.266,
          40.006
        ],
        [
          -105.268,
          40.006
        ]
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
