
import pandas as pd
import numpy as np


def jhu_data_process_date(jhu_data):
    # fix the country name
    jhu_data['Country/Region'] = jhu_data['Country/Region'].replace({'Korea, South': 'South Korea',
                                                                     'Taiwan*': 'Taiwan', 'US': 'United States'})
    df_country = jhu_data.set_index('Country/Region')
    # special fix for different level rows
    df_country.insert(loc=1, column="Country_level", value=0)
    duplicated = ~df_country.index.duplicated(keep=False)
    df_country['Country_level'] = duplicated.astype(int)
    df_country['index col'] = df_country.index
    special_rows = df_country[df_country['Country_level'] == 0]
    # build date index
    date_list = list(special_rows.columns)[4:-1]
    # sum up the value from lower level
    try:
        agg_special_rows = special_rows.pivot_table(values=date_list, index='index col', aggfunc=np.sum)[date_list]
        df_country2 = df_country[df_country['Country_level'] == 1].copy()
        df_country2.drop(['Province/State', 'Country_level', 'Lat', 'Long', 'index col'], axis=1, inplace=True)
        final_country_df = pd.concat([df_country2, agg_special_rows]).T
    except:
        df_country2 = df_country[df_country['Country_level'] == 1].copy()
        df_country2.drop(['Province/State', 'Country_level', 'Lat', 'Long', 'index col'], axis=1, inplace=True)
        final_country_df = df_country2.T
    final_country_df.index = pd.to_datetime(final_country_df.index)
    return final_country_df


def jhu_data_process_day(date_df):
    day_list = [list(date_df[c][date_df[c] > 0]) for c in date_df.columns]
    day_df = pd.DataFrame(day_list, index=list(date_df.columns)).T
    day_df.index += 1
    return day_df


def jhu_data_process_2day_specific(date_df, day_threshold):
    country_arrays = [np.array(date_df[c])[np.array(date_df[c]) > day_threshold] for c in date_df.columns]
    day_df = pd.DataFrame(country_arrays).T
    day_df.columns = list(date_df.columns)
    day_df.index += 1
    # calculate daily increase
    temp_df = day_df.diff(periods=1)
    series_list = [temp_df[c].shift(-1)[temp_df[c].shift(-1) > 0].reset_index(drop=True) for c in temp_df.columns]
    daily_increase_df = pd.DataFrame(series_list).T
    daily_increase_df.index = daily_increase_df.index + 1
    ## make the value into 2-day format
    list_list = [[(daily_increase_df[c][n] + daily_increase_df[c][n + 1])
                  for n in range(1, len(daily_increase_df)) if n % 2 == 1] for c in daily_increase_df.columns]
    avg_2day_increase_df = pd.DataFrame(list_list, index=list(daily_increase_df.columns)).T
    return avg_2day_increase_df


def jhu_data_process_7day_moving(date_df, day_threshold):
    country_arrays = [np.array(date_df[c])[np.array(date_df[c]) > day_threshold] for c in date_df.columns]
    day_df = pd.DataFrame(country_arrays).T
    day_df.columns = list(date_df.columns)
    day_df.index += 1
    # calculate daily increase
    temp_df = day_df.diff(periods=1)
    series_list = [temp_df[c].shift(-1)[temp_df[c].shift(-1) > 0].reset_index(drop=True) for c in temp_df.columns]
    daily_increase_df = pd.DataFrame(series_list).T
    daily_increase_df.index = daily_increase_df.index + 1
    return daily_increase_df.rolling(window=7).mean().shift(-6)


def data_process_avg(complete_df, country_pop_dict):
    for c in list(complete_df.columns):
        try:
            complete_df[c] = round(complete_df[c] / country_pop_dict.get(c) * 1000000, 2)
        except:
            complete_df[c + '_no_pop_value'] = complete_df[c]
    return complete_df


def top_country(complete_df, country_pop_dict, rank):
    top = complete_df.T.iloc[:, -1].sort_values(ascending=False)[
          0:30]  # some countries have inconsistent name so limit the number
    top_avg = {c: round(top[c] / country_pop_dict.get(c) * 1000000, 2) for c in top.index}
    return pd.Series(top_avg, name='Infection Rate').sort_values(ascending=False)[0:rank]

