import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree

vitesses_trackmate = '/Users/romain/Desktop/STAGE/PYTHON/vitesse_chlamy.csv'
data = pd.read_csv(vitesses_trackmate)

min_area = 30
max_area = 300

# Filtrer les particules par taille
df1 = data[data['Area'] > min_area]
df = df1[df1['Area'] < max_area]

# Trier les donnees par Slice pour faciliter le traitement
df = df.sort_values(by='Slice').reset_index(drop=True)

# Initialisation des listes pour les resultats
tracked_particles = []

def create_kdtree(data):
    return cKDTree(data[['XM', 'YM']].values)

def calculate_angle(v1, v2):
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
    cosine_angle = dot_product / (norm_v1 * norm_v2)
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0)) # eviter erreurs num
    return np.degrees(angle)

def associate_particles(df):
    unique_slices = df['Slice'].unique()
    prev_positions = None
    prev_slice = None
    for slice_num in unique_slices:
        current_data = df[df['Slice'] == slice_num]
        if prev_positions is not None:
            tree = create_kdtree(current_data)
            for i, prev_row in prev_positions.iterrows():
                pos = np.array([prev_row['XM'], prev_row['YM']])
                dist, idx = tree.query(pos)
                if dist < 10: # seuil de proximite en pixels
                    current_row = current_data.iloc[idx]
                    if prev_slice is not None:
                        prev_vector = np.array([prev_row['XM'] - prev_positions['XM'].mean(),
                                                prev_row['YM'] - prev_positions['YM'].mean()])
                        current_vector = np.array([current_row['XM'] - prev_row['XM'],
                                                   current_row['YM'] - prev_row['YM']])
                        
                        angle = calculate_angle(prev_vector, current_vector)
                        
                        if angle < 2 or angle > 178:
                            tracked_particles.append({
                                'Prev_Slice': prev_slice,
                                'Current_Slice': slice_num,
                                'Prev_XM': prev_row['XM'],
                                'Prev_YM': prev_row['YM'],
                                'Current_XM': current_row['XM'],
                                'Current_YM': current_row['YM'],
                                'Area': prev_row['Area']
                            })
        prev_positions = current_data
        prev_slice = slice_num

associate_particles(df)

particles_df = pd.DataFrame(tracked_particles)

if not particles_df.empty:
    # Calculer les distances parcourues en pixels
    particles_df['Distance'] = np.sqrt((particles_df['Current_XM'] - particles_df['Prev_XM'])**2 + 
                                       (particles_df['Current_YM'] - particles_df['Prev_YM'])**2)

    # Estimer la taille moyenne d'une particule (moyenne sur les Area)
    mean_area = df['Area'].mean()
    particle_diameter_pixels = np.sqrt(mean_area / np.pi) * 2
    conversion_factor = 10 / particle_diameter_pixels # 10 um cell diameter

    # Convertir les distances en micrometres
    particles_df['Distance_micrometers'] = particles_df['Distance'] * conversion_factor

    # Calculer la vitesse
    time_interval_seconds = 0.05 # 0.05 secondes entre chaque image
    particles_df['Speed_micrometers_per_second'] = particles_df['Distance_micrometers'] / time_interval_seconds

    # Filtrer les particules dont le deplacement total est inferieur a 3 micrometres
    total_displacements = particles_df.groupby(['Prev_XM', 'Prev_YM', 'Current_XM', 'Current_YM'])['Distance_micrometers'].sum()
    valid_particles = total_displacements[total_displacements >= 3].index
    particles_df = particles_df[particles_df[['Prev_XM', 'Prev_YM', 'Current_XM', 'Current_YM']].apply(tuple, axis=1).isin(valid_particles)]

    # Vitesse moyenne
    mean_speed = particles_df['Speed_micrometers_per_second'].mean()
    print(f"Vitesse moyenne des particules : {mean_speed:.2f} micrometres par seconde")

    # Histogramme des valeurs de vitesse
    plt.hist(particles_df['Speed_micrometers_per_second'], bins=30, edgecolor='black')
    plt.xlabel('Vitesse (micrometres/seconde)')
    plt.ylabel('Frequence')
    plt.title('Distribution des vitesses des particules')
    plt.show()
else:
    print("Aucune particule trackee avec ces criteres.")
