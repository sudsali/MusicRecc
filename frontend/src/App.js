import './App.css';
import { BrowserRouter as Router } from "react-router-dom";

// import Header from './components/ui/Header';
import AnimatedRoutes from './routes/AnimatedRoutes';

function App() {
  return (
    <div className="App">
      <Router>
        <AnimatedRoutes/>
      </Router>
    </div>
  );
}

export default App;
