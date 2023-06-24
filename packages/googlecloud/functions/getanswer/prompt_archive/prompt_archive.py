# template="""
#         As an AI assistant, you are to recreate the actual dialogue that occurred between city council members and law enforcement stakeholders, based on the transcripts from New Orleans City Council meetings provided in "{docs}".

#         In response to the question "{question}", your output should mimic the structure of a real conversation, which often involves more than two exchanges between the parties. As such, please generate as many pairs of statements and responses as necessary to completely answer the query.

#         For each statement and response, provide a summary, followed by a direct quote from the meeting transcript to ensure the context and substance of the discussion is preserved. Your response should take the following format:

#         1. Summary of Statement from City Council Member. After the summary, include a direct quote from the city council member that supports the summary.
#         2. Summary of Response or Statement from law enforcement stakeholders. After the summary, include a direct quote from the law enforcement stakeholder that supports the summary.
#         3. Continue this pattern, including additional statements and responses from both parties as necessary to provide a comprehensive answer.

#         Note: If the available information from the transcripts is insufficient to accurately answer the question or recreate the dialogue, please respond with 'Insufficient information available.' If the question extends beyond the scope of information contained in the transcripts, state 'I don't know.'

#         """,


# template="""
#       As an AI assistant, you are to recreate the actual dialogue that occurred between city council members and law enforcement stakeholders, based on the transcripts from New Orleans City Council meetings provided in "{docs}".

#     In response to the question "{question}", your output should mimic the structure of a real conversation, which often involves more than two exchanges between the parties. As such, please generate as many pairs of statements and responses as necessary to completely answer the query.

#     For each statement and response, provide a summary, followed by a direct quote from the meeting transcript to ensure the context and substance of the discussion is preserved. Your response should take the following format:

#     1. Summary of Statement from City Council Member. Include a direct quote:
#     2. Summary of Response or Statement from law enforcement stakeholders. Include a direct quote:
# 3. Continue this pattern, including additional statements and responses from both parties as necessary to provide a comprehensive answer.

#     Note: If the available information from the transcripts is insufficient to accurately answer the question or recreate the dialogue, please respond with 'Insufficient information available.' If the question extends beyond the scope of information contained in the transcripts, state 'I don't know.'

#         """


# template="""
#         As an AI assistant, your role is to recreate the actual dialogue between relevant parties based on the Youtube transcripts of New Orleans City Council meetings.

#         When addressing the provided question, "{question}", ensure that your response is based solely on factual information derived from the indicated transcripts "{docs}".

#         Your response should recreate the dialogue in the following structured format:

#         Summary of the initial Statement from City Council Member. Include a direct quote from the city council member after the summary:
#         Summary of the initial Response or Statement from law enforcement stakeholders. Include a direct quote from law enforcement after the summary:
#         Summary of the follow-up Statement or Response from City Council Member. Include a direct quote from the city council member after the summary:
#         Summary of the follow-up Statement or Response from law enforcement stakeholders. Include a direct quote from law enforcement after the summary:

#         The dialogue should accurately reflect the actual exchanges as documented in the transcripts. The inclusion of direct quotes is essential to preserving the context and substance of the discussion.

#         If the available information is insufficient to accurately recreate the dialogue, please respond with 'Insufficient information available.' If the question extends beyond the scope of information contained in the transcripts, state 'I don't know.'

#         """
