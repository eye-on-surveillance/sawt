import pandas as pd
import re
import ast
import numpy as np
import csv


def parse_motions(text):
    if not isinstance(text, str):
        return []

    title_re = re.compile(
        r"(AMENDMENT TO ORDINANCE|MOTION|RESOLUTION) ?-? ?(NO\.)? ?([A-Z0-9\-]+\,?[A-Z0-9\-]?) - BY: (.*)"
    )
    action_re = re.compile(
        r"(ACTION:\n)(Amendment|As Amended|Adopt|Enter Executive Session)"
    )
    brief_re = re.compile(r"Brief:\n(.*)(?=Annotation:)", re.DOTALL)
    annotation_re = re.compile(r"Annotation:\n(.*)")
    moved_by_re = re.compile(r"MOVED BY:\n(.*)")
    seconded_by_re = re.compile(r"SECONDED BY:\n(.*)")
    votes_re = re.compile(r"(.*?)(?: - \d+)?\n(YEAS|NAYS|ABSTAIN|ABSENT|RECUSED):")
    motion_passed_re = re.compile(r"AND THE MOTION (PASSED|FAILED).")
    withdrawn_re = re.compile(r"WITHDRAWN.")

    motion_blocks = re.split(r"(AND THE MOTION (PASSED|FAILED).\n|WITHDRAWN.\n)", text)

    parsed_list = []

    for block in motion_blocks:
        if not isinstance(block, str):
            continue

        matches = list(title_re.finditer(block))
        for i, title_match in enumerate(matches):
            parsed = {"motionDetails": {}}

            parsed["motionDetails"]["title"] = (
                title_match.group(1) + " " + title_match.group(3)
            )
            parsed["motionDetails"]["proposedBy"] = title_match.group(4)

            action_match = action_re.search(block, pos=title_match.end())
            if action_match:
                parsed["motionDetails"]["action"] = action_match.group(2)

            brief_match = brief_re.search(block, pos=title_match.end())
            if brief_match:
                parsed["motionDetails"]["brief"] = brief_match.group(1).strip()

            annotation_match = annotation_re.search(block, pos=title_match.end())
            if annotation_match:
                parsed["motionDetails"]["annotation"] = annotation_match.group(1)

            moved_by_match = moved_by_re.search(block, pos=title_match.end())
            if moved_by_match:
                parsed["motionDetails"]["movedBy"] = moved_by_match.group(1)

            seconded_by_match = seconded_by_re.search(
                block, pos=(moved_by_match.end() if moved_by_match else 0)
            )
            if seconded_by_match:
                parsed["motionDetails"]["secondedBy"] = seconded_by_match.group(1)

            parsed["motionDetails"]["votingDetails"] = {}

            for votes_match in votes_re.finditer(
                block, pos=(seconded_by_match.end() if seconded_by_match else 0)
            ):
                vote_type = votes_match.group(2).lower()
                members = votes_match.group(1).split(",")
                for member in members:
                    parsed["motionDetails"]["votingDetails"][member.strip()] = vote_type

            motion_passed_match = motion_passed_re.search(
                block, pos=(seconded_by_match.end() if seconded_by_match else 0)
            )
            if motion_passed_match:
                parsed["motionDetails"]["motionPassed"] = (
                    True if motion_passed_match.group(1) == "PASSED" else False
                )

            withdrawn_match = withdrawn_re.search(
                block, pos=(seconded_by_match.end() if seconded_by_match else 0)
            )
            if withdrawn_match:
                parsed["motionDetails"]["withdrawn"] = True

            if parsed["motionDetails"]["votingDetails"]:
                parsed_list.append(parsed)

    return parsed_list


