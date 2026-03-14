import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

chemin_csv_2 = " Users/romain/Desktop/STAGE/PYTHON/tracking_SPOTS.csv "
data = pd.read_csv(chemin_csv_2)

data['FRAME'] = pd.to_numeric(data['FRAME'], errors='coerce')
data['TRACK_ID'] = pd.to_numeric(data['TRACK_ID'], errors='coerce')
data['POSITION_X'] = pd.to_numeric(data['POSITION_X'], errors='coerce')
data['POSITION_Y'] = pd.to_numeric(data['POSITION_Y'], errors='coerce')

time_per_frame = 5
angle_threshold = 10
immobile_threshold = 60

def compute_kinematics(df):
    df['dX'] = df['POSITION_X'].diff()
    df['dY'] = df['POSITION_Y'].diff()
    df['distance'] = np.sqrt(df['dX']**2 + df['dY']**2)
    
    dot = df['dX'] * df['dX'].shift(-1) + df['dY'] * df['dY'].shift(-1)
    mags = df['distance'] * df['distance'].shift(-1)
    df['angle'] = np.arccos(np.clip(dot / mags, -1.0, 1.0)) * 180 / np.pi
    return df

data = data.groupby('TRACK_ID', group_keys=False).apply(compute_kinematics)

total_displacements = data.groupby('TRACK_ID')['distance'].sum()
mobile_particles = total_displacements[total_displacements > immobile_threshold].index
filtered_data = data[data['TRACK_ID'].isin(mobile_particles)].copy()

filtered_data['change_of_direction'] = filtered_data['angle'] > angle_threshold

durations = []
change_frames_and_particles = []

for track_id in filtered_data['TRACK_ID'].unique():
    track_data = filtered_data[filtered_data['TRACK_ID'] == track_id]
    change_frames = track_data[track_data['change_of_direction']]['FRAME'].values
    change_times = change_frames * time_per_frame
    
    if len(change_times) > 1:
        durations.extend(np.diff(change_times))
        
    change_frames_and_particles.extend(zip(change_frames, [track_id] * len(change_frames)))

if durations:
    print(f"Duree moyenne de changement de direction : {np.mean(durations):.2f} secondes")
    print(f"Ecart-type : {np.nanstd(durations):.2f} secondes\n")

print("Frames et particules avec changement de direction :")
for frame, particle in change_frames_and_particles:
    print(f"Frame : {frame:.0f}, Particule : {particle:.0f}")

if durations:
    plt.hist(durations, bins=20, edgecolor='black')
    plt.title("Distribution des temps entre changements de direction")
    plt.xlabel("Duree (secondes)")
    plt.ylabel("Frequence")
    plt.show()
