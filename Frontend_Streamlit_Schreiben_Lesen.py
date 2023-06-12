import streamlit as st
import requests
import mysql.connector
import matplotlib.pyplot as plt
import io
from PIL import Image
#import pandas as pd
#from http import client
#import time


#MY SQL Server-Zugriff und Programmierungen der Temperaturen
def save_temperature(temperature):
    cnx = mysql.connector.connect(user='root', password='qyxZog-totsaj-qidco0',
                                  host='localhost',
                                  database='temperature_data')
    cursor = cnx.cursor()
    query = "INSERT INTO temperatures (value) VALUES (%s)"
    cursor.execute(query, (temperature,))
    cnx.commit()
    cursor.close()
    cnx.close()
    cursor = cnx.cursor()



def get_temperature_data():
    cnx = mysql.connector.connect(user='root', password='qyxZog-totsaj-qidco0',
                                    host='localhost',
                                    database='temperature_data')
    cursor = cnx.cursor()
    query = "SELECT value FROM temperatures"
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    cnx.close()
    temperatures = [row[0] for row in result]
    return temperatures

def update_pid_parameters(kp, ki, kd):
    #Verbindung zur Datenbank herstellen
    cnx = mysql.connector.connect(user='root', password='qyxZog-totsaj-qidco0',
                                   host='localhost',
                                   database='temperature_data')
    cursor = cnx.cursor()
    #Aktualisierung der PID-Parameter in der Datenbank
    update_query = "UPDATE pid_parameters SET kp = %s, ki = %s, kd = %s"
    values = (kp, ki, kd)
    cursor.execute(update_query, values)
    cnx.commit()
    cursor.close()
    cnx.close()

#Programmierung im Streamlit
def main():
    #Anpassung der Farben wie wir uns es vorstellen
    primaryColor = "#E694FF"
    backgroundColor = "#00172B"
    secondaryBackgroundColor = "#0083B8"
    textColor = "#FFFFFF"
    font = "sans-serif"

    #Erstellung des CSS-Stile
    custom_css = f"""
        <style>
        body {{
            background-color: {backgroundColor};
            color: {textColor};
            font-family: {font};
        }}

        .stApp {{
            background-color: {backgroundColor};
            color: {textColor};
        }}

        .stTextInput, .stTextArea, .stNumberInput {{
            background-color: {secondaryBackgroundColor};
            color: {textColor};
        }}

        .stButton, .stButton > button {{
            background-color: {primaryColor};
            color: {backgroundColor};
        }}
        </style>
    """
    
    #Anzeigen des custom_css im Streamlit
    st.markdown(custom_css, unsafe_allow_html=True)
    st.title("Projektarbeit Programmieren 2 \U0001F525")
    st.header("von Stefan, Samir, Fabian")

    #Button zum Starten des Heizvorgangs
    if st.button("Heizung Starten"):
        response = requests.post("http://192.168.10.200:502/start-heating")
        if response.status_code == 200:
            st.write("Heating started successfully.")
        else:
            st.write("Failed to start heating.")

    #Anzeige des PID-Reglers
    st.subheader("PID Regelung")
    kp = st.number_input("kp", value=1.0, step=0.1)
    ki = st.number_input("ki", value=2.0, step=0.1)
    kd = st.number_input("kd", value=0.1, step=0.1)
   
    st.subheader("Veranschaulichung was gesteuert wird")
    image= Image.open("Modbus.PNG")
    st.image(image)
      
    #Abrufen der Temperaturdaten
    temperatures = get_temperature_data()
    
    st.subheader("Diagramm des steigenden Heizwertes")
    #Diagramm anzeigen
    plt.plot(temperatures)
    plt.xlabel("Zeit")
    plt.ylabel("Temperatur")
    st.pyplot(plt)
    #Aktualisierung der PID-Parameter
    update_pid_parameters(kp, ki, kd)

    #Speichern des Diagramms in einem BytesIO-Objekt
    image_stream = io.BytesIO()
    plt.savefig(image_stream, format='png')
    image_stream.seek(0)
    #Anzeigen des Diagramms im Streamlit
    st.image(image_stream)

    if st.button("Löschen der Temperatur-Daten aus der Datenbank"):
        response = requests.post("http://192.168.10.200:502/delete-temperature-data")
        if response.status_code == 200:
            st.write("Temperature data deleted successfully.")
        else:
            st.write("Failed to delete temperature data.")


if __name__ == "__main__":
    main()
