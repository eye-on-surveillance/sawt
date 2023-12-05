"use client"
import React, { useState } from 'react';

const Rubric = ({ criteria }) => {
    // This state will hold the scores for each criterion
    const [scores, setScores] = useState(criteria.reduce((acc, criterion) => {
      acc[criterion.id] = 1; // Initialize all criteria with a score of 1
      return acc;
    }, {}));
  
    const handleScoreChange = (criterionId, score) => {
      setScores(prevScores => ({ ...prevScores, [criterionId]: score }));
    };
  
    const saveScores = () => {
      console.log(scores);
        // TODO:
            // Bundle with the userComments then
            // send scores to supabase.
            // Submit to userFeedback table.

    };
  
    const circleButtonStyle = (score, criterionId) => ({
        width: '40px', // Circle diameter
        height: '40px', // Circle diameter
        borderRadius: '50%', // Make it round
        margin: '5px',
        fontWeight: scores[criterionId] === score ? 'bold' : 'normal',
        outline: 'none',
        border: scores[criterionId] === score ? '2px solid blue' : '1px solid grey'
      });
      const submitButtonStyle = {
        padding: '10px 20px', 
        fontSize: '16px', 
        color: 'white', 
        backgroundColor: '#007bff', 
        border: 'none', 
        borderRadius: '5px', 
        cursor: 'pointer', 
        outline: 'none',
        marginTop: '20px', 
      };
    
      const containerStyle = {
        display: 'flex', 
        justifyContent: 'center', // Center children horizontally
        alignItems: 'center', // Center children vertically
        flexDirection: 'column', // Stack children vertically
        padding: '20px', // Add padding around the container
    };
    
    return (
        <div style= {containerStyle}>
            <div>
                {criteria.map(criterion => (
                    <div key={criterion.id} style={{ marginBottom: '10px' }}>
                        <label>{criterion.description}</label>
                        <div>
                            {[1, 2, 3, 4, 5].map(score => (
                            <button
                                key={score}
                                style={circleButtonStyle(score, criterion.id)}
                                onClick={() => handleScoreChange(criterion.id, score)}
                            >
                                {score}
                            </button>
                            ))}
                        </div>
                    </div>
                    ))}
                <button onClick={saveScores} style={submitButtonStyle}>Submit</button>
            </div>
        </div>
    );
  };
  
  export default Rubric;