import pandas as pd
import numpy as np
import plotly.express as px

months_short = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]


def select_type(hotel_type="All"):
    """Reads the "data/processed/clean_hotels.csv" source file and returns
        a data frame filtered by hotel type

    Parameters
    ----------
    hotel_type : string, either "City", "Resort", or "Both

    Returns
    -------
    dataframe with hotel data filtered by hotel type
    """
    hotels = pd.read_csv("clean_hotels.csv")
    # filter based on hotel type selection
    if hotel_type == "Resort":
        hotels = hotels[hotels["Hotel type"] == "Resort"]
    if hotel_type == "City":
        hotels = hotels[hotels["Hotel type"] == "City"]
    return hotels


def get_year_stats(data, scope="all_time", ycol="Reservations", year=2016):
    """creates a string with summary stats from the selected year
    Parameters
    ----------
    data :       dataframe produced by `get_year_data()`
    scope:       should the stats be for "all_time" or the "current" year?
    y_col:       the variable selected from "y-axis-dropdown"
    year:        the year selected from "year-dropdown"
    Returns
    -------
    string:      ex) "Year 2016: Ave=4726, Max=6203(Oct), Min=2248(Jan)"
    """
    if scope == "all_time":
        max_ind = data[data["Line"] == "Average"][ycol].argmax()
        min_ind = data[data["Line"] == "Average"][ycol].argmin()
        ave = round(data[data["Line"] == "Average"][ycol].mean())
        string = f"Historical "
    else:
        max_ind = data[data["Line"] != "Average"][ycol].argmax() + 12
        min_ind = data[data["Line"] != "Average"][ycol].argmin() + 12
        ave = round(data[data["Line"] != "Average"][ycol].mean())
        string = f"Year {year} "
    maxi = round(data.iloc[max_ind, 2])
    mini = round(data.iloc[min_ind, 2])
    max_month = months_short[data.iloc[max_ind, 0] - 1]
    min_month = months_short[data.iloc[min_ind, 0] - 1]

    string += f"Ave : {ave},  Max : {maxi}({max_month}),  Min : {mini}({min_month})"
    return string


def get_month_stats(data, scope="all_time", ycol="Reservations", year=2016, month=1):
    """creates a string with summary stats from the selected month and year
    Parameters
    ----------
    data :       dataframe produced by `get_year_data()`
    scope:       should the stats be for "all_time" or the "current" year
    y_col:       the variable selected from "y-axis-dropdown"
    year:        the year selected from "year-dropdown"
    month:       the month selected from "month-dropdown"
    Returns
    -------
    string:      ex) "Jan 2016 Ave : 73, Max : 183(Jan 2), Min : 33(Jan 31)"
    """
    short_month = months_short[month - 1]  # convert numeric month to abbreviated text
    if scope == "all_time":
        max_ind = data[data["Line"] == "Average"][ycol].argmax()
        min_ind = data[data["Line"] == "Average"][ycol].argmin()
        ave = round(data[data["Line"] == "Average"][ycol].mean())
        string = f"Historical  "
    else:
        if (year < 2016 and month < 7) or (
            year > 2016 and month > 8
        ):  # if out of data range return message
            return "No data for this month"
        max_ind = data[data["Line"] != "Average"][ycol].argmax() + len(
            data[data["Line"] == "Average"]
        )
        min_ind = data[data["Line"] != "Average"][ycol].argmin() + len(
            data[data["Line"] == "Average"]
        )
        ave = round(data[data["Line"] != "Average"][ycol].mean(skipna=True))
        string = f" {short_month} {year}  "

    maxi = round(data.iloc[max_ind, 2])
    mini = round(data.iloc[min_ind, 2])
    max_date = data.iloc[max_ind, 0]
    min_date = data.iloc[min_ind, 0]

    string += f"Ave : {ave},  Max : {maxi}({short_month} {max_date}),  Min : {mini}({short_month} {min_date})"
    return string


