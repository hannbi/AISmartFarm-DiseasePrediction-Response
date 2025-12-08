import { BrowserRouter, Routes, Route } from "react-router-dom";
import StartPage from "./pages/StartPage";
import CropSelect from "./pages/CropSelect";
import Monitoring from "./pages/Monitoring";
import Dashboard from "./pages/Dashboard";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<StartPage />} />
        <Route path="/crop" element={<CropSelect />} />
        <Route path="/monitoring/:id" element={<Monitoring />} />
        <Route path="/dashboard/:id" element={<Dashboard />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
