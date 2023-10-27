const ThreeCardLayout = ({ cards }) => {
    return (
      <div className="flex justify-center mt-10 space-x-4">
        {cards && cards.map((card, index) => (
          <div key={index} className="flex-none w-1/4 bg-white p-6 rounded shadow hover:bg-gray-100 active:bg-gray-200 transition">
            {card.content}
          </div>
        ))}
      </div>
    );
  };