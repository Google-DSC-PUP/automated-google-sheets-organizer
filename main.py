import gspread
import pandas as pd
import os
import warnings


warnings.filterwarnings("ignore")
gc = gspread.oauth()
MAIN_SPREADSHEET_ID = os.environ.get("MAIN_SPREADSHEET_ID")


sh = gc.open_by_key(MAIN_SPREADSHEET_ID)
worksheet = sh.sheet1


df = pd.DataFrame(worksheet.get_all_records())
drop_col = [0, 1, 4, 5, 6, 7, 12, 16, 17, 18, 19]
df.drop(df.columns[drop_col], axis=1, inplace=True)
df.columns = ['first_name', 'last_name', 'program', 'year_and_block', 'tech_team', 'reason_joining_team', 'application_link', 'resource_links', 'additional_message']
df['ID'] = range(1, len(df) + 1)


for team in df['tech_team'].unique():
    tech_df = df[df['tech_team'] == team]
    tech_df_video = tech_df[tech_df['application_link'] != '']
    tech_df_video.dropna(subset=['application_link'])

    sh = gc.open(f"{team} Applicants")

    ws_applicants = sh.get_worksheet(1)
    ws_applicants.clear()
    ws_applicants.update(range_name="A:J", values=[df.columns.values.tolist()] + tech_df.values.tolist())

    ws_vid = sh.get_worksheet(0)
    curr_app_vid_df = pd.DataFrame(ws_vid.get_all_records())
    curr_app_vid_df.drop(df.columns[[0,1]], axis=1, inplace=True)
    filtered_df = tech_df_video[~tech_df_video['ID'].isin(curr_app_vid_df['ID'])]
    
    print(f"on {team}")
    if not filtered_df.empty:
        cell_list = ws_vid.findall(team)
        lowest_row = cell_list[-1].row
        ws_vid.update(range_name=f"C{lowest_row+1}:L{lowest_row+200}", values=filtered_df.values.tolist())
        print(f"Appended {len(filtered_df)} new responses")
    else:
        print("Found zero reponses.")
    print()
