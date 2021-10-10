import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from PIL import Image

st.set_page_config(page_title='Survey Responses')
st.title('Survey Responses')

### Create upload widget
st.header('Upload')
data_file = st.file_uploader('Upload your CSV or Excel file.',
                             type=['csv', 'xlsx'])

if not data_file:
    st.text('You have not uploaded a file. Please upload a file. :)')

if data_file is not None:

    # Output upload details
    st.success("File successfully uploaded!")
    st.write('---')
    file_details = {'filename': data_file.name,
                    'filetype': data_file.type,
                    'filesize': data_file.size}
    st.write(file_details)

    st.write('---')

    ### Load data
    df = pd.read_excel(data_file,
                       usecols='A:O',
                       header=0)

    # Clean the dataframe
    df = df.drop(['ID', 'Email', 'Name'], axis=1)
    df = df.rename(columns={'Name2': 'Name',
                            'Sub-Category2': '2',
                            'Sub-Category3': '3',
                            'Sub-Category4': '4',
                            'Customer': 'Type'})

    # Replace NaN with '-'
    df = df.fillna('-')

    # Combine Sub-Category values into a single column
    target = df.loc[:, '2':'4']
    d = {}
    for index in target.index:
        for i in target.iloc[index]:
            if i == '-':
                continue
            else:
                d[index] = i

    copy = df['Sub-Category'].tolist().copy()
    for i, v in enumerate(copy):
        if i in d:
            copy[i] = d[i]
        else:
            continue

    # Update Sub-Category column
    df['Sub-Category'] = copy

    df = df.drop(['2', '3', '4'], axis=1)

    # Repeat for Customer and Project columns
    # Combine Project with Customer columns into new column called Type
    target_proj = df['Project']
    d_proj = {}
    for i in target_proj.index:
        if target_proj[i] == '-':
            continue
        else:
            d_proj[i] = target_proj[i]

    copy_type = df['Type'].tolist().copy()
    for i, v in d_proj.items():
        copy_type[i] = v

    # Replace
    df['Type'] = copy_type

    # Drop Project column
    df = df.drop(['Project'], axis=1)

    ### Streamlit selection
    start_date = np.datetime64(st.date_input('Start date', df['Date'].min()))
    end_date = np.datetime64(st.date_input('End date', df['Date'].max()))

    if start_date < end_date:
        st.success('Start date: {}\n\nEnd date: {}'.format(start_date, end_date))
    else:
        st.error('Error: End date must fall after start date.')

    name_selection = st.multiselect('Names:',
                                    df['Name'].unique().tolist(),
                                    default=df['Name'].unique().tolist())

    if not name_selection:
        st.error("Warning: Please make appropriate name selection")
    else:
        ### Filter based on selections
        mask = (df['Date'].between(start_date,
                                   end_date)) & (df['Name'].isin(name_selection))

        # Number of results after filtering
        number_of_results = df[mask].shape[0]

        ### Group dataframe based on selection
        df_grouped = df[mask].groupby(by=['Category'])[['Hours']].sum()
        df_grouped = df_grouped.reset_index()

        ### Plot the bar chart
        bar_chart = px.bar(df_grouped,
                           x='Category',
                           y='Hours',
                           text='Hours',
                           color_discrete_sequence=['#F63366'] * len(df_grouped),
                           template='plotly_white')

        st.write('---')
        st.dataframe(df[mask])
        st.markdown(f'*Available Results: {number_of_results}*')
        st.write('---')

        st.write('## Summary of Categories by Hours')
        st.plotly_chart(bar_chart)

        st.write('---')

        option = st.selectbox('Select Category:', df[mask]['Category'].unique().tolist())
        df_cat = pd.DataFrame(df[mask].groupby(['Category', 'Sub-Category'])['Hours'].sum()).reset_index()
        df_cat = df_cat[df_cat['Category'] == option].assign(hack='').set_index('hack')
        df_cat = df_cat.iloc[:, 1:]
        st.dataframe(df_cat)

        pie_chart = px.pie(df_cat,
                           title=f'Percentage Hours Spent on <b>{option}</b>',
                           values='Hours',
                           names='Sub-Category',
                           color_discrete_sequence=px.colors.sequential.Burg)

        st.plotly_chart(pie_chart)

        st.write('---')

        # remove '-' in options
        list_options = df[mask]['Type'].unique().tolist()
        list_options_copy = list_options.copy()
        for index, value in enumerate(list_options_copy):
            if value == '-':
                del list_options[index]

        # select by customer or projects
        option = st.selectbox('Select Customer or Project:', list_options)
        df_cust = pd.DataFrame(df[mask].groupby(['Type', 'Category', 'Sub-Category'])['Hours'].sum()).reset_index()
        df_cust = df_cust[df_cust['Type'] == option].assign(hack='').set_index('hack')
        df_cust = df_cust.iloc[:, 1:]
        st.dataframe(df_cust)


        pie_chart = px.pie(df_cust,
                           title=f'Percentage Hours Spent on <b>{option}</b>',
                           values='Hours',
                           names='Sub-Category',
                           color_discrete_sequence=px.colors.sequential.Blugrn)

        st.plotly_chart(pie_chart)
        st.write('---')













