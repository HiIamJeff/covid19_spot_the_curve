
import pandas as pd
from utils.data_utils import jhu_data_process_date, jhu_data_process_2day_specific, jhu_data_process_7day_moving, \
    top_country, data_process_avg


# Load the data
case_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
df_case = pd.read_csv(case_url)

# Population data
data_url_pop = 'https://raw.githubusercontent.com/HiIamJeff/COVID19_Spot_the_Curve/master/Country_Population.csv'

pop_df = pd.read_csv(data_url_pop)
pop_df['Population'] = pop_df['Population'].str.replace(',', '').astype(int)
country_pop_dict = pop_df.set_index('Country').to_dict('dict')['Population']
# fix specific country name
country_pop_dict['Czechia'] = country_pop_dict.pop('Czech Republic (Czechia)', 'default_value_if_not_found')

# final dataset
infection_data = data_process_avg(jhu_data_process_2day_specific(jhu_data_process_date(df_case), 100), country_pop_dict)
infection_data_moving = data_process_avg(jhu_data_process_7day_moving(jhu_data_process_date(df_case), 100), country_pop_dict)
top10_df = pd.DataFrame(top_country(jhu_data_process_date(df_case), 20))[0:10].reset_index().rename(
    columns={'index': 'Country'})
