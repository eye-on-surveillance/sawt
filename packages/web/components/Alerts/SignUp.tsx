"use client";
import { TABLES } from "@/lib/supabase/db";
import { supabase } from "@/lib/supabase/supabaseClient";
import { useEffect, useRef, useState } from "react";
import styles from "./alertsignup.module.scss";

interface AlertSignUpProps {
  onSignUpComplete: () => void;
}

export default function AlertSignUp({ onSignUpComplete }: AlertSignUpProps) {
  const [email, setEmail] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const emailInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (emailInputRef.current) {
      emailInputRef.current.focus();
    }
  }, []);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSuccessMessage("");
    await handleSubscription(email);
  };

  const handleSubscription = async (email: string) => {
    try {
      const { data, error } = await supabase
        .from(TABLES.ALERTS)
        .insert([{ email: email, topics: "" }]);
      if (error) {
        console.error("Error inserting subscription", error.message);
        setSuccessMessage(`Error: ${error.message}. Please try again.`);
      } else {
        console.log("Subscription added!", data);
        setSuccessMessage(
          "Thank you for subscribing! You will start receiving alerts soon."
        );
        onSignUpComplete();
      }
    } catch (err) {
      console.error("Unexpected error", err);
      setSuccessMessage("An unexpected error occurred. Please try again.");
    }
  };

  const handleClose = () => {
    onSignUpComplete();
  };

  return (
    <div className={styles["alert-sign-up"]}>
      <form onSubmit={handleSubmit}>
        <label htmlFor="email" className={styles["label"]}>
          Sign up to receive alerts about new ordinances on first reading at
          city council.
        </label>
        <input
          ref={emailInputRef}
          type="email"
          id="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Enter your email"
          required
          className={styles["input"]}
        />
        <button type="submit" className={styles["submit-button"]}>
          Subscribe
        </button>
        {successMessage && (
          <div className={styles["success-message"]}>{successMessage}</div>
        )}
        <button
          type="button"
          onClick={handleClose}
          className={styles["cancel-button"]}
        >
          Cancel
        </button>
      </form>
    </div>
  );
}
