# Frontend - Sistema di Previsione e Analisi del Rischio Meteorologico

Interfaccia web interattiva per la visualizzazione geospaziale dei rischi meteorologici basata su React e Kepler.gl.

## 🌟 Caratteristiche Principali

- **Visualizzazione 3D Interattiva**: Mappe geospaziali interattive con Kepler.gl
- **Dati in Tempo Reale**: Connessione diretta al backend FastAPI per dati meteorologici aggiornati
- **Analisi Multi-Rischio**: Visualizzazione di eventi di rischio storici e previsioni
- **Interfaccia Moderna**: React 19 con Vite per sviluppo rapido e performance elevate

## 🛠 Stack Tecnologico

- **Framework**: React 19.2.0
- **Build Tool**: Vite 7.2.4
- **Visualizzazione**: Kepler.gl 3.2.5
- **State Management**: Redux 5.0.1 + React Redux 9.2.0
- **Styling**: Styled Components 6.3.8
- **React Side Effects**: React Palm 3.3.11

## 📁 Struttura del Progetto

```
frontend/
├── src/
│   ├── App.jsx              # Componente principale con mappa Kepler.gl
│   ├── store.js             # Configurazione Redux store
│   ├── main.jsx             # Punto di ingresso React
│   ├── index.css            # Stili globali
│   └── assets/              # Risorse statiche
├── public/                  # File pubblici
├── package.json             # Dipendenze e script
└── vite.config.js          # Configurazione Vite
```

## 🚀 Avvio Rapido

### Prerequisiti
- Node.js 18+ 
- Backend FastAPI in esecuzione su `http://localhost:8000`

### Installazione e Avvio

1. **Installazione dipendenze**:
```bash
npm install
```

2. **Avvio server di sviluppo**:
```bash
npm run dev
```
L'applicazione sarà disponibile su `http://localhost:5173`

3. **Build per produzione**:
```bash
npm run build
```

4. **Anteprima build di produzione**:
```bash
npm run preview
```

## 🗺️ Funzionalità della Mappa

### Dati Visualizzati
- **Eventi di Rischio Storici**: Recuperati da `/api/events`
- **Coordinate Geografiche**: Latitudine e longitudine per ogni evento
- **Parametri Meteorologici**:
  - Temperatura (`2t`)
  - Componenti del vento (`10u`, `10v`)
  - Altri dati meteo disponibili dal backend

### Interfaccia Kepler.gl
- **Navigazione 3D**: Zoom, pan, rotazione della mappa
- **Layer Personalizzabili**: Filtri e styling per i dati
- **Esportazione**: Salva mappe e configurazioni
- **Analisi Spaziale**: Strumenti di misurazione e overlay

## 🔌 Connessione Backend

Il frontend si connette al backend FastAPI tramite API REST:

### Endpoint Utilizzati
- `GET /api/events?limit=5000`: Recupera eventi di rischio storici

### Formato Dati
Il backend restituisce un array di oggetti con struttura:
```javascript
{
  latitude: number,
  longitude: number,
  '2t': number,        // Temperatura
  '10u': number,       // Vento componente U
  '10v': number,       // Vento componente V
  // ... altri campi meteo
}
```

## 🎨 Personalizzazione

### Modifica Configurazione Mappa
La configurazione iniziale della mappa è definita in `src/App.jsx`:
```javascript
const config = {
  version: 'v1',
  config: {
    mapState: {
      latitude: 40.8518,    // Centro su Napoli
      longitude: 14.2681,
      zoom: 5
    }
  }
};
```

### Aggiunta Nuovi Dati
Per aggiungere nuovi dataset:
1. Modifica la struttura `dataset` in `App.jsx`
2. Aggiungi nuovi campi nell'array `fields`
3. Aggiorna la mappatura dei dati in `rows`

## 🛠 Sviluppo

### Script Disponibili
- `npm run dev`: Server di sviluppo con hot reload
- `npm run build`: Build ottimizzata per produzione
- `npm run lint`: Analisi codice con ESLint
- `npm run preview`: Anteprima build di produzione

### Configurazione ESLint
Il progetto include configurazione ESLint per:
- React Hooks
- React Refresh
- Best practices JavaScript/React

## 🔧 Configurazione Avanzata

### Variabili d'Ambiente
Per la configurazione dell'API backend o Mapbox token:
```bash
# Crea .env.local
VITE_API_BASE_URL=http://localhost:8000
VITE_MAPBOX_TOKEN=your_token_here
```

### Ottimizzazioni Performance
- **React Compiler**: Disabilitato per mantenere performance di sviluppo
- **Bundle Splitting**: Configurato tramite Vite
- **Tree Shaking**: Automatico per le dipendenze

## 🐛 Troubleshooting

### Problemi Comuni
1. **Backend non raggiungibile**: Assicurati che il backend sia in esecuzione su porta 8000
2. **Dati non caricati**: Verifica la risposta dell'API nel browser DevTools
3. **Mappa non visualizzata**: Controlla la console per errori JavaScript

### Debug
- Usa React DevTools per ispezionare componenti
- Controlla Redux DevTools per stato dell'applicazione
- Monitora la scheda Network per chiamate API

## 📚 Risorse

- [Documentazione Kepler.gl](https://docs.kepler.gl/docs/)
- [Documentazione React](https://react.dev/)
- [Documentazione Vite](https://vite.dev/)
- [API del Backend](../src/api/main.py)
