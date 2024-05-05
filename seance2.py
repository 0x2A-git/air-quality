import pandas as pd
import matplotlib.pyplot as plt
import numpy as np 

xlsx_path = 'datasource/activites.xlsx'
db_path = 'tache2/db_full.csv'
# Lecture de la base de données CSV dans un DataFrame pandas
base = pd.read_csv(db_path, sep=',')
# Conversion de la colonne 'Time' en datetime et configuration du fuseau horaire sur UTC+01:00
base['Time'] = pd.to_datetime(base['Time']).dt.tz_convert('UTC+01:00')
# Affichage des types de données du DataFrame
print(base.dtypes)
# Segmentation du DataFrame
# DF segmentation
print("Reading excel file...")
# Lecture du fichier activities dans un DataFrame
df_excel = pd.read_excel(xlsx_path, sheet_name='Done so far')
print("Done reading excel file !")

# Suppression des colonnes inutiles 
print("Dropping columns from Excel sheet...")
df_excel = df_excel.drop(columns=df_excel.columns[df_excel.columns.str.contains('^Unnamed|Comments')], errors="ignored")
print("Done dropping columns from Excel sheet !")
print(df_excel.dtypes)
# Conversion des dates en datetime et configuration du fuseau horaire
print("Converting Excel sheet dates...")
df_excel['Started'] = pd.to_datetime(df_excel['Started']).dt.tz_localize('UTC').dt.tz_convert('UTC+01:00')
df_excel['Ended'] = pd.to_datetime(df_excel['Ended']).dt.tz_localize('UTC').dt.tz_convert('UTC+01:00')
print("Done converting Excel sheet dates !")
# Suppression des lignes avec des valeurs manquantes 
print("Dropping N/A from Excel...")
df_excel = df_excel.dropna().reset_index(drop=True)
print("Done dropping N/A from Excel !")
# Affichage du DataFrame Excel nettoyé
print(df_excel)

labelled_dataset = pd.DataFrame()
instances = {}
# Dictionnaire pour mapper les étiquettes d'activité
labels= {'Saber': 1,'Aera': 2, 'Nett': 3, 'Asp': 4, 'AS1': 5, 'Bougie': 6, 'SdB': 7, 'BricoP': 8, 'BricoC': 9, 'Oeuf':10}

for idact, act in enumerate(df_excel['activity']):
    start = df_excel['Started'][idact]# Heure de début de l'activité
    end = df_excel['Ended'][idact]# Heure de fin de l'activité
    # Extraction des instances de la base de données en fonction des heures de début et de fin
    new_instance = base[(base['Time'] >= start) & (base['Time'] <= end)].reset_index(drop=True).sort_values(by='Time').drop(columns='Time')
    # Attribution de l'étiquette aux instances
    new_instance['label'] = labels[act]*np.ones(len(new_instance))
    # Concaténation des instances au jeu de données étiqueté
    labelled_dataset = pd.concat([labelled_dataset,new_instance],ignore_index=True)
    # Stockage des instances dans un dictionnaire
    if not act in instances:
        instances[act] = [new_instance]
    else :
        instances[act].append(new_instance)

# Enregistrement du jeu de données étiqueté sur le disque sous forme de CSV
print("Saving labels to disk...")
labelled_dataset.to_csv('tache3/labels.csv', index = False, sep = ';')
print("Done saving labels to disk !")

def averageSignature(instances):
    """
    Calcul de la signature moyenne des instances.

    Parameters:
    instances (dict): Un dictionnaire contenant des instances de données pour chaque activité.

    Returns:
    pandas.DataFrame: Le DataFrame contenant la signature moyenne des instances.
    """
    df_avg = pd.DataFrame(instances[0])# Initialisation du DataFrame avec la première instance
    df_avg = df_avg.drop('label', axis=1)# Suppression de la colonne d'étiquette
    for i in range(1, len(instances)): 

        current_instance = instances[i] 
        current_instance = current_instance.drop('label', axis=1)

        min_rows = min(current_instance.shape[0], df_avg.shape[0])

        for row in range(min_rows):
            avg_row = df_avg.iloc[row]
            current_avg_row = current_instance.iloc[row]

            df_avg.iloc[row] = (avg_row + current_avg_row) / 2
    print(df_avg)

    df_avg = df_avg.dropna()

    return df_avg

# Plotting the average signature for AS1
fig = plt.figure(figsize=(10, 6))

i = 0

# Traçage de la signature moyenne pour chaque activité
for activity in instances.keys():
    i+= 1
    plt.subplot(5,2,i)
    avg = averageSignature(instances[activity])
    for column in avg.columns:
        plt.plot(avg.index, avg[column])


    plt.title(f'Average signature of {activity}')
    plt.xlabel('Number of Samples')
    plt.ylabel('Sensor Measurements')

fig.tight_layout()
plt.show()
