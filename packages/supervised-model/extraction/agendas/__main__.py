import agendas

if __name__ == "__main__":
    df = agendas.process_docx_files('../../../backend/src/minutes_agendas_directory/agendas')
    df.to_excel('output/ordinances_test.xlsx', index=False)
