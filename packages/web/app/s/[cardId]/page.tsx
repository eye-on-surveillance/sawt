import CardResponse from "@/components/CardResponse";
import Citation from "@/components/Citation";
import { ECardStatus, ECardType, ICard } from "@/lib/api";

export default function Card({ params }: { params: { cardId: string } }) {
  const { cardId } = params;
  const card: ICard = {
    id: "arstarst-3452345234-arstarstarstars",
    card_type: ECardType.QUERY_IN_DEPTH,
    title:
      "what is city council doing to address lack of opportunities for youth?",
    likes: 0,
    status: ECardStatus.PUBLIC,
    created_at: new Date(),
    responses: [
      {
        response:
          "The effectiveness of surveillance is a contentious issue according to the transcripts from the New Orleans City Council. A significant number of the constituents, who are opponents of the proposed Ord. 33639, argue that surveillance does not equate to safety. They cite the racist history of surveillance and the racial biases built into surveillance technologies, arguing that the use of these technologies decreases safety for Black and brown New Orleanians and erodes public trust.",
      },
      {
        response:
          "Critics also point to the potential for misuse of surveillance technologies, the violation of civil liberties, and the lack of transparency and oversight in how the technologies are used. They argue that the money spent on surveillance could be better used to address root problems of crime, such as lack of affordable housing, job training programs, and other social services.",
      },
      {
        response:
          "On the other hand, there are proponents who argue for the implementation of 'facial recognition' by surveillance, particularly in light of increased crime in the city. They believe that surveillance can assist in the reduction of unlawful activity in communities. They point out that many homes, businesses, and public places already employ monitoring devices for security purposes.",
      },
      {
        response:
          "However, even among the proponents, there is acknowledgment of potential privacy concerns. Overall, the transcripts suggest that the views on the effectiveness of surveillance are divided, with significant concerns about racial bias, civil liberties, and misuse of technology on one hand, and a belief in its potential to deter crime on the other.",
      },
    ],
    citations: [
      {
        source_title: "Criminal Justice City Council Meeting 4/12/2022",
        source_publish_date: "6/22/2022",
        source_name:
          "Criminal Justice City Council Committee Meeting 4-12-2022.json",
      },
      {
        source_title: "Regular City Council Meeting 7/21/2023",
        source_publish_date: "7/21/2023",
        source_name: "Regular City Council Meeting 7-21-2022.json",
      },
      {
        source_title: "Criminal Justice City Council Meeting 6/15/2022",
        source_publish_date: "6/15/2022",
        source_name:
          "Criminal Justice City Council Committee Meeting 6-15-2022.json",
      },
      {
        source_title: "Criminal Justice City Council Meeting 6/15/2022",
        source_publish_date: "6/15/2022",
        source_name:
          "Criminal Justice City Council Committee Meeting 6-15-2022.json",
      },
    ],
    // Only used client-side, because there aren't userIds for ownership
    is_mine: true,
  };

  return (
    <div className="px-6 py-5 text-left sm:px-16 md:flex">
      <div className="md:grow"></div>
      <div className="md:w-3/4 md:max-w-2xl">
        <div className="my-5">
          <h1 className="text-2xl">{card.title}</h1>
          <h1 className="text-sm">{card.created_at?.toString()}</h1>
        </div>

        {card.responses!.map((response, index) => (
          <CardResponse response={response} key={index} />
        ))}
        <div className="text-sm">
          {card.citations!.map((citation, index) => (
            <Citation citation={citation} index={index} key={index} />
          ))}
        </div>
      </div>
      <div className="md:grow"></div>
    </div>
  );
}
