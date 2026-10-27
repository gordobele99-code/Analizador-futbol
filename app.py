import requests
import streamlit as st

st.set_page_config(
    page_title="Analizador Masivo de Fútbol", page_icon="⚽", layout="wide"
)

st.title("⚽ Analizador de Fútbol Automatizado")
st.write(
    "Aplicación conectada a datos abiertos para calcular valor (Value Bet) y"
    " Criterio de Kelly."
)

# Configuración de Banca
banca = st.sidebar.number_input("Tu Banca Total ($)", value=100, step=10)

API_KEY = st.sidebar.text_input(
    "API Key de Football-Data.org (Opcional)", type="password"
)


@st.cache_data(ttl=3600)
def obtener_partidos(api_key):
  url = "https://api.football-data.org/v4/matches?status=SCHEDULED"
  headers = {"X-Auth-Token": api_key} if api_key else {}
  try:
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
      return response.json().get("matches", [])
    else:
      return []
  except:
    return []


partidos = obtener_partidos(API_KEY)

if partidos:
  st.success(
      f"¡Se cargaron {len(partidos)} partidos próximos automáticamente!"
  )

  for p in partidos[:15]:
    home = p["homeTeam"]["name"]
    away = p["awayTeam"]["name"]
    competition = p["competition"]["name"]
    fecha = p["utcDate"]

    with st.expander(f"{competition}: {home} vs {away} ({fecha[:10]})"):
      col1, col2 = st.columns(2)

      with col1:
        st.subheader("Cuotas del Mercado (1X2)")
        cuota_local = st.number_input(
            f"Cuota Local ({home})",
            min_value=1.01,
            value=2.00,
            key=f"h_{p['id']}",
        )
        cuota_empate = st.number_input(
            "Cuota Empate", min_value=1.01, value=3.40, key=f"d_{p['id']}"
        )
        cuota_visitante = st.number_input(
            f"Cuota Visitante ({away})",
            min_value=1.01,
            value=3.50,
            key=f"a_{p['id']}",
        )

      with col2:
        st.subheader("Análisis de Valor y Kelly")
        prob_aprox_local = 1 / cuota_local
        st.write(
            f"Probabilidad implícita local: {prob_aprox_local*100:.1f}%"
        )

        cuota_elegida = st.selectbox(
            "Selecciona tu apuesta",
            ["Local", "Empate", "Visitante"],
            key=f"sel_{p['id']}",
        )
        cuota_seleccion = (
            cuota_local
            if cuota_elegida == "Local"
            else (cuota_empate if cuota_elegida == "Empate" else cuota_visitante)
        )

        prob_estimada = st.slider(
            "Tu probabilidad estimada (%)",
            1,
            100,
            int(prob_aprox_local * 100),
            key=f"prob_{p['id']}",
        )
        p_dec = prob_estimada / 100.0

        b_val = cuota_seleccion - 1
        if b_val > 0:
          kelly_full = (p_dec * cuota_seleccion - 1) / b_val
          kelly_sugerido = max(0.0, kelly_full * 0.25)
          monto_apuesta = banca * kelly_sugerido

          st.metric(
              label="Apuesta Sugerida (Criterio de Kelly 25%)",
              value=f"${monto_apuesta:.2f}",
              delta=f"{kelly_sugerido*100:.1f}% de la banca",
          )
        else:
          st.warning("La cuota debe ser mayor a 1.00")
else:
  st.info(
      "Para ver partidos automáticos, recuerda configurar tu API Key o usa las"
      " opciones disponibles."
          )
  
