import { createMap } from "maplibre-gl-js-amplify"; 
import "maplibre-gl/dist/maplibre-gl.css";
import { useEffect } from 'react';

function Map() {
    return (
        <div className="Map">
            <h1>My Restaurant</h1>
            <ul id="locations">
                <li><b>My Restaurant - Upper East Side</b> <br/> 300 E 77th St, New York, NY 10075 </li>
                <li><b>My Restaurant - Hell's Kitchen</b> <br/> 725 9th Ave, New York, NY 10019</li>
                <li><b>My Restaurant - Lower East Side</b><br/> 102 Norfolk St, New York, NY 10002</li>
            </ul>
        </div>
    );
}


 async function initializeMap() {
    const map = await createMap({
        container: "map", // An HTML Element or HTML element ID to render the map in https://maplibre.org/maplibre-gl-js-docs/api/map/
        center: [-73.98597609730648, 40.751874635721734], // center in New York
        zoom: 11,
    })
    return map;
}

