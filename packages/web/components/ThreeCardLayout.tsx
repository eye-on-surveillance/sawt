"use client";



export default function ThreeCardLayout({ cards }) {

  return (
    <div className="flex justify-center mt-10 space-x-4">
      {cards && cards.map((card, index) => (
        <div key={index} className="flex-none w-1/4 bg-white p-6 rounded shadow hover:bg-gray-100 active:bg-gray-200 transition">
              {/* Card content goes here */}
          {card.response}


        </div>
      ))
      }
    </div>
  );




};
  


/*
            {card.responses}

export type ICard = {
  id?: string;
  card_type: ECardType;
  title: string;
  subtitle?: string;
  likes?: number;
  status?: ECardStatus;
  created_at?: Date;
  responses?: IResponse[];
  citations?: ICitation[];
  // Only used client-side, because there aren't userIds for ownership
  is_mine?: boolean;
  processing_time_ms?: number;
};

*/