// --- LIVE LOCATION UPDATES FOR USERS ---
function sendLiveLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(pos => {
            const lat = pos.coords.latitude;
            const lon = pos.coords.longitude;

            fetch('/update_location', {
                method: 'POST',
                headers: {'Content-Type':'application/json'},
                body: JSON.stringify({lat, lon})
            })
            .then(res => res.json())
            .then(data => console.log('Live location sent:', data))
            .catch(err => console.error('Error sending location:', err));
        });
    }
}

// Send every 5 seconds
setInterval(sendLiveLocation, 5000);

// --- MAP PREVIEW FUNCTION (for user forms) ---
function initMapPreview(latInputId, lonInputId, mapDivId) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(pos => {
            const lat = pos.coords.latitude;
            const lon = pos.coords.longitude;

            document.getElementById(latInputId).value = lat;
            document.getElementById(lonInputId).value = lon;

            const map = L.map(mapDivId).setView([lat, lon], 15);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(map);
            L.marker([lat, lon]).addTo(map).bindPopup("Your Location").openPopup();
        });
    } else {
        alert("Geolocation is not supported by your browser.");
    }
}

// --- ADMIN DASHBOARD: CHECK FOR NEW REQUESTS ---
function checkNewRequests(adminId) {
    fetch('/get_new_requests/' + adminId)
        .then(res => res.json())
        .then(data => {
            if (data.new_requests.length > 0) {
                const notifDiv = document.getElementById('notifications');
                if (notifDiv) {
                    notifDiv.innerHTML = '🔥 New Request!';
                }
                // Optionally, append new rows dynamically to the table
                console.log('New Requests:', data.new_requests);
            }
        })
        .catch(err => console.error('Error fetching new requests:', err));
}

// Check every 5 seconds
setInterval(() => {
    const adminDiv = document.getElementById('notifications');
    if(adminDiv) {
        const adminId = adminDiv.dataset.adminId;
        checkNewRequests(adminId);
    }
}, 5000);

// --- ADMIN TRACKING PAGE: LIVE MARKERS ---
function initTrackingMap(adminLat, adminLon, userLat, userLon, userId) {
    adminLat = parseFloat(adminLat);
    adminLon = parseFloat(adminLon);
    userLat = parseFloat(userLat);
    userLon = parseFloat(userLon);

    const map = L.map('map').setView([userLat, userLon], 14);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(map);

    const userMarker = L.marker([userLat, userLon]).addTo(map).bindPopup("User Location");
    const adminMarker = L.marker([adminLat, adminLon], {
        icon: L.icon({
            iconUrl:'https://cdn-icons-png.flaticon.com/512/149/149059.png',
            iconSize:[30,30]
        })
    }).addTo(map).bindPopup("Admin Location");

    const routeControl = L.Routing.control({
        waypoints: [
            L.latLng(adminLat, adminLon),
            L.latLng(userLat, userLon)
        ],
        addWaypoints: false,
        draggableWaypoints: false,
        routeWhileDragging: false
    }).addTo(map);

    // Update admin location
    setInterval(() => {
        if(navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(pos => {
                adminLat = pos.coords.latitude;
                adminLon = pos.coords.longitude;
                adminMarker.setLatLng([adminLat, adminLon]);
                routeControl.setWaypoints([L.latLng(adminLat, adminLon), L.latLng(userLat, userLon)]);
            });
        }
    }, 5000);

    // Poll user location from server
    setInterval(() => {
        fetch('/get_user_location/' + userId)
        .then(res => res.json())
        .then(loc => {
            if(loc.lat && loc.lon){
                userLat = parseFloat(loc.lat);
                userLon = parseFloat(loc.lon);
                userMarker.setLatLng([userLat, userLon]);
                routeControl.setWaypoints([L.latLng(adminLat, adminLon), L.latLng(userLat, userLon)]);
            }
        });
    }, 5000);
}
