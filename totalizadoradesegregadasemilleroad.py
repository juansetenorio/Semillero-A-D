import pandas as pd
from datetime import datetime

# Valores característicos de los dispositivos
device_values = {
    'Refrigerator': 138.528090,
    'Clothes washer': 149.506370,
    'Clothes Iron': 843.043542,
    'Computer': 37.390654,
    'Oven': 1395.031694,
    'Play': 31.116667,
    'TV': 63.912018,
    'Sound system': 32.735294
}

# Nuevas combinaciones para cada cuarto del día (solo los primeros 10)
top_combinations_extended = {
    '0-6 am': [('Sound system',), ('Refrigerator',), ('Refrigerator', 'Sound system'), ('TV',), ('Refrigerator', 'TV'),
               ('TV', 'Sound system'), ('Computer',), ('Refrigerator', 'TV', 'Sound system'), ('Computer', 'Sound system'),
               ('Refrigerator', 'Computer')],
    '6 am-12 pm': [('Refrigerator',), ('Sound system',), ('TV',), ('Refrigerator', 'Sound system'), ('Clothes washer',),
                   ('Refrigerator', 'TV'), ('Computer',), ('TV', 'Sound system'), ('Refrigerator', 'Clothes washer'),
                   ('Clothes washer', 'Sound system')],
    '12 pm-6 pm': [('Refrigerator',), ('Sound system',), ('Refrigerator', 'Sound system'), ('TV',), ('Clothes washer',),
                   ('Refrigerator', 'TV'), ('Computer',), ('TV', 'Sound system'), ('Refrigerator', 'Clothes washer'),
                   ('Clothes washer', 'Sound system')],
    '6 pm-12 am': [('Refrigerator',), ('TV',), ('Sound system',), ('Refrigerator', 'TV'), ('Refrigerator', 'Sound system'),
                   ('TV', 'Sound system'), ('Refrigerator', 'TV', 'Sound system'), ('Play',), ('Computer',), ('Play', 'TV')]
}

def get_time_of_day(time_str):
    time = datetime.strptime(time_str, '%m/%d/%Y %H:%M').time()
    if 0 <= time.hour < 6:
        return "0-6 am"
    elif 6 <= time.hour < 12:
        return "6 am-12 pm"
    elif 12 <= time.hour < 18:
        return "12 pm-6 pm"
    else:
        return "6 pm-12 am"

def process_data(file_path, start_row, end_row):
    df = pd.read_csv(file_path)
    df['Time of Day'] = df['Fecha'].apply(get_time_of_day)
    results = []

    for index, row in df.iterrows():
        if index < start_row or index >= end_row:
            continue
        medidor_value = row['Medidor [W]']
        time_of_day = row['Time of Day']
        #Analizando, debajo de un rango se considera que los dispositivos estudiados tienen potencia minima o 0.
        if medidor_value < 135:
            for device in device_values:
                row[device] = 0
        else:
            #Potencia minima suministrada  por los demas dispositivos, constante
            medidor_value -= 102.23
            closest_combination = None
            closest_diff = float('inf')
            second_closest_combination = None
            second_closest_diff = float('inf')
            for combination in top_combinations_extended[time_of_day]:
                sum_values = sum(device_values[dev] for dev in combination)
                diff = abs(medidor_value - sum_values)
                if diff < closest_diff:
                    second_closest_combination = closest_combination
                    second_closest_diff = closest_diff
                    closest_diff = diff
                    closest_combination = combination
                elif diff < second_closest_diff:
                    second_closest_combination = combination
                    second_closest_diff = diff
            for device in device_values:
                if device in closest_combination:
                    row[device] = device_values[device]
                else:
                    row[device] = 0
        results.append(row)

    # Crear un nuevo DataFrame con los resultados
    new_df = pd.DataFrame(results)
    return new_df

# Ruta del archivo que se va a suministrar. 60 primeros datos. 
file_path = 'consumo_casa.csv'
start_row = 0
end_row = 60

new_df = process_data(file_path, start_row, end_row)

# Matriz de energia desegregada
new_df.to_csv('resultados_ajustados.csv', index=False)
# Segunda matriz,  uso de cargas
new_df_binary = new_df.replace({val: 1.0 for val in device_values.values()}, regex=True)
new_df_binary.to_csv('resultados_ajustados_binario.csv', index=False)

