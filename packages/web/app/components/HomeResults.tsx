import { EResponseType, ICard } from "@/lib/api";
import QueryResult from "./QueryResult";

const results: ICard[] = [
  {
    id: "1",
    card_type: EResponseType.RESPONSE_TYPE_DEPTH,
    title: "Tell me about bus rapid transit",
    responses: [
      {
        response:
          "Bus Rapid Transit (BRT) is a type of public transportation system that aims to provide fast, efficient, and reliable commuting options. The New Orleans City Council is considering a BRT proposal that would revamp the RTA Park and Ride lot on Wall Boulevard, turning it into the West Bank Terminus for this route of the RTA BRT's West Corridor project.",
      },
    ],
    created_at: new Date(),
    likes: 23,
  },
  {
    id: "2",
    card_type: EResponseType.RESPONSE_TYPE_DEPTH,
    title: "what has helena moreno done about climate change",
    responses: [
      {
        response:
          "Council Member Helena Moreno has taken various actions to address climate change in New Orleans. She has been part of creating sustainable plans, promoting economic growth, and endorsing projects that focus on the environment.",
      },
    ],
    created_at: new Date(1650000000000),
    likes: 0,
  },
  {
    id: "3",
    card_type: EResponseType.RESPONSE_TYPE_DEPTH,
    title: "What is a proviso?",
    responses: [
      {
        response:
          "A proviso, as mentioned in the transcripts, appears to be a stipulation or condition attached to an ordinance, motion, or proposal that the council is considering. It seems to be a sort of amendment or additional clause which sets specific terms or conditions that must be met. In the context of the City Council of New Orleans' meeting, a proviso was recommended by the commission to limit events to occur only when the school is not in session. This suggests that a proviso is used to provide specific guidelines or restrictions that govern how an ordinance or law is to be applied. It is a tool used to ensure that the intent of the law is preserved and to prevent potential misuse or misinterpretation. The specific nature and impact of a proviso likely vary based on the context and the specific legislation it is attached to.",
      },
    ],
    created_at: new Date(1640000000000),
    likes: 1,
  },
];

export default function HomeBanner() {
  return (
    <div className="min-h-[40vh] w-screen bg-indigo-800 px-6 py-12 sm:px-16">
      {results.map((card) => (
        <QueryResult key={card.id} card={card} />
      ))}
    </div>
  );
}
