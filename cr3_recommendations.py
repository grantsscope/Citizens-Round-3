import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import re

st.set_page_config(layout='wide')
tcol1,tcol2,tcol3 = st.columns([1,3,1])

tcol2.image("https://grantsscope.xyz/wp-content/uploads/2024/04/bafybeibrcljtp3nqiowx7qng7fh2xkj23rnm6fbidqosdu5qxrtcudkkue-3.jpeg")
tcol2.title('Gitcoin Citizens Retro - Round 3')
tcol2.markdown('### Get one-click personalized grantee recommendations')

# Get address
address = tcol2.text_input('Enter your Ethereum address below (starting "0x"):', 
							help='ENS not supported, please enter 42-character hexadecimal address starting with "0x"')

# Convert to lower case for ease of comparison
address = address.lower()

if address and address != 'None':
        
        if not re.match(r'^(0x)?[0-9a-f]{40}$', address, flags=re.IGNORECASE):
            tcol2.error('Not a valid address. Please enter a valid 42-character hexadecimal Ethereum address starting with "0x"')
            my_bar.empty()
        else:

            # Load all donations data on Grants Stack
            gs_donations_df = pd.read_csv('gs_donations.csv')
            # Convert voter to lower case for ease of comparison
            gs_donations_df['Voter'] = gs_donations_df['Voter'].str.lower()
            gs_donations_df['PayoutAddress'] = gs_donations_df['PayoutAddress'].str.lower()

            #load the citizens round 3 projects
            cr3_df = pd.read_csv('summarized_cr3_projects.csv')
            # Convert Payout Address to lower case for ease of comparison
            cr3_df['PayoutAddress'] = cr3_df['PayoutAddress'].str.lower()
            cr3_df['Application Link'] = 'https://explorer-v1.gitcoin.co/#/round/42161/0x5aa255d5cae9b6ce0f2d9aee209cb02349b83731/' + cr3_df['ApplicationId'].astype(str)

            #Step 0: Find CR3 projects previously supported by user
            supported_by_user = gs_donations_df[gs_donations_df['Voter'] == address].drop_duplicates(subset=['PayoutAddress'])

            # Filter by those participating in CR3
            #filtered_supported_by_user = supported_by_user.merge(cr3_df['PayoutAddress'].drop_duplicates(), on='PayoutAddress', how='inner')
            
            filtered_supported_by_user = supported_by_user.merge(cr3_df[['PayoutAddress', 'Project Name', 'Application Link']].drop_duplicates(), 
                on='PayoutAddress', 
                how='inner',
                suffixes=('', '_cr3'))

            tcol2.markdown("filtered_supported_by_user")
            tcol2.dataframe(filtered_supported_by_user)

            filtered_supported_by_user.drop('Project Name', axis=1, inplace=True)
            filtered_supported_by_user.rename(columns={'Project Name_cr3': 'Project Name'}, inplace=True)

            # Results Display Code
            #matched_projects = filtered_supported_by_user.merge(cr3_df[['PayoutAddress', 'Project Name', 'Application Link']], 
            #                on='PayoutAddress', 
            #                how='inner',
            #                suffixes=('', '_cr3'))

            #matched_projects.drop('Project Name', axis=1, inplace=True)
            #matched_projects.rename(columns={'Project Name_cr3': 'Project Name'}, inplace=True)

            #tcol2.dataframe(matched_projects)    

            #matched_projects_df = matched_projects.groupby(['PayoutAddress', 'Project Name', 'Application Link']).agg({
            #    'AmountUSD': 'sum',                
            #    'Round Name': ', '.join  # Join the combined project-round strings
            #}).reset_index()

            matched_projects_df = filtered_supported_by_user.groupby(['PayoutAddress', 'Project Name', 'Application Link']).agg(
                {
                'AmountUSD': 'sum',  
                'Round Name': ', '.join  # Join the combined project-round strings              
                })

            tcol2.markdown("matched_projects_df")
            tcol2.dataframe(matched_projects_df, hide_index=True, use_container_width=True)

            tcol2.markdown("#### Who from the Retro Round you have contributed to before?")
            tcol2.markdown("Here are the projects whose payout address you have previously donated to. Show them some love again in this round!")
            
            tcol2.dataframe(matched_projects_df, hide_index=True, use_container_width=True,
                column_order=("Project Name", "Round Name", "Application Link"),   
                column_config = {
                    "Project Name": "Project Name",
                    "Round Name": "Previous Round(s) You Contributed to",
                    "Application Link": st.column_config.LinkColumn(label = "Application Detail", display_text = "Open Application")
                    #"AmountUSD": st.column_config.NumberColumn("Total Donations (in USD)", step = 1, format = "$%d")
                    } 
                )            


            #Step 1: Find top 5 grantees donated to by the user
            #top_addresses = gs_donations_df[gs_donations_df['Voter'] == address].groupby('PayoutAddress').agg({'AmountUSD': 'sum'}).reset_index().sort_values('AmountUSD', ascending=False).head(5)
            #top_projects = pd.merge(top_addresses, gs_donations_df[['PayoutAddress', 'Project Name']].drop_duplicates(), on='PayoutAddress', how='left')

            # Aggregate donations by PayoutAddress, Voter, and Round Name including the Project Name
            top_addresses_by_round = gs_donations_df[gs_donations_df['Voter'] == address].groupby(['PayoutAddress', 'Round Name']).agg({'AmountUSD': 'sum', 'Project Name': 'first'}).reset_index().sort_values('AmountUSD', ascending=False)

            # Now, get the top 5 addresses based on the summed AmountUSD
            top_addresses = top_addresses_by_round.groupby('PayoutAddress').agg(TotalAmountUSD=('AmountUSD', 'sum')).reset_index().sort_values('TotalAmountUSD', ascending=False).head(5)

            # Following section is for debugging and display
            # Merge back with top_addresses_by_round to get associated Round Names and Project Names for the top addresses
            top_projects = top_addresses.merge(top_addresses_by_round[['PayoutAddress', 'Round Name', 'Project Name', 'AmountUSD']], on='PayoutAddress', how='left')

            top_projects['ProjectRound'] = top_projects.apply(lambda x: f"{x['Project Name']} [{x['Round Name']}]", axis=1)

            # Grouping by 'PayoutAddress', summing 'AmountUSD', and joining the concatenated 'ProjectRound'
            top_projects_grouped_df = top_projects.groupby('PayoutAddress').agg({
                'AmountUSD': 'sum',  # Sum the amounts
                'ProjectRound': ', '.join  # Join the combined project-round strings
            }).reset_index()

            tcol2.markdown("#### Recommendations Based on Your Donation History")
            tcol2.caption("We scanned your entire donation history on Grants Stack through March 31st 2024 for Gitcoin Grants and Community Rounds. Here are your top 5 contributions based on the Payout Address you have contributed to:")
            tcol2.dataframe(top_projects_grouped_df, column_config = {
                "ProjectRound": "Project (Round) Donated to",
                "AmountUSD": st.column_config.NumberColumn("Total Donations (oin USD)", step = 1, format = "$%d")
                },
                column_order=("ProjectRound", "AmountUSD"),
                hide_index=True, use_container_width=True)            
            # End of debudding and display code

            #Step 2: Find the list of voters, excluding the user, who also support these projects
            other_voters = gs_donations_df[gs_donations_df['PayoutAddress'].isin(top_addresses['PayoutAddress']) & (gs_donations_df['Voter'] != address)]
            unique_other_voters = other_voters['Voter'].drop_duplicates()

            # Debugging
            tcol2.markdown("A total of " + str(len(unique_other_voters)) + " voters also support the projects you support the most.")

            #Step 3: Find top citizen round 3 projects supported by other voters
            # Find projects supported by other voters
            filtered_by_voters = gs_donations_df[gs_donations_df['Voter'].isin(unique_other_voters)]

        
            # Aggregate by donation amount and frequency of contribution
            top_supports_by_other_voters = filtered_by_voters.groupby('PayoutAddress') \
                                                             .agg({'AmountUSD': ['sum', 'count']}) \
                                                             .reset_index()

            # Rename columns for clarity
            top_supports_by_other_voters.columns = ['PayoutAddress', 'TotalAmountUSD', 'DonationCount']

            # Sort by donation count first, then by total amount in descending order
            top_supports_by_other_voters = top_supports_by_other_voters.sort_values(by=['DonationCount', 'TotalAmountUSD'], ascending=[False, False])
                                                 

            # Filter by those participating in CR3
            filtered_top_supports = top_supports_by_other_voters[top_supports_by_other_voters['PayoutAddress'].isin(cr3_df['PayoutAddress'])]
            # Debugging

            filtered_top_supports_names = filtered_top_supports.merge(cr3_df[['PayoutAddress', 'Project Name']].drop_duplicates(), on='PayoutAddress', how='left')
            #tcol2.markdown("Top CR3 projects supported by other voters")
            #tcol2.dataframe(filtered_top_supports_names, hide_index=True, use_container_width=True)            

            #Step 4: Exclude projects voted by the user

            recommended_addresses = filtered_top_supports[~filtered_top_supports['PayoutAddress'].isin(filtered_supported_by_user['PayoutAddress'])].head(10)

            recommended_projects = recommended_addresses.merge(cr3_df[['PayoutAddress', 'Project Name', 'Application Link']].drop_duplicates(), on='PayoutAddress', how='left')

            #tcol2.dataframe(recommended_addresses, hide_index=True, use_container_width=True)
            tcol2.markdown("This group of voters have previously supported a total of " + str(len(recommended_projects)) + " projects participating in Citizens Retro #3")
            tcol2.markdown("Here are the top 5 most frequently contributed projects by voters who support the projects you contribute to most:")
            tcol2.dataframe(recommended_projects,
                column_config = {
                "Project Name": "Project Name",
                "Application Link": st.column_config.LinkColumn(label = "Application Detail", display_text = "Open Application")
                },
                column_order=("Project Name", "Application Link"),
                hide_index=True, use_container_width=True)            


