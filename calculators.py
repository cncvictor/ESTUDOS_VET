import streamlit as st
import math

class AnesthesiaCalculator:
    @staticmethod
    def calcular_dose_medicamento(peso, dose_mg_kg, concentracao_mg_ml):
        """Calcula o volume em ml baseado no peso e dose desejada"""
        volume_ml = (peso * dose_mg_kg) / concentracao_mg_ml
        return round(volume_ml, 2)
    
    @staticmethod
    def calcular_taxa_infusao(peso, taxa_ml_kg_h):
        """Calcula a taxa de infusão em ml/h"""
        return round(peso * taxa_ml_kg_h, 2)
    
    @staticmethod
    def calcular_volume_sangue(peso, especie):
        """Calcula o volume sanguíneo estimado"""
        volumes = {
            'canino': 0.09,  # 9% do peso corporal
            'felino': 0.07,  # 7% do peso corporal
            'equino': 0.08,  # 8% do peso corporal
            'bovino': 0.07   # 7% do peso corporal
        }
        return round(peso * volumes.get(especie, 0.08) * 1000, 0)  # retorna em ml
    
    @staticmethod
    def calcular_perdas_permitidas(volume_sangue, hematocrito_atual, hematocrito_minimo):
        """Calcula o volume de sangue que pode ser perdido até atingir o hematócrito mínimo"""
        return round(volume_sangue * (1 - (hematocrito_minimo / hematocrito_atual)), 0)
    
    @staticmethod
    def calcular_fluidoterapia(peso, taxa_ml_kg_h, duracao_h):
        """Calcula o volume total de fluidos para um período"""
        return round(peso * taxa_ml_kg_h * duracao_h, 0)
    
    @staticmethod
    def calcular_deficit_hidrico(peso, percentual_desidratacao):
        """Calcula o déficit hídrico baseado no percentual de desidratação"""
        return round(peso * percentual_desidratacao * 10, 0)  # retorna em ml

def render_calculator_interface():
    st.header("🧮 Calculadoras Anestésicas")
    
    calc = AnesthesiaCalculator()
    
    calculator_type = st.selectbox(
        "Selecione a Calculadora",
        ["Dose de Medicamento", "Taxa de Infusão", "Volume Sanguíneo", 
         "Perdas Permitidas", "Fluidoterapia", "Déficit Hídrico"]
    )
    
    if calculator_type == "Dose de Medicamento":
        peso = st.number_input("Peso (kg)", min_value=0.1, value=10.0)
        dose = st.number_input("Dose (mg/kg)", min_value=0.01, value=1.0)
        conc = st.number_input("Concentração (mg/ml)", min_value=0.1, value=10.0)
        
        if st.button("Calcular"):
            resultado = calc.calcular_dose_medicamento(peso, dose, conc)
            st.success(f"Volume a ser administrado: {resultado} ml")
    
    elif calculator_type == "Taxa de Infusão":
        peso = st.number_input("Peso (kg)", min_value=0.1, value=10.0)
        taxa = st.number_input("Taxa (ml/kg/h)", min_value=0.1, value=2.0)
        
        if st.button("Calcular"):
            resultado = calc.calcular_taxa_infusao(peso, taxa)
            st.success(f"Taxa de infusão: {resultado} ml/h")
    
    elif calculator_type == "Volume Sanguíneo":
        peso = st.number_input("Peso (kg)", min_value=0.1, value=10.0)
        especie = st.selectbox(
            "Espécie",
            ["canino", "felino", "equino", "bovino"]
        )
        
        if st.button("Calcular"):
            resultado = calc.calcular_volume_sangue(peso, especie)
            st.success(f"Volume sanguíneo estimado: {resultado} ml")
    
    elif calculator_type == "Perdas Permitidas":
        volume_sangue = st.number_input("Volume sanguíneo (ml)", min_value=1.0, value=1000.0)
        ht_atual = st.number_input("Hematócrito atual (%)", min_value=1.0, max_value=100.0, value=45.0)
        ht_minimo = st.number_input("Hematócrito mínimo desejado (%)", min_value=1.0, max_value=100.0, value=25.0)
        
        if st.button("Calcular"):
            resultado = calc.calcular_perdas_permitidas(volume_sangue, ht_atual, ht_minimo)
            st.success(f"Volume de perdas permitidas: {resultado} ml")
    
    elif calculator_type == "Fluidoterapia":
        peso = st.number_input("Peso (kg)", min_value=0.1, value=10.0)
        taxa = st.number_input("Taxa (ml/kg/h)", min_value=0.1, value=2.0)
        duracao = st.number_input("Duração (horas)", min_value=1, value=24)
        
        if st.button("Calcular"):
            resultado = calc.calcular_fluidoterapia(peso, taxa, duracao)
            st.success(f"Volume total de fluidos: {resultado} ml")
    
    elif calculator_type == "Déficit Hídrico":
        peso = st.number_input("Peso (kg)", min_value=0.1, value=10.0)
        desidratacao = st.number_input("Percentual de desidratação (%)", min_value=0.1, max_value=15.0, value=5.0)
        
        if st.button("Calcular"):
            resultado = calc.calcular_deficit_hidrico(peso, desidratacao/100)
            st.success(f"Déficit hídrico: {resultado} ml") 