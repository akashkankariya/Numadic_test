import pandas as pd
from datetime import datetime


# Defining Path
base_vehicle_data_path = r'Data/NU-raw-location-dump/EOL-dump/'
trip_info_path = r'Data/Trip-Info.csv'

# Storing trip_info.csv in pandas dataframe
trip_info = pd.read_csv(trip_info_path)

# Taking input of start and end date
start_date = int(input('Enter Start date : '))
end_date = int(input('Enter End date : '))

columns = ['License plate number', 'Distance', 'Number of Trips Completed',
           'Average Speed', 'Transporter Name', 'Number of Speed Violations']

asset_report = pd.DataFrame(columns=columns)

start_date_datetime = datetime.fromtimestamp(start_date)
end_date_datetime = datetime.fromtimestamp(end_date)
trip_info['datetime'] = pd.to_datetime(trip_info['date_time'], format='%Y%m%d%H%M%S')


# Selecting only required data
trip_info_required_data = trip_info.loc[(trip_info['datetime'] >= start_date_datetime) & (trip_info['datetime'] <= end_date_datetime)]
unique_vehicle = trip_info_required_data['vehicle_number'].value_counts()
unique_vehicle_numbers = unique_vehicle.keys().values

# Running loop for all vehicles
for vehicle_number in unique_vehicle_numbers:
    try:
        vehicle_data_path = base_vehicle_data_path + str(vehicle_number) + '.csv'
        vehicle_data = pd.read_csv(vehicle_data_path)
        try:
            vehicle_required_data = vehicle_data.loc[(vehicle_data['tis'] >= start_date) & (vehicle_data['tis'] <= end_date)].copy()
            if(len(vehicle_required_data) > 0):
                node = dict(zip(columns, [None]*len(columns)))
                node['License plate number'] = vehicle_number
                node['Number of Trips Completed'] = unique_vehicle[vehicle_number]
                vehicle_required_data['time_interval'] = vehicle_required_data['tis'] - vehicle_required_data['tis'].shift(1)
                vehicle_required_data['Distance'] = vehicle_required_data.apply(lambda x: -(x['time_interval'] * x['spd']/3600), axis=1)
                distance = round(vehicle_required_data['Distance'].sum(), 3)
                node['Distance'] = distance
                if(distance == 0):
                    continue
                node['Average Speed'] = round(-(distance/vehicle_required_data['time_interval'].loc[vehicle_required_data['spd'] > 0].sum())*3600, 2)
                node['Transporter Name'] = trip_info_required_data.loc[trip_info['vehicle_number'] == vehicle_number].iloc[0]['transporter_name']
                node['Number of Speed Violations'] = len(vehicle_required_data.loc[vehicle_required_data['osf'] & vehicle_required_data['spd'] > 0]) \
                                                     + len(vehicle_required_data.loc[vehicle_required_data['harsh_acceleration']]) \
                                                     + len(vehicle_required_data.loc[vehicle_required_data['hbk']])

                asset_report = asset_report.append(node, ignore_index=True)
                print('Data Recorded for %s' % vehicle_number)


        except Exception as e:
            print(e)

    except Exception:
        print("Data not available for vehicle %s" % (vehicle_number))

print()

path_to_save_report ='Reports/' + str(input('Enter name for report: ')) + '.csv'

asset_report.to_csv(path_to_save_report)

