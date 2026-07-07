"use client";

import { motion } from "framer-motion";
import DigitalClock from "./DigitalClock";

export default function TopNav() {
  return (
    <motion.header
      initial={{ y: -14, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.45, delay: 0.08, ease: [0.16, 1, 0.3, 1] }}
      className="pointer-events-none absolute right-6 top-5 z-40 hidden h-[56px] items-center gap-2 xl:flex"
    >
      <div className="pointer-events-auto">
        <DigitalClock />
      </div>
    </motion.header>
  );
}
