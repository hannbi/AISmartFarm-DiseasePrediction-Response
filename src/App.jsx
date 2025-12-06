import { BrowserRouter, Routes, Route } from "react-router-dom";
import StartPage from "./pages/StartPage";
import CropSelect from "./pages/CropSelect";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<StartPage />} />
        <Route path="/crop" element={<CropSelect />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
