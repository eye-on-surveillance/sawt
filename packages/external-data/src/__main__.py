import os
from news_extractor import url_to_json_selenium
import json
from concurrent.futures import ThreadPoolExecutor

MAX_WORKERS = 5


def process_url(url):
    try:
        data = url_to_json_selenium(url)
        if not data or not data["messages"][0]["title"]:
            # No title found, return the URL to be logged
            return url

        output_dir = "../../backend/src/news_directory"
        filename = f"{data['messages'][0]['title']}.json"
        filename = os.path.join(output_dir, filename)

        with open(filename, "w") as f:
            f.write(json.dumps(data, indent=4))
        return None  # No issues, so return None
    except Exception as e:
        print(f"Exception for URL {url}: {str(e)}")
        return url


def main():
    url_list = [
        # "https://www.nola.com/news/politics/how-should-new-orleans-spend-millions-of-one-time-funds-new-debate-begins/article_ef36af06-d320-11ed-b9fe-978f03c2909b.html",
        # "https://www.nola.com/news/crime_police/judge-offers-no-ruling-on-citys-motion-to-exit-consent-decree/article_1871f7dc-15c9-11ee-ad6c-afaeccd8e9dc.html",
        # "https://www.nola.com/news/environment/new-orleans-prepares-for-three-months-of-salt-intrusion/article_03452ac2-5d64-11ee-ba66-2fb982d2b7c1.html",
        "https://lailluminator.com/2023/07/28/new-orleans-police-use-of-facial-recognition-nets-zero-arrests-in-9-months/",
        # "https://lailluminator.com/2023/06/03/theyre-guzzlers-new-orleans-ignores-clean-fleet-law-during-50-million-vehicle-buying-spree/",
        # "https://thelensnola.org/2022/12/02/council-approves-2023-budget-with-surprise-addition-of-124m-in-federal-coronavirus-relief-spending/",
        # "https://www.fox8live.com/video/2023/03/15/city-council-questions-911-call-center-director-tyrell-morris-over-life-threatening-failures/",
        # "https://www.nola.com/news/politics/swb-needs-major-changes-to-avoid-more-failures-bgr-says/article_1d13e9c8-f50b-11ed-9c45-67da1c67c50c.html",
        # "https://lailluminator.com/2023/02/18/frequent-outages-could-lead-to-big-fines-for-entergy-new-orleans-under-new-standards/",
        # "https://www.nola.com/gambit/news/the_latest/no-excuses-frustrated-council-members-press-richard-s-disposal-over-garbage-failures/article_e62546c4-8df8-11ed-bab6-2b43058e872b.html",
        # "https://www.wdsu.com/article/new-orleans-council-members-consent-decree-mayor-concerns/43556031",
        # "https://fightbacknews.org/articles/city-new-orleans-attempts-exit-consent-decree-protesters-demand-community-control-police",
        # "https://www.nola.com/news/politics/council-tables-plan-to-bar-food-distribution-to-homeless/article_1ba8e916-2a40-11ee-bcb2-dbfdb794bc4f.html",
        # "https://www.wwno.org/news/2023-07-13/meeting-on-controversial-new-orleans-jail-project-draws-passionate-comments-and-a-heated-exchange",
        # "https://www.wwltv.com/article/news/local/orleans/new-orleans-affordable-housing-city-council-32-million/289-7516fd45-2562-4414-94eb-2c46e810515c",
        # "https://www.nola.com/news/politics/new-orleans-swb-floats-rolling-forward-tax-rate/article_a6ce3f46-6474-11ee-b72f-b7a906a8f9ef.html",
        # "https://www.wwno.org/news/2023-04-04/advocates-to-city-council-spend-covid-aid-surplus-dollars-on-housing-and-youth-development",
        # "https://www.nola.com/news/politics/cantrell-administration-should-boost-transparency-on-388-million-in-federal-funds-bgr-says/article_6b591a1a-7d7c-11ed-b58f-0371d99e2538.html",
        "https://www.nola.com/louisiana_inspired/operation-restoration-gives-women-in-prison-health-care-path/article_a7d64b56-6081-11ed-8509-57a5911972bf.html",
        "https://lailluminator.com/2023/06/02/zombie-bill-to-ban-trans-youth-healthcare-advances-from-louisiana-senate-committee/",
        "https://kresge.org/news-views/qa-jane-place-neighborhood-sustainability-initiative-chief-on-increasing-housing-security/",
        "https://www.buzzfeednews.com/article/nidhisubbaraman/new-orleans-lead-water-hidden-report",
        "https://antigravitymagazine.com/column/new-orleans-has-a-long-history-of-street-vending-and-crackdowns-how-do-we-stop-this-cycle/",
        "https://www.nola.com/louisiana_inspired/meeting-people-where-they-are-how-a-new-orleans-group-is-addressing-youth-crime/article_13c74dca-a70d-11ed-9d8f-9b9d4dc1239f.html",
        "https://lailluminator.com/2023/11/02/entergy-bills/",
        "https://www.nola.com/news/politics/at-lincoln-beach-volunteer-caretakers-plead-for-help-from-new-orleans-city-hall/article_2cd4c6e4-2b98-11ed-b0b7-1b46c1cb095d.html",
        
    ]

    output_dir = "../../backend/src/news_directory"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        failed_urls = list(filter(None, executor.map(process_url, url_list)))

    with open(os.path.join(output_dir, "failed_urls.log"), "w") as log_file:
        for failed_url in failed_urls:
            log_file.write(f"{failed_url}\n")


if __name__ == "__main__":
    main()
