import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

import Join from "~join";
import LogIn from "~login";

export default function Landing({ setView }) {
  const [activePage, setActivePage] = useState(0);

  return (
    <div className="landing-page">
      <div className="tab-bar">
        <div onClick={() => setActivePage(0)} className="tab-login">Login</div>
        <div onClick={() => setActivePage(1)} className="tab-join">Join</div>
      </div>

      {/* AnimatePresence ensures only one component is present at a time */}
      <AnimatePresence mode="wait">
        {activePage === 0 && (
          <motion.div
            key="login"
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            transition={{ duration: 0.3 }}
          >
            <LogIn setView={setView} />
          </motion.div>
        )}

        {activePage === 1 && (
          <motion.div
            key="join"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 50 }}
            transition={{ duration: 0.3 }}
          >
            <Join setView={setView} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}