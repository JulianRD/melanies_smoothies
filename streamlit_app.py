# Import python packages
import streamlit as st
import requests
import pandas as pd
#from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(f":cup_with_straw: Customize your Smoothie! :cup_with_straw:")

st.write(
  "Choose the fruits you want in your smoothie!"
)

customer_name = st.text_input("Name for your order")

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))

#st.dataframe(data=my_dataframe, use_container_width=True)


#convert the snowpark dataframe into a pandas dataframe to use the Loc function
pd_df = my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()

ingredient_list = st.multiselect('Choose up to 5 ingredients:', my_dataframe, max_selections=5)

if ingredient_list:

    ingredient_string = ''

    for fruit_chosen in ingredient_list:
        ingredient_string += fruit_chosen + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        #st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
      
        st.subheader(fruit_chosen + ' Nutrition Information' )
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        st_dataframe = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    st.write(ingredient_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, NAME_ON_ORDER)
            values ('""" + ingredient_string + """','""" + customer_name + "')"

    #st.write(my_insert_stmt)
    #st.stop()
    
    ready_to_insert = st.button('Submit Order')
    

    if ready_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered! ' + customer_name, icon="✅")
