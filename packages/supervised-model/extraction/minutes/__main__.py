import pandas as pd
from parse_text import parse_motions, parse_text_cal, dict_to_df

if __name__ == "__main__":
    df = pd.read_csv("../../ocr/output/ocr_results.csv", encoding="latin1")

    dfa = df.copy()
    dfa["parsed_text"] = dfa["text"].apply(parse_motions)
    dfa = dfa.explode("parsed_text").reset_index(drop=True)

    dfb = df.copy()
    dfb["parsed_text"] = dfb["text"].apply(parse_text_cal)
    dfb = dfb.explode("parsed_text").reset_index(drop=True)
    
    dfc = pd.concat([dfa, dfb])

    df_new = pd.concat(dfc["parsed_text"].apply(dict_to_df).tolist(), ignore_index=True)
    df_new = df_new.drop(
        columns=["movedBy", "proposedBy", "action", "annotation", "secondedBy"]
    )
    df_new.to_csv("output/parsed_voting_rolls.csv", index=False)
