import re

with open('dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace CSS Link
content = content.replace(
    '<link href="https://cesium.com/downloads/cesiumjs/releases/1.116/Build/Cesium/Widgets/widgets.css" rel="stylesheet">',
    '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />'
)

# Replace Cesium script link
content = content.replace(
    '<script src="https://cesium.com/downloads/cesiumjs/releases/1.116/Build/Cesium/Cesium.js"></script>',
    '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>'
)

# Containers
content = content.replace(
    '<div id="cesiumContainer"></div>\n            <div id="markersContainer"></div>',
    '<div id="map"></div>'
)

content = content.replace(
    '''<div id="cesiumContainer"></div>
            <div id="markersContainer"></div>''',
    '<div id="map"></div>'
)

# Replace Styles
pattern_style = re.compile(r'/\* ── Cesium Overlays ── \*/.*?/\* ── Responsive ── \*/', re.DOTALL)
new_style = r'''/* ── Leaflet Overrides ── */
    #map {
      width: 100%;
      height: 100%;
      min-height: 500px;
      z-index: 1;
    }

    .leaflet-popup-content-wrapper {
      background: #0A1628;
      color: #F0F6FF;
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 16px;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
      padding: 0;
      overflow: hidden;
    }

    .leaflet-popup-content {
      margin: 0;
      width: 260px !important;
    }

    .leaflet-popup-tip {
      background: #0A1628;
      border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .leaflet-container a.leaflet-popup-close-button {
      color: #8BA4C2;
      padding: 12px 12px 0 0;
      width: 24px;
      height: 24px;
      font-size: 18px;
    }

    .leaflet-container a.leaflet-popup-close-button:hover {
      color: #FFF;
      background: transparent;
    }

    .popup-header {
      padding: 16px 16px 12px;
      display: flex;
      align-items: center;
      gap: 12px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }

    .popup-emoji {
      font-size: 28px;
      background: rgba(255, 255, 255, 0.05);
      width: 48px;
      height: 48px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 12px;
    }

    .popup-title {
      font-size: 15px;
      font-weight: 700;
      color: #F0F6FF;
      margin-bottom: 2px;
    }

    .popup-subtitle {
      font-size: 11px;
      color: #8BA4C2;
      font-weight: 500;
    }

    .popup-body {
      padding: 16px;
    }

    .popup-occupancy {
      background: rgba(255, 255, 255, 0.03);
      border-radius: 12px;
      padding: 12px;
      margin-bottom: 16px;
    }

    .popup-occ-row {
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      margin-bottom: 8px;
    }

    .popup-occ-avail {
      font-size: 28px;
      font-weight: 900;
      line-height: 1;
      letter-spacing: -1px;
    }

    .popup-progress {
      height: 6px;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 3px;
      overflow: hidden;
    }

    .popup-progress-fill {
      height: 100%;
      border-radius: 3px;
      transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .popup-info {
      font-size: 12px;
      color: #8BA4C2;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .popup-info span {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .popup-nav-btn {
      display: block;
      width: 100%;
      margin-top: 16px;
      padding: 10px;
      background: linear-gradient(135deg, #003B7A, #00A86B);
      color: white;
      border: none;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      text-align: center;
      text-decoration: none;
      transition: opacity 0.2s;
    }

    .popup-nav-btn:hover {
      opacity: 0.9;
      color: white;
      text-decoration: none;
    }

    /* ── Responsive ── */'''
content = pattern_style.sub(new_style, content)

# Map Init Script
pattern_script = re.compile(r'// ── Map Init \(Cesium\) ──.*?// ── Sector List ──', re.DOTALL)
new_script = r'''// ── Map Init ──
    let map;
    let markers = {};
    let activePopupId = null;

    // Inicializar mapa de Leaflet
    map = L.map('map', {
      zoomControl: false,
      attributionControl: false
    }).setView([-36.82814, -73.03363], 16);

    // Capa base clara por defecto
    let baseLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
      maxZoom: 19
    }).addTo(map);

    let isSatellite = false;

    function toggleSatellite() {
      isSatellite = !isSatellite;
      const btn = document.getElementById('satelliteBtn');
      
      if (isSatellite) {
        baseLayer.setUrl('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}');
        btn.classList.add('active');
        btn.style.background = 'var(--primary)';
        btn.style.color = '#fff';
      } else {
        baseLayer.setUrl('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png');
        btn.classList.remove('active');
        btn.style.background = 'rgba(10, 22, 40, 0.6)';
        btn.style.color = '#8BA4C2';
      }
    }

    function locateGPS() {
      if (!navigator.geolocation) {
        showToast('error', 'GPS no soportado', 'Tu navegador no soporta geolocalización.');
        return;
      }
      showToast('info', 'Ubicando...', 'Obteniendo señal GPS...', 2000);
      map.locate({setView: true, maxZoom: 18});
      map.once('locationfound', function(e) {
        showToast('success', 'Ubicado', 'Se ha centrado el mapa en tu posición.');
      });
      map.once('locationerror', function(e) {
        showToast('error', 'Error GPS', 'No se pudo obtener tu ubicación.');
      });
    }

    function createMarkerIcon(sector) {
      const colors = {
        available: '#00D185',
        limited: '#FFB800',
        full: '#FF4B5C'
      };
      
      const color = colors[sector.status];
      const pct = sector.occupancyPercent;
      
      const html = `
        <div style="
          width: 48px;
          height: 48px;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          background: linear-gradient(135deg, rgba(6, 14, 26, 0.95), rgba(10, 22, 40, 0.95));
          border: 2px solid ${color};
          border-radius: 14px;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5), 0 0 15px ${color}44;
          position: relative;
        ">
          <span style="font-size: 16px; line-height: 1;">${sector.emoji}</span>
          <span style="font-size: 10px; font-weight: 700; color: ${color}; margin-top: 2px; line-height: 1;">${pct}%</span>
          
          <div style="
            position: absolute;
            bottom: -6px;
            width: 10px;
            height: 10px;
            background: rgba(10, 22, 40, 0.95);
            border-right: 2px solid ${color};
            border-bottom: 2px solid ${color};
            transform: rotate(45deg);
          "></div>
        </div>
      `;

      return L.divIcon({
        className: 'custom-div-icon',
        html: html,
        iconSize: [48, 48],
        iconAnchor: [24, 52],
        popupAnchor: [0, -56]
      });
    }

    function createPopupHTML(sector) {
      const colors = {
        available: '#00D185',
        limited: '#FFB800',
        full: '#FF4B5C'
      };
      const color = colors[sector.status];
      const trendIcon = sector.trend === 'up' ? '📈' : sector.trend === 'down' ? '📉' : '➡️';
      const trendText = sector.trend === 'up' ? 'Llenándose rápido' : sector.trend === 'down' ? 'Liberándose' : 'Estable';

      return `
        <div class="popup-header">
          <div class="popup-emoji">${sector.emoji}</div>
          <div>
            <div class="popup-title">${sector.name}</div>
            <div class="popup-subtitle">Zona ${sector.zone} · ${sector.level === 'multilevel' ? 'Multi-nivel' : 'Superficie'}</div>
          </div>
        </div>
        
        <div class="popup-body">
          <div class="popup-occupancy">
            <div class="popup-occ-row">
              <div>
                <div style="font-size: 11px; color: #8BA4C2; margin-bottom: 2px;">Espacios disponibles</div>
                <div class="popup-occ-avail" style="color: ${color}">${sector.available}</div>
              </div>
              <div style="text-align: right;">
                <div style="font-size: 11px; color: #8BA4C2; margin-bottom: 4px;">de ${sector.capacity} totales</div>
                <span style="font-size: 11px; font-weight: 700; color: ${color}; background: ${color}22; padding: 4px 10px; border-radius: 20px;">
                  ${sector.statusLabel}
                </span>
              </div>
            </div>
            
            <div class="popup-progress">
              <div class="popup-progress-fill" style="width: ${sector.occupancyPercent}%; background: ${color};"></div>
            </div>
          </div>
          
          <div class="popup-info">
            <span>${trendIcon} Tendencia: ${trendText}</span>
            <span>🕐 Horario: ${sector.hours}</span>
            <span>📞 Asistencia: ${sector.contact}</span>
          </div>
          
          <a href="https://www.google.com/maps/dir/?api=1&destination=${sector.lat},${sector.lng}" target="_blank" class="popup-nav-btn">
            🧭 Obtener indicaciones
          </a>
        </div>
      `;
    }

    function addOrUpdateMarkers(sectors) {
      sectors.forEach(sector => {
        if (markers[sector.id]) {
          markers[sector.id].setIcon(createMarkerIcon(sector));
          if (activePopupId === sector.id) {
            markers[sector.id].setPopupContent(createPopupHTML(sector));
          } else {
            markers[sector.id]._popup.setContent(createPopupHTML(sector));
          }
        } else {
          const marker = L.marker([sector.lat, sector.lng], {
            icon: createMarkerIcon(sector)
          }).addTo(map);
          
          marker.bindPopup(createPopupHTML(sector));
          
          marker.on('popupopen', () => { activePopupId = sector.id; });
          marker.on('popupclose', () => { if (activePopupId === sector.id) activePopupId = null; });
          
          marker.on('click', () => { selectSector(sector.id); });
          
          markers[sector.id] = marker;
        }
      });
    }

    // ── Sector List ──'''
content = pattern_script.sub(new_script, content)

# Replace selectSector and resetMapView
pattern_select = re.compile(r'function selectSector\(sectorId\) \{.*?function resetMapView\(\) \{.*?\}', re.DOTALL)
new_select = r'''function selectSector(sectorId) {
      selectedSectorId = sectorId;
      const sector = ParkingModule.getSectorData(sectorId);
      
      if (sector) {
        map.flyTo([sector.lat, sector.lng], 18, {
          duration: 1.5,
          easeLinearity: 0.25
        });
        
        if (markers[sectorId]) {
          markers[sectorId].openPopup();
        }
      }
      
      document.querySelectorAll('.sector-card').forEach(card => card.classList.remove('selected'));
      const card = document.getElementById(`scard-${sectorId}`);
      if (card) card.classList.add('selected');
    }

    function resetMapView() {
      map.flyTo([-36.82814, -73.03363], 16, {
        duration: 1.5
      });
    }'''
content = pattern_select.sub(new_select, content)

with open('dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Reverted to Leaflet successfully.")
