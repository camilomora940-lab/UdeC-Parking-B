import re

with open('dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace CSS
content = content.replace(
    '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />',
    '<link href="https://cesium.com/downloads/cesiumjs/releases/1.116/Build/Cesium/Widgets/widgets.css" rel="stylesheet">'
)

# Replace Leaflet styling
pattern_style = re.compile(r'/\* ── Popup Styling ── \*/.*?/\* ── Responsive ── \*/', re.DOTALL)
new_style = r'''/* ── Cesium Overlays ── */
    #cesiumContainer { width: 100%; height: 100%; }
    .cesium-viewer-bottom { display: none !important; }

    #markersContainer {
      position: absolute;
      top: 0; left: 0;
      width: 100%; height: 100%;
      pointer-events: none;
      z-index: 1000;
      overflow: hidden;
    }

    .cesium-marker-wrap {
      position: absolute;
      transform: translate(-50%, -100%);
      pointer-events: auto;
    }

    /* ── Popup Styling ── */
    .udec-popup {
      position: absolute;
      background: #0A1628;
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 16px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.6);
      color: #F0F6FF;
      padding: 16px;
      transform: translate(-50%, calc(-100% - 60px));
      pointer-events: auto;
      z-index: 1001;
      display: none;
      min-width: 230px;
    }

    .udec-popup.active { display: block; }
    .udec-popup-close {
      position: absolute;
      top: 12px; right: 12px;
      background: none; border: none;
      color: #8BA4C2; cursor: pointer;
      font-size: 16px;
    }
    .udec-popup-close:hover { color: white; }

    .popup-header {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 12px;
    }

    .popup-emoji { font-size: 24px; }
    .popup-title { font-size: 15px; font-weight: 700; color: #F0F6FF; }
    .popup-subtitle { font-size: 11px; color: #8BA4C2; }

    .popup-occupancy {
      background: rgba(255,255,255,0.05);
      border-radius: 10px;
      padding: 10px;
      margin-bottom: 10px;
    }

    .popup-occ-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }

    .popup-occ-avail {
      font-size: 24px;
      font-weight: 900;
      letter-spacing: -1px;
    }

    .popup-progress {
      height: 8px;
      background: rgba(255,255,255,0.1);
      border-radius: 4px;
      overflow: hidden;
    }

    .popup-progress-fill {
      height: 100%;
      border-radius: 4px;
      transition: width 0.6s ease;
    }

    .popup-info { font-size: 11px; color: #8BA4C2; margin-top: 8px; }

    .popup-nav-btn {
      display: block;
      width: 100%;
      margin-top: 10px;
      padding: 8px;
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

    .popup-nav-btn:hover { opacity: 0.85; }

    /* ── Responsive ── */'''
content = pattern_style.sub(new_style, content)

# Map containers
content = content.replace(
    '<div id="map"></div>',
    '<div id="cesiumContainer"></div>\n            <div id="markersContainer"></div>'
)

# Toolbar
content = content.replace(
    '<button class="map-btn" onclick="toggleSatellite()" title="Vista satélite" id="satelliteBtn">🛰️</button>',
    '<button class="map-btn" onclick="locateGPS()" title="Ubicación GPS" id="gpsBtn">📍</button>\n              <button class="map-btn" onclick="toggleSatellite()" title="Vista satélite" id="satelliteBtn">🛰️</button>'
)

# JS Scripts
content = content.replace(
    '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>',
    '<script src="https://cesium.com/downloads/cesiumjs/releases/1.116/Build/Cesium/Cesium.js"></script>'
)

# Map Init Script
pattern_script = re.compile(r'// ── Map Init ──.*?// ── Sector List ──', re.DOTALL)
new_script = r'''// ── Map Init (Cesium) ──
    let viewer;
    let markersHtml = {};
    let activePopupId = null;
    let mapReady = false;

    try {
      viewer = new Cesium.Viewer('cesiumContainer', {
        terrain: Cesium.Terrain.fromWorldTerrain(),
        animation: false,
        baseLayerPicker: false,
        fullscreenButton: false,
        vrButton: false,
        geocoder: false,
        homeButton: false,
        infoBox: false,
        sceneModePicker: false,
        selectionIndicator: false,
        timeline: false,
        navigationHelpButton: false,
        navigationInstructionsInitiallyVisible: false
      });

      const startGoogle3D = async () => {
        try {
          const tileset = await Cesium.createGooglePhotorealistic3DTileset();
          viewer.scene.primitives.add(tileset);
        } catch (e) {
          console.warn("Google 3D Tiles failed to load. Using fallback terrain.");
        }
      };
      startGoogle3D();

      viewer.camera.flyTo({
        destination: Cesium.Cartesian3.fromDegrees(-73.03363, -36.82814, 800),
        orientation: {
          heading: Cesium.Math.toRadians(0),
          pitch: Cesium.Math.toRadians(-45),
          roll: 0.0
        },
        duration: 0
      });

      mapReady = true;

      viewer.scene.preRender.addEventListener(() => {
        for (const id in markersHtml) {
          const m = markersHtml[id];
          if (!m.position) continue;
          const canvasPos = Cesium.SceneTransforms.wgs84ToWindowCoordinates(viewer.scene, m.position);
          if (canvasPos) {
            m.el.style.left = canvasPos.x + 'px';
            m.el.style.top = canvasPos.y + 'px';
            m.el.style.display = 'block';

            if (m.popupEl) {
              m.popupEl.style.left = canvasPos.x + 'px';
              m.popupEl.style.top = canvasPos.y + 'px';
            }
          } else {
            m.el.style.display = 'none';
          }
        }
      });
    } catch (e) {
      console.error("Cesium init error", e);
    }

    function toggleSatellite() {
      showToast('info', 'Vista 3D', 'La vista 3D actual ya utiliza texturas satelitales fotorrealistas.');
    }

    function locateGPS() {
      if (!navigator.geolocation) {
        showToast('error', 'Error GPS', 'Geolocalización no soportada en tu navegador.');
        return;
      }
      showToast('info', 'Ubicando...', 'Obteniendo señal GPS...', 2000);
      navigator.geolocation.getCurrentPosition((pos) => {
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;
        viewer.camera.flyTo({
          destination: Cesium.Cartesian3.fromDegrees(lng, lat, 400),
          orientation: {
            heading: Cesium.Math.toRadians(0),
            pitch: Cesium.Math.toRadians(-60)
          },
          duration: 2
        });
        showToast('success', 'Ubicado', 'Cámara centrada en tu posición.');
      }, (err) => {
        showToast('error', 'Error GPS', 'No se pudo obtener la ubicación.');
      });
    }

    // ── Markers ──
    const markersContainer = document.getElementById('markersContainer');

    function createMarkerHTML(sector) {
      const colors = { available: '#00D185', limited: '#FFB800', full: '#FF4B5C' };
      const color = colors[sector.status];
      const pct = sector.occupancyPercent;

      return `<div style="
        width:52px; height:52px;
        display:flex; flex-direction:column;
        align-items:center; justify-content:center;
        background: linear-gradient(135deg, rgba(6,14,26,0.95), rgba(10,22,40,0.95));
        border: 2px solid ${color};
        border-radius: 14px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5), 0 0 15px ${color}44;
        font-family: Inter, sans-serif;
      ">
        <span style="font-size:18px; line-height:1;">${sector.emoji}</span>
        <span style="font-size:10px; font-weight:700; color:${color}; line-height:1.2;">${pct}%</span>
      </div>`;
    }

    function createPopupHTML(sector) {
      const colors = { available: '#00D185', limited: '#FFB800', full: '#FF4B5C' };
      const color = colors[sector.status];
      const trendIcon = sector.trend === 'up' ? '📈' : sector.trend === 'down' ? '📉' : '➡️';

      return `
        <button class="udec-popup-close" onclick="closePopup('${sector.id}', event)">✕</button>
        <div class="popup-header">
          <span class="popup-emoji">${sector.emoji}</span>
          <div>
            <div class="popup-title">${sector.name}</div>
            <div class="popup-subtitle">Zona ${sector.zone} · ${sector.level === 'multilevel' ? 'Multi-nivel' : 'Superficie'}</div>
          </div>
        </div>

        <div class="popup-occupancy">
          <div class="popup-occ-row">
            <div>
              <div style="font-size:11px;color:#8BA4C2;">Disponibles</div>
              <div class="popup-occ-avail" style="color:${color}">${sector.available}</div>
            </div>
            <div style="text-align:right;">
              <div style="font-size:11px;color:#8BA4C2;">de ${sector.capacity}</div>
              <span style="font-size:12px;font-weight:700;color:${color};background:${color}22;padding:2px 8px;border-radius:20px;">${sector.statusLabel}</span>
            </div>
          </div>
          <div class="popup-progress">
            <div class="popup-progress-fill" style="width:${sector.occupancyPercent}%;background:${color};"></div>
          </div>
        </div>

        <div class="popup-info">
          ${trendIcon} Tendencia: ${sector.trend === 'up' ? 'llenándose' : sector.trend === 'down' ? 'liberándose' : 'estable'}<br>
          🕐 ${sector.hours}<br>
          📞 ${sector.contact}
        </div>

        <a href="https://www.google.com/maps/dir/?api=1&destination=${sector.lat},${sector.lng}" target="_blank" class="popup-nav-btn">
          🧭 Cómo llegar
        </a>
      `;
    }

    function closePopup(id, event) {
      if (event) event.stopPropagation();
      if (markersHtml[id] && markersHtml[id].popupEl) {
        markersHtml[id].popupEl.classList.remove('active');
        activePopupId = null;
      }
    }

    function addOrUpdateMarkers(sectors) {
      if (!mapReady) return;
      sectors.forEach(sector => {
        if (markersHtml[sector.id]) {
          markersHtml[sector.id].el.innerHTML = createMarkerHTML(sector);
          if (markersHtml[sector.id].popupEl) {
            markersHtml[sector.id].popupEl.innerHTML = createPopupHTML(sector);
          }
        } else {
          const el = document.createElement('div');
          el.className = 'cesium-marker-wrap';
          el.innerHTML = createMarkerHTML(sector);
          el.onclick = () => selectSector(sector.id);
          markersContainer.appendChild(el);

          const popupEl = document.createElement('div');
          popupEl.className = 'udec-popup';
          popupEl.innerHTML = createPopupHTML(sector);
          markersContainer.appendChild(popupEl);

          markersHtml[sector.id] = {
            position: Cesium.Cartesian3.fromDegrees(sector.lng, sector.lat),
            el: el,
            popupEl: popupEl
          };
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
      if (!sector) return;

      if (mapReady) {
        viewer.camera.flyTo({
          destination: Cesium.Cartesian3.fromDegrees(sector.lng, sector.lat, 250),
          orientation: {
            heading: viewer.camera.heading,
            pitch: Cesium.Math.toRadians(-45),
            roll: 0.0
          },
          duration: 1.5
        });

        if (activePopupId && markersHtml[activePopupId]) {
          markersHtml[activePopupId].popupEl.classList.remove('active');
        }
        
        if (markersHtml[sectorId]) {
          markersHtml[sectorId].popupEl.classList.add('active');
          activePopupId = sectorId;
        }
      }

      document.querySelectorAll('.sector-card').forEach(c => c.classList.remove('selected'));
      document.getElementById(`scard-${sectorId}`)?.classList.add('selected');
    }

    function resetMapView() {
      if (mapReady) {
        viewer.camera.flyTo({
          destination: Cesium.Cartesian3.fromDegrees(-73.03363, -36.82814, 800),
          orientation: {
            heading: Cesium.Math.toRadians(0),
            pitch: Cesium.Math.toRadians(-45),
            roll: 0.0
          },
          duration: 1.5
        });
      }
    }'''
content = pattern_select.sub(new_select, content)

with open('dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
