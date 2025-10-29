// import reactLogo from './assets/react.svg'
// import viteLogo from '/vite.svg'

import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { DraftPage } from "./drafts/DraftPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<DraftPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
