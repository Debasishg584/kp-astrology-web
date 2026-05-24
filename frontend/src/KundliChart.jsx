import React from 'react';

const PLANET_ABBRS = {
  'Sun': 'Su', 'Moon': 'Mo', 'Mars': 'Ma', 'Mercury': 'Me',
  'Jupiter': 'Ju', 'Venus': 'Ve', 'Saturn': 'Sa', 'Rahu': 'Ra',
  'Ketu': 'Ke', 'Uranus': 'Ur', 'Neptune': 'Ne', 'Pluto': 'Pl'
};

const SIGN_NAMES = [
  'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
  'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
];

const SIGN_ABBRS = ['Ar', 'Ta', 'Ge', 'Cn', 'Le', 'Vi', 'Li', 'Sc', 'Sg', 'Cp', 'Aq', 'Pi'];

export default function KundliChart({ ascSignIdx, rasiOccupancy, bhavaOccupancy, cuspSignIndices, style = 'north', mode = 'rasi' }) {
  
  // Initialize house planets array (1-indexed, houses 1 to 12)
  const housePlanets = Array.from({ length: 13 }, () => []);
  
  if (mode === 'rasi') {
    for (const [p, signIdx] of Object.entries(rasiOccupancy || {})) {
      const houseIdx = (signIdx - ascSignIdx + 12) % 12 + 1;
      if (houseIdx >= 1 && houseIdx <= 12) {
        housePlanets[houseIdx].push(PLANET_ABBRS[p] || p);
      }
    }
  } else {
    for (const [p, houseIdx] of Object.entries(bhavaOccupancy || {})) {
      if (houseIdx >= 1 && houseIdx <= 12) {
        housePlanets[houseIdx].push(PLANET_ABBRS[p] || p);
      }
    }
  }

  // Draw North Indian Diamond Chart
  const renderNorthIndian = () => {
    const houseSigns = [];
    for (let h = 1; h <= 12; h++) {
      if (mode === 'rasi') {
        houseSigns[h] = (ascSignIdx + h - 2) % 12 + 1;
      } else {
        houseSigns[h] = cuspSignIndices?.[h - 1] || 1;
      }
    }

    const houseMeta = {
      1:  { label: [200, 95],  planets: [200, 130] },
      2:  { label: [100, 48],  planets: [100, 75] },
      3:  { label: [48, 100],  planets: [48, 128] },
      4:  { label: [95, 200],  planets: [130, 200] },
      5:  { label: [48, 300],  planets: [48, 328] },
      6:  { label: [100, 352], planets: [100, 378] },
      7:  { label: [200, 305], planets: [200, 275] },
      8:  { label: [300, 352], planets: [300, 378] },
      9:  { label: [352, 300], planets: [352, 328] },
      10: { label: [305, 200], planets: [270, 200] },
      11: { label: [352, 100], planets: [352, 128] },
      12: { label: [300, 48],  planets: [300, 75] }
    };

    return (
      <svg viewBox="0 0 400 400" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" style={{ background: '#020205', borderRadius: '8px' }}>
        {/* Outer Border */}
        <rect x="10" y="10" width="380" height="380" fill="none" stroke="#7c3aed" strokeWidth="2.5" />
        {/* Diagonals */}
        <line x1="10" y1="10" x2="390" y2="390" stroke="#4c1d95" strokeWidth="1.5" />
        <line x1="390" y1="10" x2="10" y2="390" stroke="#4c1d95" strokeWidth="1.5" />
        {/* Inner Diamond */}
        <polygon points="200,10 390,200 200,390 10,200" fill="none" stroke="#7c3aed" strokeWidth="1.5" />
        
        {/* ASC Tag */}
        <text x="200" y="65" textAnchor="middle" fill="#f6c90e" fontSize="10" fontWeight="bold" letterSpacing="1">
          ASC (LAGNA)
        </text>

        {/* Render Houses */}
        {Object.entries(houseMeta).map(([hStr, meta]) => {
          const h = parseInt(hStr);
          const signNum = houseSigns[h];
          const planets = housePlanets[h] || [];
          
          return (
            <React.Fragment key={h}>
              {/* Sign Number */}
              <text x={meta.label[0]} y={meta.label[1]} textAnchor="middle" fill="#f6c90e" fontSize="13" fontWeight="bold">
                {signNum}
              </text>
              {/* Planets */}
              {planets.length > 0 && (
                <text x={meta.planets[0]} y={meta.planets[1]} textAnchor="middle" fill="#e2e8f0" fontSize="12" fontWeight="bold">
                  {planets.reduce((acc, p, idx) => {
                    const chunkIdx = Math.floor(idx / 2);
                    if (!acc[chunkIdx]) acc[chunkIdx] = [];
                    acc[chunkIdx].push(p);
                    return acc;
                  }, []).map((chunk, cIdx) => (
                    <tspan key={cIdx} x={meta.planets[0]} dy={cIdx === 0 ? 0 : 15}>
                      {chunk.join(' ')}
                    </tspan>
                  ))}
                </text>
              )}
            </React.Fragment>
          );
        })}
      </svg>
    );
  };

  // Draw South Indian Box Chart
  const renderSouthIndian = () => {
    const cellMeta = {
      12: { x: 0,   y: 0,   name: 'Pi' }, 
      1:  { x: 100, y: 0,   name: 'Ar' }, 
      2:  { x: 200, y: 0,   name: 'Ta' }, 
      3:  { x: 300, y: 0,   name: 'Ge' }, 
      4:  { x: 300, y: 100, name: 'Cn' }, 
      5:  { x: 300, y: 200, name: 'Le' }, 
      6:  { x: 300, y: 300, name: 'Vi' }, 
      7:  { x: 200, y: 300, name: 'Li' }, 
      8:  { x: 100, y: 300, name: 'Sc' }, 
      9:  { x: 0,   y: 300, name: 'Sg' }, 
      10: { x: 0,   y: 200, name: 'Cp' }, 
      11: { x: 0,   y: 100, name: 'Aq' }  
    };

    const houseSigns = [];
    for (let h = 1; h <= 12; h++) {
      if (mode === 'rasi') {
        houseSigns[h] = (ascSignIdx + h - 2) % 12 + 1;
      } else {
        houseSigns[h] = cuspSignIndices?.[h - 1] || 1;
      }
    }

    const signHouses = {};
    for (let h = 1; h <= 12; h++) {
      const s = houseSigns[h];
      signHouses[s] = h;
    }

    const signPlanets = Array.from({ length: 13 }, () => []);
    if (mode === 'rasi') {
      for (const [p, signIdx] of Object.entries(rasiOccupancy || {})) {
        signPlanets[signIdx].push(PLANET_ABBRS[p] || p);
      }
    } else {
      for (const [p, houseIdx] of Object.entries(bhavaOccupancy || {})) {
        if (houseIdx >= 1 && houseIdx <= 12) {
          const signIdx = houseSigns[houseIdx];
          signPlanets[signIdx].push(PLANET_ABBRS[p] || p);
        }
      }
    }

    return (
      <svg viewBox="0 0 400 400" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" style={{ background: '#020205', borderRadius: '8px' }}>
        {/* Center Empty box border */}
        <rect x="100" y="100" width="200" height="200" fill="rgba(15, 15, 30, 0.4)" stroke="#4c1d95" strokeWidth="1.5" />
        <text x="200" y="190" textAnchor="middle" fill="#7c3aed" fontSize="14" fontWeight="bold" letterSpacing="2">DIVYA DRISHTI</text>
        <text x="200" y="215" textAnchor="middle" fill="#f6c90e" fontSize="11" fontWeight="bold" letterSpacing="1">
          ASC: {SIGN_NAMES[ascSignIdx - 1]?.toUpperCase()}
        </text>

        {Object.entries(cellMeta).map(([sStr, cell]) => {
          const s = parseInt(sStr);
          const px = cell.x;
          const py = cell.y;
          const signName = cell.name;
          const houseNum = signHouses[s];
          const planets = signPlanets[s] || [];

          return (
            <React.Fragment key={s}>
              {/* Outer boundary of box */}
              <rect x={px} y={py} width="100" height="100" fill="none" stroke="#7c3aed" strokeWidth="1.5" />
              {/* Sign Abbreviation */}
              <text x={px + 8} y={py + 20} fill="#94a3b8" fontSize="11" fontWeight="bold">
                {signName.toUpperCase()}
              </text>
              {/* Lagna (ASC) highlight */}
              {s === ascSignIdx && (
                <>
                  <text x={px + 92} y={py + 20} textAnchor="end" fill="#f6c90e" fontSize="10" fontWeight="bold" letterSpacing="0.5">
                    ASC
                  </text>
                  <line x1={px} y1={py} x2={px + 25} y2={py + 25} stroke="#f6c90e" strokeWidth="1.5" />
                </>
              )}
              {/* House Number */}
              {houseNum && (
                <text x={px + 92} y={py + 35} textAnchor="end" fill="#7c3aed" fontSize="10" fontWeight="bold">
                  H{houseNum}
                </text>
              )}
              {/* Planets */}
              {planets.length > 0 && (
                <text x={px + 50} y={py + 55} textAnchor="middle" fill="#e2e8f0" fontSize="11" fontWeight="bold">
                  {planets.reduce((acc, p, idx) => {
                    const chunkIdx = Math.floor(idx / 2);
                    if (!acc[chunkIdx]) acc[chunkIdx] = [];
                    acc[chunkIdx].push(p);
                    return acc;
                  }, []).map((chunk, cIdx) => (
                    <tspan key={cIdx} x={px + 50} dy={cIdx === 0 ? 0 : 15}>
                      {chunk.join(' ')}
                    </tspan>
                  ))}
                </text>
              )}
            </React.Fragment>
          );
        })}
      </svg>
    );
  };

  return style === 'north' ? renderNorthIndian() : renderSouthIndian();
}
