from chaparralapi import Client, Result
import streamlit as st
import pandas as pd

def login_dialog():
    """
    Sets the login information in streamlit session state
    """
    st.title("Login")
    api_key = st.text_input("API Key")

    if st.button("Login", type="primary"):
        try:
            client = Client(api_key)
            user_profile = client.get_user_profile()
            st.session_state['user'] = user_profile
            st.session_state['authenticated'] = True
            st.session_state['api_key'] = api_key

        except Exception as e:
            st.error(f"Login failed: {str(e)}")

            st.session_state['authenticated'] = False
            st.session_state['user'] = None
            st.session_state['api_key'] = None


def logout_dialog():
    """
    Clears the login information in streamlit session state
    """
    st.title("Logout")
    if st.button("Logout", type="primary"):
        st.session_state['authenticated'] = False
        st.session_state['user'] = None
        st.session_state['api_key'] = None
        st.rerun()


def login():
    """
    Will stop streamlit execution if use is not logged in
    """

    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    if st.session_state['authenticated'] is False:
        login_dialog()

        if st.session_state['authenticated'] is True:
            st.rerun()

        st.stop()

    else:
        st.write(
            f"Logged in as {st.session_state['user'].first_name} {st.session_state['user'].last_name} ({st.session_state['user'].email})")
        logout_dialog()

        if st.session_state['authenticated'] is False:
            st.rerun()


with st.sidebar:
    st.header("Chaparral Auto Uploader")
    login()

client = Client(st.session_state['api_key'])

if 'search_id' not in st.session_state:
    search_results = client.get_search_results()
    sr_df = pd.DataFrame([sr.dict() for sr in search_results])
    selection = st.dataframe(sr_df, use_container_width=True, hide_index=True,
                             on_select='rerun', selection_mode='single-row')
    selected_indices = [row for row in selection['selection']['rows']]
    selected_ids = [sr_df.iloc[i].id for i in selected_indices]

    if len(selected_ids) == 1:
        st.session_state['search_id'] = selected_ids[0]
        st.rerun()
else:
    st.subheader("Selected Search Result")
    search_result = client.get_search_result(st.session_state['search_id'])
    sr_df = pd.DataFrame([search_result.dict()])
    st.dataframe(sr_df, use_container_width=True, hide_index=True)
    if st.button("Change Search", use_container_width=True):
        del st.session_state['search_id']
        st.rerun()


    result = Result(client, search_result.id)
    proteins = [pi.protein for pi in result.protein_iterable()]
    protein_df = pd.DataFrame([protein.dict() for protein in proteins])
    selection = st.dataframe(protein_df, use_container_width=True, hide_index=True,
                                on_select='rerun', selection_mode='single-row')
    selected_indices = [row for row in selection['selection']['rows']]

    if len(selected_indices) == 1:
        selected_row = protein_df.iloc[selected_indices[0]]
        protein_name = selected_row['name']
        peptides = selected_row['peptide_sequences']

        serialized_peptides = ';'.join(peptides)

        st.write(f"Selected Protein: {protein_name}")
        db, protein_id, protein_name = protein_name.split('|')
        st.write(f"Peptides: {peptides}")

        PDB_APP = f'https://pdb-coverage.streamlit.app/?protein_id={protein_id}&input_type=peptides&input={serialized_peptides}'

        st.link_button("View in PDB", PDB_APP, use_container_width=True)




