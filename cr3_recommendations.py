import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import re
import numpy as np
import plotly.express as px

st.set_page_config(layout='wide')
tcol1,tcol2,tcol3 = st.columns([1,16,1])

#tcol2.image("https://grantsscope.xyz/wp-content/uploads/2024/04/bafybeibrcljtp3nqiowx7qng7fh2xkj23rnm6fbidqosdu5qxrtcudkkue-3.jpeg")
tcol2.title('Gitcoin Citizens Retro - Round 3')
tcol2.markdown('### Get one-click personalized grantee recommendations using GrantsScope')
tcol2.markdown('Dive into the [Gitcoin Citizens Retro Round](https://gitcoin.notion.site/Citizens-Retro-704a64ca7a874a1d97d94d48a05bb81f), designed to honor and reward the invaluable contributions of our citizens to the Gitcoin ecosystem. \
                Contributions are welcome until **April 16th**, and we\'re excited to share that GrantsScope is among the grantees seeking retroactive support in this round. ')
tcol2.markdown('Want to explore more about the round? Click [here](https://explorer-v1.gitcoin.co/#/round/42161/0x5aa255d5cae9b6ce0f2d9aee209cb02349b83731)  for a deep dive. \
                If GrantsScope\'s mission resonates with you, consider showing your support in the Gitcoin Citizens Round by contributing [here](https://explorer-v1.gitcoin.co/#/round/42161/0x5aa255d5cae9b6ce0f2d9aee209cb02349b83731/57).')

tcol2.markdown('We\'re excited to offer you personalized recommendations to enhance your contribution experience. Here\'s what you can expect:')
tcol2.markdown('1. **Cherished Allies:** Re-discover the grantees you\'ve supported in the past.' + '\n' \
                '2. **Community Favorites:** Explore grantees backed by the community who also champion your favorite projects.' + '\n' \
                '3. **Likeminded Visionaries:** We\'ll introduce you to grantees similar to those you\'ve previously supported or that align with community favorites. They\'re on missions you might find just as inspiring!')

# Get address
address = tcol2.text_input('Enter your Ethereum address below (starting "0x"):', 
							help='ENS not supported, please enter 42-character hexadecimal address starting with "0x"')

# Convert to lower case for ease of comparison
address = address.lower()

