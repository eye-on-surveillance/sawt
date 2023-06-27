import React from "react";

const AboutPage: React.FC = () => {
  return (
    <section className="space-y-4 p-6">
      <h2 className="text-2xl font-bold">About The Great Inquirer</h2>
      <p>
        Welcome to the Great New Orleanian Inquirer—a revolution in how you
        interact with your city council representatives. By harnessing the power
        of advanced language modeling, we&apos;ve created a platform that
        provides a seamless and trustworthy source of information. Our extensive
        database, drawn from the transcripts, minutes, and agendas of city
        council meetings, provides the bedrock of our service. No more digging
        through countless documents—now, all the critical details from these
        meetings are at your fingertips. Not just data, but knowledge—insights,
        clarifications, and contextual understanding made possible through our
        AI-powered analysis of these resources. With the Great New Orleanian
        Inquirer, you&apos;re not just getting answers, you&apos;re gaining a
        deeper understanding of your city&apos;s governance. Start your journey
        with us, and see how we&apos;re changing the face of citizen engagement.
      </p>
      <h2 className="text-2xl font-bold">Features</h2>
      <ul className="list-disc pl-5">
        <li>
          Comprehensive Answers: The Great Inquirer aims to provide accurate and
          comprehensive answers to user queries. Our AI assistant generates
          summaries of statements and responses from city council members and
          external stakeholders, accompanied by direct quotes from the meeting
          transcripts. We strive to preserve context and substance while
          addressing the questions posed by our users.
        </li>
        <li>
          Contextual Dialogue Recreation: Through our AI assistant, The Great
          Inquirer recreates the actual dialogue that took place during city
          council meetings. By analyzing transcripts and generating
          comprehensive statements and responses, we ensure that users receive a
          holistic understanding of the discussions and decisions made by
          council members and external stakeholders.
        </li>
        <li>
          Reliable Information: The Great Inquirer is founded on an extensive
          database of New Orleans&apos; City Council meetings. These meetings
          were meticulously sourced from the{" "}
          <a
            href="https://www.youtube.com/@neworleanscitycouncil488"
            target="_blank"
            rel="noopener noreferrer"
          >
            City Council&apos;s YouTube channel
          </a>
          , coupled with the minutes and agendas gathered from the{" "}
          <a
            href="https://council.nola.gov/meetings/"
            target="_blank"
            rel="noopener noreferrer"
          >
            New Orleans City Council&apos;s website
          </a>
          . This dual-source approach guarantees the provision of authentic and
          reliable information.
        </li>
      </ul>
      <p>
        We are continuously working to improve and expand The Great
        Inquirer&apos;s capabilities, with a focus on enhancing user experience,
        incorporating user feedback, and expanding the coverage of available
        information. Our vision is to foster a vibrant and engaged community
        that actively participates in the decision-making processes that shape
        the city of New Orleans.
      </p>
      <p>
        Join The Great Inquirer today and be part of the conversation that
        shapes your community&apos;s future. Together, we can make a difference.
      </p>
      <p>
        Note: The Great Inquirer is currently a work in progress, and we
        appreciate your patience and support as we strive to deliver the best
        possible experience for our users.
      </p>
    </section>
  );
};

export default AboutPage;
