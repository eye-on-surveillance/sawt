

interface RubricProps {
  criteria: Array<{
      id: string;
      description: string;
  }>;
  scores: Record<string, number>;
  onScoreChange: (criterionId: string, score: number) => void;
}


const Rubric: React.FC<RubricProps> = ({ criteria, scores, onScoreChange }) => {    // This state will hold the scores for each criterion

  
  
  const circleButtonStyle = (score: number, criterionId: string) => ({
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
    
      const containerStyle: React.CSSProperties = {
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        flexDirection: 'column',
        padding: '20px',
      };

      return (
        <div style={containerStyle}>
            <div>
                {criteria.map(criterion => (
                    <div key={criterion.id} style={{ marginBottom: '10px' }}>
                        <label>{criterion.description}</label>
                        <div>
                            {[1, 2, 3, 4, 5].map(score => (
                            <button
                                key={score}
                                style={circleButtonStyle(score, criterion.id)}
                                onClick={() => onScoreChange(criterion.id, score)}
                              >
                                {score}
                            </button>
                            ))}
                        </div>
                    </div>
                    ))}
                {/* <button onClick={saveScores} style={submitButtonStyle}>Submit</button> */}
          {/* <button style={submitButtonStyle}>Submit</button> */}

            </div>
        </div>
    );
  };
  
  export default Rubric;