"use client";
import { useState } from "react";
import SignUp from "../components/Alerts/SignUp";
import HomeLearnMore from "../components/Footer/HomeLearnMore";
import HomeBanner from "../components/HomeBanner/HomeBanner";
import HomeResults from "../components/HomeResults/HomeResults";

export default function Home() {
  const [isSignUpComplete, setIsSignUpComplete] = useState(false);

  const handleSignUpComplete = () => {
    setIsSignUpComplete(true);
  };

  // Inline styles for the overlay
  const overlayStyle = {
    position: "fixed",
    top: 0,
    left: 0,
    width: "100%",
    height: "100%",
    backgroundColor: "rgba(0, 0, 0, 0.5)",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    zIndex: 100, // Make sure this is above other content
  };

  return (
    <div>
      {!isSignUpComplete && (
        <div style={overlayStyle}>
          <SignUp onSignUpComplete={handleSignUpComplete} />
        </div>
      )}

      <HomeBanner />
      <HomeResults />
      <HomeLearnMore />
    </div>
  );
}
