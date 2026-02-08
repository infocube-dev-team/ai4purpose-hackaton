import { createStore, combineReducers, applyMiddleware } from 'redux';
import { taskMiddleware } from 'react-palm/tasks';
import keplerGlReducer from 'kepler.gl/reducers';

const reducer = combineReducers({
  keplerGl: keplerGlReducer
});

const store = createStore(reducer, {}, applyMiddleware(taskMiddleware));

export default store;
