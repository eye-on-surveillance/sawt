import pandas as pd
from parse_text import (
    parse_motions,
    parse_text_cal,
    dict_to_df,
    read_json_files,
    clean_votes,
    clean_ordinances,
)
import json
import os


def process_json_file(json_file_path):
    with open(json_file_path, "r") as f:
        data = json.load(f)
        messages = data.get("messages", {})

        dfs = []  # List to hold DataFrames
        for _, message in messages.items():
            parsed_motions = parse_motions(message)
            for parsed in parsed_motions:
                df = dict_to_df(
                    parsed, os.path.basename(json_file_path)
                )  # Pass only the filename
                dfs.append(df)

            parsed_cal = parse_text_cal(message)
            for parsed in parsed_cal:
                df = dict_to_df(
                    parsed, os.path.basename(json_file_path)
                )  # Pass only the filename
                dfs.append(df)

        return dfs


if __name__ == "__main__":
    directory = "../../ocr/output/json"

    all_dfs = []  # List to hold all DataFrames from all JSON files
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            json_file_path = os.path.join(directory, filename)
            dfs_from_file = process_json_file(json_file_path)
            all_dfs.extend(dfs_from_file)

    # Concatenate all DataFrames into one
    final_df = pd.concat(all_dfs, ignore_index=True)

    # Process the final_df
    final_df = final_df.rename(columns={"title": "ordinance", "brief": "summary"})
    final_df.loc[:, "votes"] = final_df.council_member.str.cat(final_df.vote, sep=" - ")
    final_df = final_df.drop(
        columns=[
            "movedBy",
            "proposedBy",
            "action",
            "annotation",
            "secondedBy",
            "council_member",
            "vote",
        ]
    )
    final_df["votes"] = final_df["votes"].fillna("").apply(clean_votes)
    final_df = final_df.pipe(clean_ordinances)

    # Save to CSV
    final_df.to_csv("output/parsed_voting_rolls.csv", index=False)
