"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from "react";

interface FarmContextType {
  cropType: string;
  setCropType: (crop: string) => void;
  location: string;
  setLocation: (location: string) => void;
}

const FarmContext = createContext<FarmContextType | undefined>(undefined);

export function FarmProvider({ children }: { children: ReactNode }) {
  const [cropType, setCropType] = useState("tomato");
  const [location, setLocation] = useState("Detecting location...");

  useEffect(() => {
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          try {
            const { latitude, longitude } = position.coords;
            // Use OpenStreetMap Nominatim for free reverse geocoding
            const response = await fetch(
              `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&accept-language=en`
            );
            const data = await response.json();
            
            if (data && data.address) {
              const city = data.address.city || data.address.town || data.address.village || data.address.county || "Unknown City";
              const state = data.address.state || "";
              
              const locationString = state ? `${city}, ${state}` : city;
              setLocation(locationString);
            } else {
              setLocation("Global / Unknown");
            }
          } catch (error) {
            console.error("Error fetching location details:", error);
            setLocation("Location unavailable");
          }
        },
        (error) => {
          console.error("Geolocation error:", error);
          setLocation("Location access denied");
        }
      );
    } else {
      setLocation("Geolocation not supported");
    }
  }, []);

  return (
    <FarmContext.Provider value={{ cropType, setCropType, location, setLocation }}>
      {children}
    </FarmContext.Provider>
  );
}

export function useFarm() {
  const context = useContext(FarmContext);
  if (context === undefined) {
    throw new Error("useFarm must be used within a FarmProvider");
  }
  return context;
}