def get_year_data(hotel_type, y_col, year):
    """returns a data frame containing monthly summaries of one variable for
    the selected hotel type, for the selected year and for all-time

    Parameters
    ----------
    hotel_type : string, either "City", "Resort", or "Both
    y_col:       the variable selected from "y-axis-dropdown"
    year:        the year selected from "year-dropdown"

    Returns
    -------
    dataframe:  monthly summaries of selected variable for the selected time period
    """
    hotels = select_type(hotel_type)
    data = pd.DataFrame()
    if y_col == "Reservations":  # count number of "Reservations"
        data["Average"] = (
            hotels.groupby("Arrival month")["Hotel type"].count()
            / hotels.groupby("Arrival month")["Arrival year"].nunique()
        )
        data[str(year)] = (
            hotels[hotels["Arrival year"] == year]
            .groupby("Arrival month")["Hotel type"]
            .count()
        )
    elif y_col == "Average daily rate":  # average the "Average daily rate"
        data["Average"] = hotels.groupby("Arrival month")[y_col].mean()
        data[str(year)] = (
            hotels[hotels["Arrival year"] == year]
            .groupby("Arrival month")[y_col]
            .mean()
        )
    else:  # sum the other variables
        data["Average"] = (
            hotels.groupby("Arrival month")[y_col].sum()
            / hotels.groupby("Arrival month")["Arrival year"].nunique()
        )
        data[str(year)] = (
            hotels[hotels["Arrival year"] == year].groupby("Arrival month")[y_col].sum()
        )

    # make the month_no a column
    data = data.reset_index()
    data = pd.melt(data, "Arrival month").rename(
        columns={"variable": "Line", "value": y_col}
    )

    return data


def get_month_data(
    hotel_type="All",
    y_col="Reservations",
    year=2016,
    month=1,
):
    """returns a data frame containing monthly summaries of one variable for
    the selected hotel type, for the selected year and for all-time

    Parameters
    ----------
    hotel_type : string, either "City", "Resort", or "Both
    y_col:       the variable selected from "y-axis-dropdown"
    year:        the year selected from "year-dropdown"
    month:       the month selected from "month-dropdown"

    Returns
    -------
    dataframe:  daily summaries of selected variable for the selected time period
    """
    hotels = select_type(hotel_type)
    hotels = hotels[hotels["Arrival month"] == month]
    data = pd.DataFrame()
    if y_col == "Reservations":  # count number of "Reservations"
        data["Average"] = (
            hotels.groupby("Arrival day")["Hotel type"].count()
            / hotels.groupby("Arrival day")["Arrival year"].nunique()
        )
        data[str(year)] = (
            hotels[hotels["Arrival year"] == year]
            .groupby("Arrival day")["Hotel type"]
            .count()
        )
    elif y_col == "Average daily rate":  # average the "Average daily rate"
        data["Average"] = hotels.groupby("Arrival day")[y_col].mean()
        data[str(year)] = (
            hotels[hotels["Arrival year"] == year].groupby("Arrival day")[y_col].mean()
        )
    else:  # sum the other variables
        data["Average"] = (
            hotels.groupby("Arrival day")[y_col].sum()
            / hotels.groupby("Arrival day")["Arrival year"].nunique()
        )
        data[str(year)] = (
            hotels[hotels["Arrival year"] == year].groupby("Arrival day")[y_col].sum()
        )
    data = data.reset_index()
    data = pd.melt(data, "Arrival day").rename(
        columns={"variable": "Line", "value": y_col}
    )

    # filter out feb 29 for non-leap years
    if (year % 4 != 0) and month == 2:
        data = data[data["Arrival day"] != 29]

    # get the day of the week for the selected year
    data["Arrival day of week"] = pd.to_datetime(
        year * 10000 + month * 100 + data["Arrival day"], format="%Y%m%d"
    )
    data["Arrival day of week"] = data["Arrival day of week"].dt.dayofweek
    data["Arrival day of week"] = data["Arrival day of week"].replace(
        [0, 1, 2, 3, 4, 5, 6], ["Mon", "Tues", "Wed", "Thur", "Fri", "Sat", "Sun"]
    )

    return data


def left_hist_data(hotel_type="All", year=2016, month=1):
    """returns a data frame containing binned counts of hotel guests' country of origin
    for the selected hotel type and time period

    Parameters
    ----------
    hotel_type : string, either "City", "Resort", or "Both
    year:        the year selected from "year-dropdown"
    month:       the month selected from "month-dropdown"

    Returns
    -------
    dataframe:  containing binned counts of hotel guests' country of origin
    """
    df = select_type(hotel_type)
    df = df[df["Arrival year"] == year]
    df = df[df["Arrival month"] == month]
    df = (
        df.groupby("Country of origin")
        .size()
        .reset_index(name="counts")
        .sort_values(by="counts", ascending=False)[:10]
    )
    return df


