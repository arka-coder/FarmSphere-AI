"use client";
import { useState, useEffect} from"react";
import { motion} from"framer-motion";
import { Wind, Droplets, Thermometer, Eye, Gauge, CloudRain, MapPin} from"lucide-react";
import Sidebar from"@/components/layout/Sidebar";
import TopNav from"@/components/layout/TopNav";
import { type WeatherData} from"@/lib/api";

const rawApiBase = process.env.NEXT_PUBLIC_API_URL ||"http://localhost:8000";
const API_BASE = rawApiBase.endsWith('/') ? rawApiBase.slice(0, -1) : rawApiBase;

const conditionEmoji: Record<string, string> = {
"Partly Cloudy":"⛅",
"Sunny":"☀️",
"Clear":"☀️",
"Cloudy":"☁️",
"Overcast":"☁️",
"Light Rain":"🌦️",
"Heavy Rain":"🌧️",
"Thunderstorm":"⛈️",
"Foggy":"🌫️",
"Mist":"🌫️",
"Haze":"🌫️",
"Windy":"💨",
"Drizzle":"🌦️",
"Snow":"❄️",
};

const getEmoji = (condition: string) =>
 Object.entries(conditionEmoji).find(([k]) =>
 condition?.toLowerCase().includes(k.toLowerCase())
 )?.[1] ??"🌤️";

async function fetchWeatherByCoords(lat: number, lon: number): Promise<WeatherData> {
 const res = await fetch(`${API_BASE}/api/weather?lat=${lat}&lon=${lon}`);
 if (!res.ok) throw new Error("Weather fetch failed");
 return res.json();
}

