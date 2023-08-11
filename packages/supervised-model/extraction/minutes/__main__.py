import pandas as pd
from parse_text import parse_motions, parse_text_cal, dict_to_df, read_json_files

if __name__ == "__main__":
    # Reading data from JSON files
    all_data = read_json_files("../../ocr/output/json")

    dfa_list, dfb_list = [], []
    for data in all_data:
        dfa_temp = {"text": data}
        dfa_temp["parsed_text"] = parse_motions(data)
        dfa_list.append(dfa_temp)

        dfb_temp = {"text": data}
        dfb_temp["parsed_text"] = parse_text_cal(data)
        dfb_list.append(dfb_temp)

    dfa = pd.DataFrame(dfa_list).explode("parsed_text").reset_index(drop=True)
    dfb = pd.DataFrame(dfb_list).explode("parsed_text").reset_index(drop=True)

    dfc = pd.concat([dfa, dfb])

    df_new = pd.concat(dfc["parsed_text"].apply(dict_to_df).tolist(), ignore_index=True)
    df_new = df_new.drop(
        columns=["movedBy", "proposedBy", "action", "annotation", "secondedBy"]
    )
    df_new.to_csv("output/parsed_voting_rolls.csv", index=False)