def parse_text_cal(text):
    if not isinstance(text, str):
        return []

    text = re.sub(
        r"https://cityofno\.granicus\.com/MinutesViewer[^\s\n]*",
        "",
        text,
        flags=re.MULTILINE,
    )

    title_re = re.compile(
        r"(CAL\. NO\.) ?-? ?([A-Z0-9,\- ]+)(?:- BY: (.*?))(?: \(BYREQUEST\))?(?=Brief:|\\n|$)",
        re.DOTALL,
    )
    action_re = re.compile(
        r"(ACTION:\n)(Amendment|As Amended|Adopt|Enter Executive Session)"
    )
    brief_re = re.compile(r"Brief:\n(.*?)(?=Annotation:)", re.DOTALL)
    annotation_re = re.compile(r"Annotation:\n(.*)")
    moved_by_re = re.compile(r"MOVED BY:\n(.*)")
    seconded_by_re = re.compile(r"SECONDED BY:\n(.*)")
    votes_re = re.compile(
        r"(([\w\s,]+)(?: - \d+)?)?\n(YEAS|NAYS|ABSTAIN|ABSENT|RECUSED):"
    )
    motion_passed_re = re.compile(r"AND THE MOTION (PASSED|FAILED).")
    withdrawn_re = re.compile(r"WITHDRAWN.")

    motion_blocks = re.split(r"(AND THE MOTION (PASSED|FAILED).\n|WITHDRAWN.\n)", text)

    parsed_list = []

    for block in motion_blocks:
        if not isinstance(block, str):
            continue

        matches = list(title_re.finditer(block))
        for i, title_match in enumerate(matches):
            parsed = {"motionDetails": {}}

            parsed["motionDetails"]["title"] = (
                title_match.group(1) + " " + title_match.group(2)
            )
            proposedBy = title_match.group(3)
            if proposedBy:
                proposedBy = (
                    proposedBy.replace("\n", " ").replace("(BYREQUEST)", "").strip()
                )
            parsed["motionDetails"]["proposedBy"] = proposedBy

            action_match = action_re.search(block, pos=title_match.end())
            if action_match:
                parsed["motionDetails"]["action"] = action_match.group(2)

            brief_match = brief_re.search(block, pos=title_match.end())
            if brief_match:
                parsed["motionDetails"]["brief"] = brief_match.group(1).strip()

            annotation_match = annotation_re.search(block, pos=title_match.end())
            if annotation_match:
                parsed["motionDetails"]["annotation"] = annotation_match.group(1)

            moved_by_match = moved_by_re.search(block, pos=title_match.end())
            if moved_by_match:
                parsed["motionDetails"]["movedBy"] = moved_by_match.group(1)

            seconded_by_match = seconded_by_re.search(
                block, pos=(moved_by_match.end() if moved_by_match else 0)
            )
            if seconded_by_match:
                parsed["motionDetails"]["secondedBy"] = seconded_by_match.group(1)

            parsed["motionDetails"]["votingDetails"] = {}

            for votes_match in votes_re.finditer(
                block, pos=(seconded_by_match.end() if seconded_by_match else 0)
            ):
                vote_type = votes_match.group(3).lower()
                members = (
                    votes_match.group(2).split(", ") if votes_match.group(2) else ["0"]
                )
                for member in members:
                    member = member.strip()
                    if member and member != "0":
                        member = member.replace("\n", "")
                        parsed["motionDetails"]["votingDetails"][member] = vote_type

            motion_passed_match = motion_passed_re.search(
                block, pos=(seconded_by_match.end() if seconded_by_match else 0)
            )
            if motion_passed_match:
                parsed["motionDetails"]["motionPassed"] = (
                    True if motion_passed_match.group(1) == "PASSED" else False
                )

            withdrawn_match = withdrawn_re.search(
                block, pos=(seconded_by_match.end() if seconded_by_match else 0)
            )
            if withdrawn_match:
                parsed["motionDetails"]["withdrawn"] = True

            if parsed["motionDetails"]["votingDetails"]:
                parsed_list.append(parsed)

    return parsed_list


votes = ["yeas", "nays", "recused", "abstain", "absent"]


def dict_to_df(row):
    if pd.isnull(row):
        return pd.DataFrame(
            {
                "title": [np.nan],
                "proposedBy": [np.nan],
                "action": [np.nan],
                "brief": [np.nan],
                "annotation": [np.nan],
                "movedBy": [np.nan],
                "council_member": [None],
                "vote": ["Not available"],
            }
        )

    if isinstance(row, str):
        dict_data = ast.literal_eval(row)
    else:
        dict_data = row

    motion_data = dict_data["motionDetails"].copy()
    voting_details = motion_data.pop("votingDetails", {})
    motion_df = pd.json_normalize(motion_data)

    voting_data = []
    for member, vote in voting_details.items():
        if vote.lower() in votes:
            voting_data.append({"council_member": member, "vote": vote})

    if not voting_data:
        voting_data.append({"council_member": None, "vote": "Not available"})

    voting_df = pd.DataFrame(voting_data)

    df = pd.concat([motion_df] * len(voting_df), ignore_index=True)
    df = pd.concat([df, voting_df], axis=1)

    return df
