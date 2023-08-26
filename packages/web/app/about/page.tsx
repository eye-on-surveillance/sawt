import Link from "next/link";
import React from "react";

const Step = ({ title, text }: { title: string; text: string }) => {
  return (
    <div className="rounded border-2 border-solid border-purple px-3 py-5">
      <h3 className="text-lg font-bold">{title}</h3>
      <p>{text}</p>
    </div>
  );
};

const AboutPage: React.FC = () => {
  return (
    <div className="bg-blue px-6 text-primary md:flex">
      <div className="md:grow"></div>
      <div className="pb-24 md:w-3/4 md:max-w-2xl">
        <section className="space-y-4">
          <h2 className="text-2xl font-bold">About Sawt</h2>
          <p>
            <Link
              href="https://eyeonsurveillance.org"
              className="text-secondary"
            >
              Eye on Surveillance
            </Link>{" "}
            created SAWT as a tool for New Orleanians to more easily find out
            what is being shared and discussed in City Council meetings. The app
            uses advanced language modeling, a form of artificial intelligence,
            to:
          </p>
          <ol className="m-2 list-inside list-decimal">
            <li>
              Create transcripts of all City Council meetings from 2023_ to
              Present.
            </li>
            <li>
              When you ask SAWT a question, the app searches through those
              transcripts to find any instances when somebody said something
              relevant to your query.
            </li>
            <li>
              The results (a summary as well as direct quotes) then show up in
              the SAWT feed, where you can also see other queries and results.
            </li>
          </ol>
          <h2 className="text-2xl font-bold">How Sawt works</h2>
          <div className="grid grid-flow-row auto-rows-max gap-3 text-purple sm:grid-cols-1 md:grid-cols-3">
            <Step
              title="Step 1"
              text="Turn YouTube videos of city council meetings into written transcripts"
            />
            <Step
              title="Step 2"
              text="Take your question and search the written transcripts"
            />
            <Step
              title="Step 3"
              text="Compile the results for you to view and share"
            />
          </div>
          <h2 className="text-2xl font-bold">About the results</h2>
          <p>
            The results are produced from AI-generated transcripts of City
            Council meetings and records. There may be inaccuracies in the
            transcriptions, and there may be other relevant data available in
            the original source materials not uncovered by SAWT. There may also
            be inaccuracies in what is stated or presented during a City Council
            meeting – SAWT is not a fact checker.
          </p>
          <p>
            The results provided by SAWT are great starting points for further
            research and exploration, and you’ll want to fact check any
            information and figures that you might use for informational,
            research, and advocacy purposes. Here are some follow-up steps that
            you could take:
          </p>
          <ul className="m-2 list-inside list-disc">
            <li>
              Look at the metadata for your SAWT results to understand when,
              who, and where something was shared or stated in the course of a
              meeting.
            </li>
            <li>
              Watch the City Council meeting recording to understand the context
              within which something was said.
            </li>
            <li>
              Follow up with the speaker and/or file a public records request to
              find official records and documentation in regards to a particular
              topic.
            </li>
            <li>
              Verify and contextualize SAWT results with other sources of data,
              such as news reports, civic organization and monitor reports and
              analysis, etc.
            </li>
          </ul>
        </section>
      </div>
      <div className="md:grow"></div>
    </div>
  );
};

export default AboutPage;
