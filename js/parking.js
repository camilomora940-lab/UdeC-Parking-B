/* =====================================================
   UdeC ParkApp — Parking Data Engine (Supabase Realtime)
   ===================================================== */

const ParkingModule = (() => {
  let SECTORS = [];
  let state = {};
  let onUpdateCallback = null;

  async function initState() {
    try {
      // Fetch sectors from Supabase
      const { data, error } = await supabase.from('sectors').select('*');
      if (error) throw error;
      
      SECTORS = data.map(s => ({
        id: s.id,
        name: s.name,
        shortName: s.short_name,
        emoji: s.emoji,
        lat: s.lat,
        lng: s.lng,
        capacity: s.capacity,
        zone: s.zone,
        level: s.level,
        hours: s.hours,
        contact: s.contact
      }));

      // Initialize state
      data.forEach(s => {
        state[s.id] = {
          occupied: s.occupied,
          available: s.capacity - s.occupied,
          lastUpdated: new Date().toISOString(),
          trend: 'stable' // We could compute this if we track history
        };
      });

    } catch (e) {
      console.error('Error fetching from Supabase:', e);
    }
  }

  // Get sector with computed status
  function getSectorData(sectorId) {
    const sector = SECTORS.find(s => s.id === sectorId);
    if (!sector) return null;
    const s = state[sectorId] || { occupied: 0, available: sector.capacity, lastUpdated: null };
    const occupancyRate = s.occupied / sector.capacity;

    let status, statusLabel, statusColor;
    if (occupancyRate >= 0.95) {
      status = 'full'; statusLabel = 'Lleno'; statusColor = '#FF4B5C';
    } else if (occupancyRate >= 0.7) {
      status = 'limited'; statusLabel = 'Limitado'; statusColor = '#FFB800';
    } else {
      status = 'available'; statusLabel = 'Disponible'; statusColor = '#00D185';
    }

    return {
      ...sector,
      ...s,
      occupancyRate,
      occupancyPercent: Math.round(occupancyRate * 100),
      status,
      statusLabel,
      statusColor
    };
  }

  function getAllSectors() {
    return SECTORS.map(s => getSectorData(s.id));
  }

  function getTotals() {
    const all = getAllSectors();
    return {
      totalCapacity: all.reduce((a, s) => a + s.capacity, 0),
      totalOccupied: all.reduce((a, s) => a + s.occupied, 0),
      totalAvailable: all.reduce((a, s) => a + s.available, 0),
      full: all.filter(s => s.status === 'full').length,
      limited: all.filter(s => s.status === 'limited').length,
      available: all.filter(s => s.status === 'available').length
    };
  }

  // History for charts (simulated for now)
  function getHistory() {
    const hours = [];
    const now = new Date();
    for (let i = 7; i >= 0; i--) {
      const h = new Date(now.getTime() - i * 60 * 60 * 1000);
      const hour = h.getHours();
      let pct;
      if (hour >= 8 && hour <= 10) pct = 80 + Math.random() * 15;
      else if (hour >= 12 && hour <= 13) pct = 65 + Math.random() * 15;
      else if (hour >= 17 && hour <= 19) pct = 85 + Math.random() * 12;
      else if (hour >= 22 || hour <= 6) pct = 2 + Math.random() * 8;
      else pct = 40 + Math.random() * 25;
      hours.push({ label: `${hour.toString().padStart(2, '0')}:00`, pct: Math.round(pct) });
    }
    return hours;
  }

  // Start Realtime Subscription
  async function startSimulation(onUpdate) {
    onUpdateCallback = onUpdate;
    await initState();
    
    // Trigger initial render
    if (typeof onUpdateCallback === 'function') {
      onUpdateCallback(getAllSectors(), getTotals());
    }

    // Subscribe to realtime changes on 'sectors' table
    supabase
      .channel('public:sectors')
      .on('postgres_changes', { event: 'UPDATE', schema: 'public', table: 'sectors' }, payload => {
        const updatedSector = payload.new;
        const oldState = state[updatedSector.id];
        
        let trend = 'stable';
        if (oldState) {
          if (updatedSector.occupied > oldState.occupied) trend = 'up';
          else if (updatedSector.occupied < oldState.occupied) trend = 'down';
        }

        state[updatedSector.id] = {
          occupied: updatedSector.occupied,
          available: updatedSector.capacity - updatedSector.occupied,
          lastUpdated: new Date().toISOString(),
          trend: trend
        };

        if (typeof onUpdateCallback === 'function') {
          onUpdateCallback(getAllSectors(), getTotals());
        }
      })
      .subscribe();

    return null; // No interval to return
  }

  // Notifications check
  function checkAlerts(prevTotals, newTotals) {
    const alerts = [];
    const all = getAllSectors();

    all.forEach(s => {
      if (s.status === 'full' && s.trend === 'up') {
        alerts.push({ type: 'warning', sector: s.name, msg: `${s.shortName} está completamente lleno` });
      }
      if (s.status === 'available' && s.occupancyPercent < 30 && s.trend === 'down') {
        alerts.push({ type: 'success', sector: s.name, msg: `${s.shortName} tiene buena disponibilidad (${s.available} espacios)` });
      }
    });
    return alerts;
  }

  return {
    initState,
    getAllSectors,
    getSectorData,
    getTotals,
    getHistory,
    startSimulation,
    checkAlerts,
    get SECTORS() { return SECTORS; }
  };
})();
