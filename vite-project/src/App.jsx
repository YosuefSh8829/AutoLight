import { Routes, Route } from "react-router-dom";
import Home from "./Components/Home";
import Header from "./Components/Header";
import Login from "./Components/Login";
import Signup from "./Components/Signup";
import Dashboard from "./Components/Dashboard";
import ControlSystem from "./Components/ControlSystem";
import { IoTProvider } from "./Components/context/IoTContext";
import { AuthProvider } from "./Components/AuthContext";

function App() {
  return (
    <AuthProvider>
      <IoTProvider>
        <Header />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/Controlpanel" element={<ControlSystem />} />
        </Routes>
      </IoTProvider>
    </AuthProvider>
  );
}

export default App;
