import { getPageMetadata } from "@/lib/paths";
import React from "react";
import styles from "./step.module.scss";

const Step = ({ title, text }: { title: string; text: string }) => {
  return (
    <div className="rounded border-2 border-solid border-purple px-3 py-5">
      <h3 className="text-lg font-bold">{title}</h3>
      <p>{text}</p>
    </div>
  );
};

export const metadata = getPageMetadata("Tips");

const TipsPage: React.FC = () => {
  return (
    <div className={styles["step-content"]}>
      <div className="min-h-[85vh] px-6 text-primary md:flex">
        <div className="md:grow"></div>
        <div className="pb-24 md:w-3/4 md:max-w-2xl">
          <section className="space-y-4">
            <h2 className="text-xl font-bold">
              I’m not quite sure how to use this app. What kinds of questions
              can I ask?
            </h2>
            <p>
              Think about the kinds of topics that are covered during City
              Council meetings, and the different people who speak. This
              includes councilmembers, mayoral staff, public agency
              representatives, activists, and other civic actors. Instead of
              watching many hours of City Council recordings to find out what
              has been said about a topic, use this app to do that search for
              you in fewer than 60 seconds!
            </p>

            <h2 className="text-xl font-bold">
              We suggest building questions around the following:
            </h2>
            <ul className="m-2 list-inside list-disc">
              <li>
                A particular topic, technology, policy, or issue that you’d like
                to find out about – e.g., surveillance, incarceration, criminal
                justice reform, crime cameras, etc.
              </li>
              <li>
                AND a particular person, agency, or other stakeholder that may
                have reported data, findings, questions, or concerns in relation
                to that topic – e.g., NOPD, City Council, the Mayor.
              </li>
              <li>
                For example, you could ask: “What data does NOPD have to show
                the effectiveness of crime cameras in New Orleans?”
              </li>
              <li>
                Or you could ask: “What is City Council doing to address racial
                inequality in the criminal justice system?”
              </li>
              <li>
                Visit the homepage to see questions asked by other people and
                organizations, and also case studies on how results were used.
              </li>
            </ul>
            <p>
              The app is in development – feel free to use it for asking
              different kinds of questions, and this will help EOS improve the
              app and make it more useful.
            </p>
          </section>
        </div>
        <div className="md:grow"></div>
      </div>
    </div>
  );
};

export default TipsPage;
