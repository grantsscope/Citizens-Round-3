import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# Get address
address = st.text_input('Enter your Ethereum address below to uncover your unique impact story (starting "0x"):', 
							help='ENS not supported, please enter 42-character hexadecimal address starting with "0x"')

# Convert to lower case for ease of comparison
address = address.lower()

if address and address != 'None':
        
        if not re.match(r'^(0x)?[0-9a-f]{40}$', address, flags=re.IGNORECASE):
            tcol2.error('Not a valid address. Please enter a valid 42-character hexadecimal Ethereum address starting with "0x"')
            my_bar.empty()
        else:

            # Load all donations data on Grants Stack
            gs_donations_df = pd.read_csv('./gs donations.csv')
            # Convert voter to lower case for ease of comparison
            gs_donations_df['Voter'] = gs_donations_df['Voter'].str.lower()

            #load the citizens round 3 projects
            cr3_df = pd.read_csv('./summarized_cr3_projects.csv')
            # Convert Payout Address to lower case for ease of comparison
            cr3_df['PayoutAddress'] = cr3_df['PayoutAddress'].str.lower()

            #Step 1: Find top 5 grantees donated to by the user
            top_addresses = gs_donations_df[gs_donations_df['Voter'] == address].groupby('PayoutAddress').agg({'AmountUSD': 'sum'}).reset_index().sort_values('AmountUSD', ascending=False).head(5)

            #Step 2: Find the list of voters, excluding the user, who also support these projects
            other_voters = gs_donations_df[gs_donations_df['PayoutAddress'].isin(top_addresses['PayoutAddress']) & (gs_donations_df['Voter'] != address)]
            unique_other_voters = other_voters['Voter'].drop_duplicates()

            #Step 3: Find top citizen round 3 projects supported by other voters
            # Find projects supported by other voters
            filtered_by_voters = gs_donations_df[gs_donations_df['Voter'].isin(unique_other_voters)]

            # Sort by amount donated
            top_supports_by_other_voters = filtered_by_voters.groupby('PayoutAddress') \
                                                                 .agg({'AmountUSD': 'sum'}) \
                                                                 .reset_index() \
                                                                 .sort_values('AmountUSD', ascending=False)

            # Filter by those participating in CR3
            filtered_top_supports = top_supports_by_other_voters[top_supports_by_other_voters['PayoutAddress'].isin(cr3_df['PayoutAddress'])]


            #Step 4: Exclude projects voted by the user

            # Find projects supported by user
            supported_by_user = gs_donations_df[gs_donations_df['Voter'] == address].drop_duplicates(subset=['PayoutAddress'])
            # Filter by those participating in CR3

            filtered_supported_by_user = supported_by_user.merge(cr3_df['PayoutAddress'].drop_duplicates(), on='PayoutAddress', how='inner')
            #filtered_supported_by_user = supported_by_user[supported_by_user['PayoutAddress'].isin(cr3_df['PayoutAddress'])]


            recommended_addresses = filtered_top_supports[~filtered_top_supports['PayoutAddress'].isin(filtered_supported_by_user)].head(10)

            recommended_projects = recommended_addresses.merge(cr3_df[['PayoutAddress', 'Project Name']].drop_duplicates(), on='PayoutAddress', how='left')

            st.dataframe(recommended_projects[['Project Name']])