import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import re

# Get address
address = st.text_input('Enter your Ethereum address below to uncover your unique impact story (starting "0x"):', 
							help='ENS not supported, please enter 42-character hexadecimal address starting with "0x"')

# Convert to lower case for ease of comparison
address = address.lower()

if address and address != 'None':
        
        if not re.match(r'^(0x)?[0-9a-f]{40}$', address, flags=re.IGNORECASE):
            st.error('Not a valid address. Please enter a valid 42-character hexadecimal Ethereum address starting with "0x"')
            my_bar.empty()
        else:

            # Load all donations data on Grants Stack
            gs_donations_df = pd.read_csv('gs donations.csv')
            # Convert voter to lower case for ease of comparison
            gs_donations_df['Voter'] = gs_donations_df['Voter'].str.lower()
            gs_donations_df['PayoutAddress'] = gs_donations_df['PayoutAddress'].str.lower()

            #load the citizens round 3 projects
            cr3_df = pd.read_csv('summarized_cr3_projects.csv')
            # Convert Payout Address to lower case for ease of comparison
            cr3_df['PayoutAddress'] = cr3_df['PayoutAddress'].str.lower()

            #Step 1: Find top 5 grantees donated to by the user
            top_addresses = gs_donations_df[gs_donations_df['Voter'] == address].groupby('PayoutAddress').agg({'AmountUSD': 'sum'}).reset_index().sort_values('AmountUSD', ascending=False).head(5)
            top_projects = pd.merge(top_addresses, gs_donations_df[['PayoutAddress', 'Project Name']].drop_duplicates(), on='PayoutAddress', how='left')

            # Debugging
            st.markdown("Your top supported projects:")
            st.dataframe(top_projects)            

            #Step 2: Find the list of voters, excluding the user, who also support these projects
            other_voters = gs_donations_df[gs_donations_df['PayoutAddress'].isin(top_addresses['PayoutAddress']) & (gs_donations_df['Voter'] != address)]
            unique_other_voters = other_voters['Voter'].drop_duplicates()

            # Debugging
            st.markdown("A total of " + str(len(unique_other_voters)) + " voters also support your top 5 projects")

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
            top_supports_by_other_voters = top_supports_by_other_voters.sort_values(by=['DonationCount', 'TotalAmountUSD'], ascending=[False, False]
                                                 

            # Filter by those participating in CR3
            filtered_top_supports = top_supports_by_other_voters[top_supports_by_other_voters['PayoutAddress'].isin(cr3_df['PayoutAddress'])]
            # Debugging

            filtered_top_supports_names = filtered_top_supports.merge(cr3_df[['PayoutAddress', 'Project Name']].drop_duplicates(), on='PayoutAddress', how='left')
            st.markdown("Top CR3 projects supported by other voters")
            st.dataframe(filtered_top_supports_names)            


            #Step 4: Exclude projects voted by the user

            # Find projects supported by user
            supported_by_user = gs_donations_df[gs_donations_df['Voter'] == address].drop_duplicates(subset=['PayoutAddress'])

            # Filter by those participating in CR3
            filtered_supported_by_user = supported_by_user.merge(cr3_df['PayoutAddress'].drop_duplicates(), on='PayoutAddress', how='inner')
            #filtered_supported_by_user = supported_by_user[supported_by_user['PayoutAddress'].isin(cr3_df['PayoutAddress'])]

            # Debugging
            matched_projects = filtered_supported_by_user.merge(cr3_df[['PayoutAddress', 'Project Name']], on='PayoutAddress', how='inner')
            st.markdown("You have previously donated to the payout address used by these projects:")
            st.dataframe(matched_projects)            

            recommended_addresses = filtered_top_supports[~filtered_top_supports['PayoutAddress'].isin(filtered_supported_by_user['PayoutAddress'])].head(10)

            recommended_projects = recommended_addresses.merge(cr3_df[['PayoutAddress', 'Project Name']].drop_duplicates(), on='PayoutAddress', how='left')

            st.dataframe(recommended_addresses)
            st.dataframe(recommended_projects[['Project Name']])