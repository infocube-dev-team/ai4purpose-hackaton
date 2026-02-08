import React, { useEffect } from 'react';
import { Provider, useDispatch } from 'react-redux';
import KeplerGl from 'kepler.gl';
import { addDataToMap } from 'kepler.gl/actions';
import { processKeplerglJSON } from 'kepler.gl/processors';
import store from './store';

const MAP_ID = 'map';

function MapContainer() {
  const dispatch = useDispatch();

  useEffect(() => {
    // Fetch data from our FastAPI backend
    fetch('http://localhost:8000/api/events?limit=5000')
      .then(res => res.json())
      .then(data => {
        // Data is array of objects. Kepler expects specific format or easier: GeoJSON / CSV
        // If we use addDataToMap, we can pass rows directly if configured right

        // Let's create a dataset structure Kepler likes
        const dataset = {
          info: {
            label: 'Risk Events',
            id: 'risk_events'
          },
          data: {
            fields: [
              { name: 'latitude', type: 'real' },
              { name: 'longitude', type: 'real' },
              { name: '2t', type: 'real' }, // Temperature
              { name: '10u', type: 'real' }, // Wind U
              { name: '10v', type: 'real' }, // Wind V
              // Add other fields as needed based on what backend returns
            ],
            rows: data.map(d => [d.latitude, d.longitude, d['2t'], d['10u'], d['10v']])
          }
        };

        const config = {
          version: 'v1',
          config: {
            mapState: {
              latitude: 40.8518, // Naples approximate
              longitude: 14.2681,
              zoom: 5
            }
          }
        };

        dispatch(
          addDataToMap({
            datasets: dataset,
            options: {
              centerMap: true,
              readOnly: false
            },
            config: config
          })
        );
      })
      .catch(err => console.error("Error loading data:", err));
  }, [dispatch]);

  return (
    <div style={{ position: 'absolute', width: '100%', height: '100%' }}>
      <KeplerGl
        id={MAP_ID}
        width={window.innerWidth}
        height={window.innerHeight}
        mapboxApiAccessToken="" // Optional if using free tiles, or provide token
      />
    </div>
  );
}

function App() {
  return (
    <Provider store={store}>
      <MapContainer />
    </Provider>
  );
}

export default App;