if address and address != 'None':
        
        if not re.match(r'^(0x)?[0-9a-f]{40}$', address, flags=re.IGNORECASE):
            tcol2.error('Not a valid address. Please enter a valid 42-character hexadecimal Ethereum address starting with "0x"')
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
            filtered_supported_by_user = supported_by_user.merge(cr3_df['PayoutAddress'].drop_duplicates(), on='PayoutAddress', how='inner')
            
            
            # Results Display Code
            matched_projects = filtered_supported_by_user.merge(cr3_df[['PayoutAddress', 'Project Name', 'Short Project Desc', 'Application Link']], 
                            on='PayoutAddress', 
                            how='inner',
                            suffixes=('', '_cr3'))

            matched_projects.drop('Project Name', axis=1, inplace=True)
            matched_projects.rename(columns={'Project Name_cr3': 'Project Name'}, inplace=True)

            #tcol2.dataframe(matched_projects)    

            matched_projects_df = matched_projects.groupby(['PayoutAddress', 'Project Name', 'Short Project Desc', 'Application Link']).agg({
                'AmountUSD': 'sum',                
                'Round Name': ', '.join  # Join the combined project-round strings
            }).reset_index()

            tcol2.markdown("#### 1. Cherished Allies: List of grantees who you have contributed in the past")
            tcol2.markdown("Here are the grantees whose payout address you have previously donated to. Show them some love again in this round!")
            
            tcol2.caption("*Double-click on a row to read the entire text.*")
            tcol2.dataframe(matched_projects_df, hide_index=True, use_container_width=True,
                column_order=("Project Name", "Short Project Desc", "Round Name", "Application Link"),   
                column_config = {
                    "Project Name": "Grantee Name",
                    "Short Project Desc": "Short Description",
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

            top_projects_grouped_df.sort_values(by=['AmountUSD'])

            tcol2.markdown("#### 2. Community Favorites: Recommendations based on your donation history")
            
            #tcol2.dataframe(top_projects_grouped_df, column_config = {
            #    "ProjectRound": "Project (Round) Donated to",
            #    "AmountUSD": st.column_config.NumberColumn("Total Donations (in USD)", step = 1, format = "$%d")
            #    },
            #    column_order=("ProjectRound"),
            #    hide_index=True, use_container_width=True)            
            # End of debudding and display code

            #Step 2: Find the list of voters, excluding the user, who also support these projects
            other_voters = gs_donations_df[gs_donations_df['PayoutAddress'].isin(top_addresses['PayoutAddress']) & (gs_donations_df['Voter'] != address)]
            unique_other_voters = other_voters['Voter'].drop_duplicates()

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

            recommended_addresses = filtered_top_supports[~filtered_top_supports['PayoutAddress'].isin(filtered_supported_by_user['PayoutAddress'])]

            recommended_projects = recommended_addresses.merge(cr3_df[['PayoutAddress', 'Project Name', 'Short Project Desc', 'Application Link']].drop_duplicates(), on='PayoutAddress', how='left')

            #tcol2.dataframe(recommended_addresses, hide_index=True, use_container_width=True)
            tcol2.markdown("Here are the 5 most frequently contributed grantees by the Gitcoin community who also support your most favorite projects.")
            
            tcol2.caption("*Double-click on a row to read the entire text.*")
            tcol2.dataframe(recommended_projects.head(5),
                column_config = {
                "Project Name": "Project Name",
                "Short Project Desc": "Short Description",
                "Application Link": st.column_config.LinkColumn(label = "Application Detail", display_text = "Open Application")
                },
                column_order=("Project Name", "Short Project Desc", "Application Link"),
                hide_index=True, use_container_width=True)

            # Explaination
            with tcol2.expander("**See explanation**"):
                st.markdown("We've analyzed your donation history on Grants Stack up to March 31st, 2024, focusing on your engagements with Gitcoin Grants and Community Rounds. \
                            The result is the following curated list of your top 5 contributions, pinpointing where your support has been directed:")
                
                project_rounds = top_projects_grouped_df['ProjectRound'].tolist()
                markdown_list = "\n".join(f"- {item}" for item in project_rounds)
                st.markdown(markdown_list)

                st.markdown("Interestingly, a community of " + str(len(unique_other_voters)) + " voters shares your passion, supporting the projects you value most. \
                    These like-minded individuals have collectively backed " + str(len(recommended_projects)) + "  grantees featured in Citizens Retro #3.")
                st.markdown("The list above showcases the top 5 grantees frequently supported by this community — ones you haven't contributed to yet. \
                    This insight offers a unique perspective on where your interests align with the broader Gitcoin community, unveiling new opportunities for your future contributions.")
                
            # Show cluster of projects distringuished by those already contributed before CR3, those recommended and others
            cluster_df = pd.read_csv('cluster_cr3_projects.csv')
            cluster_df['PayoutAddress'] = cluster_df['PayoutAddress'].str.lower()


            # Assuming 'PayoutAddress' is the column of interest in all DataFrames
            # Create conditions
            condition1 = cluster_df['PayoutAddress'].isin(matched_projects_df['PayoutAddress'])
            condition2 = cluster_df['PayoutAddress'].isin(recommended_projects.head(5)['PayoutAddress'])

            # Define choices based on conditions
            choices = [
                '1',  # If PayoutAddress is in matched_projects_df
                '2'  # If PayoutAddress is in top 5 of recommended_projects
            ]

            # Use numpy.select to assign values to the 'flag' column based on conditions
            cluster_df['flag'] = np.select([condition1, condition2], choices, default='3')

            color_map = {
                '1': '#cccccc',    # Light gray for the most subtle appearance
                '2': '#0000ff',    # Solid blue for noticeable emphasis
                '3': '#ff4500'     # Dark red or bright orange for maximum visibility
            }

            #close_projects = []

            
            #for index, row in cluster_df[cluster_df['flag'] == '3'].iterrows():
            #    for _, compare_row in cluster_df[cluster_df['flag'].isin(['1', '2'])].iterrows():
            #        distance = np.sqrt((row['UMAP_1'] - compare_row['UMAP_1']) ** 2 + (row['UMAP_2'] - compare_row['UMAP_2']) ** 2)
            #        if distance <= 0.5:
            #            close_projects.append((row['PayoutAddress'], compare_row['PayoutAddress'],distance))

            #tcol2.dataframe(close_projects)

            # Now, extract and print the information from cr3_df for each close pair found
            #for close_pair in close_projects:
            #    project_3 = cr3_df[cr3_df['PayoutAddress'].str.lower() == close_pair[0]].iloc[0]
            #    project_12 = cr3_df[cr3_df['PayoutAddress'].str.lower() == close_pair[1]].iloc[0]
                
            #    tcol2.markdown(f"Project with Flag 3: {project_3['Project Name']} - {project_3['Application Link']}")
            #    tcol2.markdown(f"Similar to: {project_12['Project Name']}")
            
            
            # Initialize a list to hold tuples of project_3 addresses and their close project_12 addresses
            close_projects_data = []

            for index, project_3 in cluster_df[cluster_df['flag'] == '3'].iterrows():
                close_project_12_addresses = []
                for _, project_12 in cluster_df[cluster_df['flag'].isin(['1', '2'])].iterrows():
                    distance = np.sqrt((project_3['UMAP_1'] - project_12['UMAP_1']) ** 2 + (project_3['UMAP_2'] - project_12['UMAP_2']) ** 2)
                    if distance < 0.35:
                        close_project_12_addresses.append(project_12['PayoutAddress'])
                
                # Add the collected data for this project_3 as a single tuple
                if close_project_12_addresses:
                    close_projects_data.append((project_3['PayoutAddress'], close_project_12_addresses))

            # Create a DataFrame from the list of tuples
            close_projects_df = pd.DataFrame(close_projects_data, columns=['Project_3_Address', 'Close_Project_12_Addresses'])

            close_projects_df['Project_3_Name'] = close_projects_df['Project_3_Address'].apply(
                lambda x: cr3_df.loc[cr3_df['PayoutAddress'].str.lower() == x.lower(), 'Project Name'].iloc[0] if not cr3_df.loc[cr3_df['PayoutAddress'].str.lower() == x.lower()].empty else 'N/A'
            )
            
            close_projects_df['Project_3_Short_Desc'] = close_projects_df['Project_3_Address'].apply(
                lambda x: cr3_df.loc[cr3_df['PayoutAddress'].str.lower() == x.lower(), 'Short Project Desc'].iloc[0] if not cr3_df.loc[cr3_df['PayoutAddress'].str.lower() == x.lower()].empty else 'N/A'
            )
            
            close_projects_df['Project_3_App_Link'] = close_projects_df['Project_3_Address'].apply(
                lambda x: cr3_df.loc[cr3_df['PayoutAddress'].str.lower() == x.lower(), 'Application Link'].iloc[0] if not cr3_df.loc[cr3_df['PayoutAddress'].str.lower() == x.lower()].empty else 'N/A'
            )

            def get_project_names(addresses):
                project_names = []
                for address in addresses:
                    project_name = cr3_df.loc[cr3_df['PayoutAddress'].str.lower() == address.lower(), 'Project Name'].iloc[0] if not cr3_df.loc[cr3_df['PayoutAddress'].str.lower() == address.lower()].empty else 'N/A'
                    project_names.append(project_name)
                return ', '.join(project_names)

            close_projects_df['Close_Project_12_Names'] = close_projects_df['Close_Project_12_Addresses'].apply(get_project_names)

            if len(close_projects_df) > 0:

                # Display the updated DataFrame
                tcol2.markdown('#### 3. Likeminded Visionaries: Grantees who are most similar to the grantees in the above two lists')
                tcol2.markdown("So that you don't miss out on learning about new grantees or grantees outside your contribution network, \
                here's a stab at listing most similar grantees to some of our recommendations above - you might like what they are up to!")

                tcol2.caption("*Double-click on a row to read the entire text.*")
                tcol2.dataframe(close_projects_df,
                                column_config = {
                                "Project_3_Name": "Grantee Name",
                                "Project_3_Short_Desc": "Short Description",
                                "Close_Project_12_Names": "Similar to",
                                "Project_3_App_Link": st.column_config.LinkColumn(label = "Application Detail", display_text = "Open Application")
                                },
                                column_order=("Project_3_Name", "Project_3_Short_Desc","Close_Project_12_Names", "Project_3_App_Link"),
                                hide_index=True, use_container_width=True)  

                with tcol2.expander("**See explanation**"):  
                    st.markdown("Technical Notes: Grantee descriptions are first converted into numerical vectors using a Sentence Transformer model. \
                        Next, UMAP reduces this high-dimensional data to a two-dimensional space, maintaining the intrinsic relationships between grantees.\
                        Finally, the HDBSCAN algorithm clusters these projects based on their descriptions' similarities, \
                        identifying dense groups and distinguishing outliers, which helps in understanding the natural categorizations and thematic consistencies within the project dataset.")


                #fig = px.scatter(cluster_df, x='UMAP_1', y='UMAP_2', color='flag',
                #     text='Project Name', 
                #     hover_data={'UMAP_1': False, 'UMAP_2': False, 'Project Name': False, 'Short Project Desc': True, 'Cluster': False},
                #     title='Visual Landscape of Gitcoin Citizens Retro #3 Projects',
                #     color_discrete_map=color_map,
                #     width=1200, 
                #     height=900)

                # Update layout to ensure text labels are displayed nicely
                #fig.update_traces(textposition='top center')

                #st.plotly_chart(fig, use_container_width=True)

