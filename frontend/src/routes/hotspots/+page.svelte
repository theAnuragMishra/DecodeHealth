<script>
    import { onMount } from 'svelte';
  
    let map;
    // const location = [25.4358, 81.8463]; // Allahabad
    const location = [26.8467, 80.9462]; // Lucknow

  
    onMount(async () => {
      const L = await import('leaflet');
      await import('leaflet/dist/leaflet.css');
  
      map = L.map('map').setView(location, 15);
  
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
      }).addTo(map);
  
      const circle = L.circle(location, {
        color: 'red',
        fillColor: '#f87171',
        fillOpacity: 0.4,
        radius: 1000
      }).addTo(map);
  
      const popupContent = `
        <div class="p-3 rounded-lg shadow-md text-sm bg-white">
          <div class="text-red-700 font-bold mb-1">⚠️ High Vulnerability Zone</div>
          <div class="text-gray-700">
            Region: <span class="font-semibold">Allahabad</span><br>
            <span class="text-red-600 font-semibold">Precaution Advised:</span> 
            High probability of Diabetes identified
          </div>
        </div>
      `;
  
      circle.bindPopup(popupContent).openPopup();
    });
  </script>
  
  <div id="map" class="h-screen w-full rounded-lg z-0"></div>
  