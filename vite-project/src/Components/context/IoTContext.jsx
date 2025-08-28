import React, { createContext, useState } from "react";

export const IoTContext = createContext();

export const IoTProvider = ({ children }) => {
  const [carDetected, setCarDetected] = useState(false);
  const [flameDetected, setFlameDetected] = useState(false);
  const [lightsOn, setLightsOn] = useState(false);

  return (
    <IoTContext.Provider
      value={{
        carDetected,
        setCarDetected,
        flameDetected,
        setFlameDetected,
        lightsOn,
        setLightsOn,
      }}
    >
      {children}
    </IoTContext.Provider>
  );
};