def right_hist_data(hotel_type="All", year=2016, month=1):
    """returns a data frame containing binned counts of the duration of guests' stay
    for the selected hotel type and time period

    Parameters
    ----------
    hotel_type : string, either "City", "Resort", or "Both
    year:        the year selected from "year-dropdown"
    month:       the month selected from "month-dropdown"

    Returns
    -------
    dataframe:  containing binned counts of duration of guests' stay
    """
    df = select_type(hotel_type)
    # select relevant columns then filter by year and month
    df = df[["Arrival year", "Arrival month", "Total nights"]]
    df = df[df["Arrival year"] == year]
    df = df[df["Arrival month"] == month]
    # calculate counts for total nights
    df = (
        df.groupby("Total nights").count()
        / df.groupby("Total nights").count().sum()
        * 100
    )
    df = df.reset_index().drop(columns="Arrival year")
    df.columns = ["Total nights", "Percent of Reservations"]

    return df

def get_guest_map_prices_busy_months():
    hotels = pd.read_csv("hotels.csv")
    country_data = pd.DataFrame(hotels.loc[hotels["is_canceled"] == 0]["country"].value_counts())
    # country_data.index.name = "country"
    country_data.rename(columns={"country": "Number of Guests"}, inplace=True)
    total_guests = country_data["Number of Guests"].sum()
    country_data["Guests in %"] = round(country_data["Number of Guests"] / total_guests * 100, 2)
    country_data["country"] = country_data.index

    guest_map = px.choropleth(country_data,
                              locations=country_data.index,
                              color=country_data["Guests in %"],
                              hover_name=country_data.index,
                              color_continuous_scale=px.colors.sequential.Plasma)

    # normalize price per night (adr):
    hotels["adr_pp"] = hotels["adr"] / (hotels["adults"] + hotels["children"])
    full_data_guests = hotels.loc[hotels["is_canceled"] == 0]  # only actual gusts
    room_prices = full_data_guests[["hotel", "reserved_room_type", "adr_pp"]].sort_values("reserved_room_type")

    prices = px.box(x=room_prices["reserved_room_type"],
                    y=room_prices["adr_pp"], color=room_prices["hotel"])
    rh = hotels.loc[(hotels["hotel"] == "Resort Hotel") & (hotels["is_canceled"] == 0)]
    ch = hotels.loc[(hotels["hotel"] == "City Hotel") & (hotels["is_canceled"] == 0)]

    # Create a DateFrame with the relevant data:
    resort_guests_monthly = rh.groupby("arrival_date_month")["hotel"].count()
    city_guests_monthly = ch.groupby("arrival_date_month")["hotel"].count()

    resort_guest_data = pd.DataFrame({"month": list(resort_guests_monthly.index),
                                      "hotel": "Resort hotel",
                                      "guests": list(resort_guests_monthly.values)})

    city_guest_data = pd.DataFrame({"month": list(city_guests_monthly.index),
                                    "hotel": "City hotel",
                                    "guests": list(city_guests_monthly.values)})
    full_guest_data = pd.concat([resort_guest_data, city_guest_data], ignore_index=True)

    # order by month:
    ordered_months = ["January", "February", "March", "April", "May", "June",
                      "July", "August", "September", "October", "November", "December"]
    full_guest_data["month"] = pd.Categorical(full_guest_data["month"], categories=ordered_months, ordered=True)

    # Dataset contains July and August date from 3 years, the other month from 2 years. Normalize data:
    full_guest_data.loc[(full_guest_data["month"] == "July") | (full_guest_data["month"] == "August"),
                        "guests"] /= 3
    full_guest_data.loc[~((full_guest_data["month"] == "July") | (full_guest_data["month"] == "August")),
                        "guests"] /= 2

    # show figure:
    busy_months = px.line(x="month", y="guests", color="hotel", data_frame=full_guest_data)

    total_bookings = hotels.shape[0]
    cancelled_bookings = hotels[hotels['is_canceled'] == 1].shape[0]
    bookings_per_month = hotels.groupby(['arrival_date_year', 'arrival_date_month'])['hotel'].count().reset_index()
    max_bookings_month = bookings_per_month.loc[bookings_per_month['hotel'].idxmax()]
    max_bookings_month = hotels.groupby('arrival_date_month')['hotel'].count().sort_values(ascending=False).iloc[0]



    return guest_map,prices,busy_months,total_bookings,cancelled_bookings,max_bookings_month

if __name__ == "__main__":
    main()