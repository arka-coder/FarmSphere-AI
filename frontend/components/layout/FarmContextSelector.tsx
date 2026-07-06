"use client";

import { useFarm } from "@/contexts/FarmContext";
import { Sprout, MapPin, ChevronDown } from "lucide-react";

const CROPS = ["tomato", "wheat", "rice", "cotton", "sugarcane"];
const LOCATIONS = ["Nashik, Maharashtra", "Pune, Maharashtra", "Ludhiana, Punjab", "Karnal, Haryana", "Global / Unknown"];

export default function FarmContextSelector() {
  const { cropType, setCropType, location, setLocation } = useFarm();

  return (
    <div className="flex items-center gap-3">
      {/* Location Selector */}
      <div className="relative group flex items-center gap-1.5 rounded-full border border-slate-200/60 bg-white/60 px-3 py-1.5 text-xs font-semibold text-slate-700 shadow-sm backdrop-blur-md hover:bg-white/90 cursor-pointer">
        <MapPin size={14} className="text-blue-500" />
        <select 
          value={location} 
          onChange={(e) => setLocation(e.target.value)}
          className="appearance-none bg-transparent outline-none cursor-pointer pr-4"
        >
          {LOCATIONS.map(l => <option key={l} value={l}>{l}</option>)}
        </select>
        <ChevronDown size={12} className="absolute right-2.5 text-slate-400 pointer-events-none" />
      </div>
    </div>
  );
}