export default function WeatherPage() {
 const [weather, setWeather] = useState<WeatherData | null>(null);
 const [loading, setLoading] = useState(true);
 const [error, setError] = useState(false);
 const [geoStatus, setGeoStatus] = useState<"requesting" |"granted" |"denied" |"unavailable">("requesting");

 useEffect(() => {
 if (!navigator.geolocation) {
 setGeoStatus("unavailable");
 // Fall back to server default
 fetch(`${API_BASE}/api/weather`)
 .then(r => r.json()).then(setWeather)
 .catch(() => setError(true))
 .finally(() => setLoading(false));
 return;
}

 navigator.geolocation.getCurrentPosition(
 (pos) => {
 setGeoStatus("granted");
 fetchWeatherByCoords(pos.coords.latitude, pos.coords.longitude)
 .then(setWeather)
 .catch(() => setError(true))
 .finally(() => setLoading(false));
},
 () => {
 setGeoStatus("denied");
 // Fall back to server default location
 fetch(`${API_BASE}/api/weather`)
 .then(r => r.json()).then(setWeather)
 .catch(() => setError(true))
 .finally(() => setLoading(false));
},
 { timeout: 6000, maximumAge: 300000}
 );
}, []);

 // Fallback mock data if backend unavailable
 const w = weather ?? {
 location:"Nashik, Maharashtra",
 temperature: 28,
 feels_like: 31,
 humidity: 72,
 wind_speed: 3.4,
 weather_condition:"Partly Cloudy",
 rainfall_24h: 0,
 pressure: 1012,
 forecast: [
 { day:"Tomorrow", condition:"Light Rain", temp_max: 30, temp_min: 23, humidity: 80, rain_chance: 70},
 { day:"Day After", condition:"Thunderstorm", temp_max: 27, temp_min: 21, humidity: 88, rain_chance: 85},
 { day:"Day 3", condition:"Sunny", temp_max: 32, temp_min: 24, humidity: 60, rain_chance: 20},
 { day:"Day 4", condition:"Partly Cloudy", temp_max: 31, temp_min: 23, humidity: 65, rain_chance: 30},
 { day:"Day 5", condition:"Sunny", temp_max: 33, temp_min: 25, humidity: 55, rain_chance: 10},
 ],
 source:"Mock Data (Backend Unavailable)",
} as any;

 const stats = [
 { icon: <Droplets size={18} className="text-blue-400" />, label:"Humidity", value: `${w.humidity}%`},
 { icon: <Wind size={18} className="text-slate-400" />, label:"Wind Speed", value: `${w.wind_speed} m/s`},
 { icon: <Thermometer size={18} className="text-orange-400" />, label:"Feels Like", value: `${w.feels_like}°C`},
 { icon: <CloudRain size={18} className="text-sky-400" />, label:"Rainfall 24h", value: `${w.rainfall_24h ?? 0} mm`},
 { icon: <Gauge size={18} className="text-purple-400" />, label:"Pressure", value: `${w.pressure ?? 1012} hPa`},
 { icon: <Eye size={18} className="text-emerald-400" />, label:"Condition", value: w.weather_condition},
 ];

 return (
 <div className="flex h-screen bg-base relative overflow-hidden">
 <div className="absolute inset-0 bg-gradient-to-br from-green-50/50 to-emerald-50/30 pointer-events-none" />
 <Sidebar />
 <main className="flex-1 flex flex-col relative overflow-hidden">
 <TopNav />
 <div className="flex-1 overflow-y-auto px-8 pt-28 pb-12 scrollbar-hide">
 <motion.div initial={{ opacity: 0, y: 12}} animate={{ opacity: 1, y: 0}} className="max-w-3xl mx-auto space-y-6">
 {/* Header */}
 <div className="bg-gradient-to-r from-sky-500 to-blue-600 rounded-2xl p-6 text-white relative overflow-hidden">
 <div className="absolute -right-6 -top-6 text-8xl opacity-20">🌤️</div>
 <p className="text-sky-200 text-sm font-medium flex items-center gap-2">
 Current Weather
 {geoStatus ==="requesting" && <span className="animate-pulse bg-sky-400/20 text-sky-200 px-2 py-0.5 rounded text-xs">Detecting location...</span>}
 {geoStatus ==="granted" && <span className="bg-emerald-400/20 text-emerald-200 px-2 py-0.5 rounded text-xs flex items-center gap-1"><MapPin size={10} /> Precise</span>}
 {geoStatus ==="denied" && <span className="bg-amber-400/20 text-amber-200 px-2 py-0.5 rounded text-xs">Using Default (Location Denied)</span>}
 {geoStatus ==="unavailable" && <span className="bg-slate-400/20 text-slate-200 px-2 py-0.5 rounded text-xs">Using Default</span>}
 </p>
 <div className="flex items-end gap-4 mt-1">
 <span className="text-6xl font-bold">{w.temperature}°C</span>
 <div className="mb-2">
 <p className="text-xl font-semibold">{getEmoji(w.weather_condition)} {w.weather_condition}</p>
 <p className="text-sky-200 text-sm flex items-center gap-1"><MapPin size={14} /> {w.location}</p>
 </div>
 </div>
 {error && (
 <p className="mt-2 text-xs text-yellow-200 bg-yellow-500/20 px-3 py-1 rounded-full inline-block">
 ⚠️ Showing mock data — backend weather API unavailable
 </p>
 )}
 </div>

 {/* Stats grid */}
 <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
 {stats.map((s, i) => (
 <motion.div
 key={i}
 initial={{ opacity: 0, y: 8}}
 animate={{ opacity: 1, y: 0}}
 transition={{ delay: i * 0.05}}
 className="glass-card bg-white p-4 flex items-center gap-3"
 >
 <div className="w-10 h-10 rounded-xl bg-gray-50 flex items-center justify-center">
 {s.icon}
 </div>
 <div>
 <p className="text-xs text-gray-400">{s.label}</p>
 <p className="font-semibold text-gray-800">{s.value}</p>
 </div>
 </motion.div>
 ))}
 </div>

 {/* 5-day Forecast */}
 <div className="glass-card bg-white p-5">
 <p className="font-semibold text-gray-800 mb-4">📅 5-Day Forecast</p>
 <div className="grid grid-cols-5 gap-3">
 {(w.forecast || []).slice(0, 5).map((f: any, i: number) => (
 <motion.div
 key={i}
 initial={{ opacity: 0, y: 8}}
 animate={{ opacity: 1, y: 0}}
 transition={{ delay: 0.3 + i * 0.07}}
 className="text-center bg-gray-50 rounded-xl p-3"
 >
 <p className="text-xs text-gray-500">{f.day}</p>
 <p className="text-2xl my-1">{getEmoji(f.condition)}</p>
 <p className="font-bold text-gray-800 text-sm">{f.temp_max}°</p>
 <p className="text-xs text-gray-400">{f.temp_min ?? f.temp_max - 6}°</p>
 <p className="text-xs text-blue-500 mt-1 font-medium">💧 {f.rain_chance}%</p>
 <p className="text-xs text-gray-400 mt-0.5 leading-tight">{f.condition}</p>
 </motion.div>
 ))}
 </div>
 </div>

 {/* Agricultural Advice */}
 <div className="glass-card bg-white p-5">
 <p className="font-semibold text-gray-800 mb-3">🌾 Agricultural Weather Advice</p>
 <div className="space-y-2">
 {(w.forecast?.[0]?.rain_chance ?? 70) > 65 && (
 <div className="flex gap-3 p-3 bg-blue-50 rounded-xl border border-blue-100">
 <span>🌧️</span>
 <p className="text-sm text-blue-700">
 <strong>Rain expected tomorrow</strong> — avoid pesticide and fertilizer application. Schedule irrigation accordingly.
 </p>
 </div>
 )}
 {(w.humidity ?? 72) > 80 && (
 <div className="flex gap-3 p-3 bg-amber-50 rounded-xl border border-amber-100">
 <span>⚠️</span>
 <p className="text-sm text-amber-700">
 <strong>High humidity alert</strong> — elevated fungal disease risk. Consider preventive fungicide spray.
 </p>
 </div>
 )}
 <div className="flex gap-3 p-3 bg-green-50 rounded-xl border border-green-100">
 <span>✅</span>
 <p className="text-sm text-green-700">
 Temperature of <strong>{w.temperature}°C</strong> is suitable for most Kharif crops. Ideal for vegetative growth.
 </p>
 </div>
 </div>
 </div>

 <p className="text-xs text-gray-400 text-center">Data source: {w.source}</p>
 </motion.div>
 </div>
 </main>
 </div>
 );
}
