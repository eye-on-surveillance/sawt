"use client";
import { useEffect, useRef, useState } from "react";
import styles from "./alertsignup.module.scss";

import { TABLES } from "@/lib/supabase/db";
import { supabase } from "@/lib/supabase/supabaseClient";

export default function AlertSignUp({ onSignUpComplete }) {
  const [email, setEmail] = useState("");
  const [selectedTopics, setSelectedTopics] = useState([]);
  const topics = [
    "Community Development",
    "Environment",
    "Budget",
    "Budget/Audit/Board of Review",
    "Surveillance",
    "Palestine",
  ];
  const [successMessage, setSuccessMessage] = useState("");
  const emailInputRef = useRef(null);

  useEffect(() => {
    emailInputRef.current.focus();
  }, []);

  const handleTopicChange = (topic) => {
    if (selectedTopics.includes(topic)) {
      setSelectedTopics(selectedTopics.filter((t) => t !== topic));
    } else {
      setSelectedTopics([...selectedTopics, topic]);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSuccessMessage("");
    await handleSubscription(email, selectedTopics);
  };

  const handleSubscription = async (email, topics) => {
    try {
      const { data, error } = await supabase
        .from(TABLES.ALERTS)
        .insert([{ email: email, topics: topics.join(", ") }]);

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
        <label htmlFor="email">Sign up for email alerts:</label>
        <input
          ref={emailInputRef}
          type="email"
          id="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Enter your email"
          required
        />

        <fieldset>
          <legend>Select topics</legend>
          {topics.map((topic, index) => (
            <div key={index} className={styles["topic-checkbox"]}>
              <input
                type="checkbox"
                id={topic}
                name={topic}
                checked={selectedTopics.includes(topic)}
                onChange={() => handleTopicChange(topic)}
              />
              <label htmlFor={topic}>{topic}</label>
            </div>
          ))}
        </fieldset>

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
