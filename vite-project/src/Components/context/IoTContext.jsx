import React, { createContext, useState } from "react";

export const IoTContext = createContext();

export const IoTProvider = ({ children }) => {
  const [lightsOn, setLightsOn] = useState(false);
  const [buzzerOn, setBuzzerOn] = useState(false); 

  return (
    <IoTContext.Provider
      value={{
        lightsOn,
        setLightsOn,
        buzzerOn,
        setBuzzerOn,
      }}
    >
      {children}
    </IoTContext.Provider>
  );
};
