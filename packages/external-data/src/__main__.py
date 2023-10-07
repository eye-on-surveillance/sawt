import os
from news_extractor import url_to_json_selenium
import json

def main():
    # Predefined list of URLs
    url_list = [
        'https://www.nola.com/news/politics/how-should-new-orleans-spend-millions-of-one-time-funds-new-debate-begins/article_ef36af06-d320-11ed-b9fe-978f03c2909b.html',
        "https://www.wdsu.com/article/new-orleans-mayor-latoya-cantrell-consent-decree-hearing-jeffrey-vappie/44951427",
        "https://www.nola.com/news/crime_police/judge-offers-no-ruling-on-citys-motion-to-exit-consent-decree/article_1871f7dc-15c9-11ee-ad6c-afaeccd8e9dc.html",
        "https://www.wwltv.com/article/news/local/they-cannot-keep-up-nopd-chief-nominee-anne-kirkpatrick-weighs-in-on-staffing-and-consent-decree/289-0beaa1e4-b91f-42ab-bd6b-c69428601e1a",
        "https://www.nola.com/news/environment/new-orleans-prepares-for-three-months-of-salt-intrusion/article_03452ac2-5d64-11ee-ba66-2fb982d2b7c1.html",
        "https://lailluminator.com/2023/07/28/new-orleans-police-use-of-facial-recognition-nets-zero-arrests-in-9-months/",
        "https://lailluminator.com/2023/06/03/theyre-guzzlers-new-orleans-ignores-clean-fleet-law-during-50-million-vehicle-buying-spree/",
        "https://thelensnola.org/2022/12/02/council-approves-2023-budget-with-surprise-addition-of-124m-in-federal-coronavirus-relief-spending/",
        "https://www.fox8live.com/video/2023/03/15/city-council-questions-911-call-center-director-tyrell-morris-over-life-threatening-failures/",
        "https://www.nola.com/news/politics/swb-needs-major-changes-to-avoid-more-failures-bgr-says/article_1d13e9c8-f50b-11ed-9c45-67da1c67c50c.html",
        "https://lailluminator.com/2023/02/18/frequent-outages-could-lead-to-big-fines-for-entergy-new-orleans-under-new-standards/",
        "https://www.nola.com/news/business/new-orleans-city-council-agrees-to-audit-entergy-management-after-series-of-failures/article_aea2bd02-865d-11eb-a4dc-4ff26eb0bf9e.html",
        "https://www.nola.com/gambit/news/the_latest/no-excuses-frustrated-council-members-press-richard-s-disposal-over-garbage-failures/article_e62546c4-8df8-11ed-bab6-2b43058e872b.html",
        "https://www.fox8live.com/2023/05/23/entergy-again-sues-new-orleans-city-council-over-1-million-reliability-fine/",


    ]

    # Ensure the output directory exists
    output_dir = "../../backend/src/news_directory"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Loop over the URLs and call url_to_json for each
    for url in url_list:
        data = url_to_json_selenium(url)

        # Construct filename using title
        sanitized_title = data['messages'][0]['title'].replace(" ", "_").replace("/", "-").replace("?", "")
        filename = f"{sanitized_title}.json"
        filename = os.path.join(output_dir, filename)

        with open(filename, 'w') as f:
            f.write(json.dumps(data, indent=4))

if __name__ == "__main__":
    main()
